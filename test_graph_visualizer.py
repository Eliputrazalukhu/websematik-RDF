"""
Unit tests for graph_visualizer module
"""
import pytest
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL
from graph_visualizer import GraphVisualizer, AGRAPH_AVAILABLE
import networkx as nx


class TestGraphVisualizer:
    """Test cases for GraphVisualizer class"""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample RDF graph"""
        g = Graph()
        ex = "http://example.org/"
        
        # Add triples
        g.add((URIRef(ex + "Person"), RDF.type, OWL.Class))
        g.add((URIRef(ex + "Person"), RDFS.label, Literal("Person")))
        g.add((URIRef(ex + "John"), RDF.type, URIRef(ex + "Person")))
        g.add((URIRef(ex + "John"), RDFS.label, Literal("John Smith")))
        g.add((URIRef(ex + "Jane"), RDF.type, URIRef(ex + "Person")))
        g.add((URIRef(ex + "Jane"), RDFS.label, Literal("Jane Doe")))
        g.add((URIRef(ex + "John"), URIRef(ex + "knows"), URIRef(ex + "Jane")))
        
        return g
    
    @pytest.fixture
    def visualizer(self, sample_graph):
        """Create a GraphVisualizer instance"""
        return GraphVisualizer(sample_graph)
    
    def test_initialization(self, visualizer):
        """Test GraphVisualizer initialization"""
        assert isinstance(visualizer.rdf_graph, Graph)
        assert isinstance(visualizer.nx_graph, nx.MultiDiGraph)
        assert visualizer.nx_graph.number_of_nodes() > 0
    
    def test_build_networkx_graph(self, visualizer):
        """Test NetworkX graph construction"""
        assert visualizer.nx_graph.number_of_nodes() > 0
        assert visualizer.nx_graph.number_of_edges() > 0
    
    def test_shorten_uri(self, visualizer):
        """Test URI shortening"""
        uri1 = "http://example.org/Person"
        shortened1 = visualizer._shorten_uri(uri1)
        assert shortened1 == "Person"
        
        uri2 = "http://www.w3.org/2000/01/rdf-schema#label"
        shortened2 = visualizer._shorten_uri(uri2)
        assert shortened2 == "label"
        
        long_uri = "x" * 100
        shortened3 = visualizer._shorten_uri(long_uri, max_length=50)
        assert len(shortened3) <= 53  # 50 + "..."
    
    def test_get_graph_stats(self, visualizer):
        """Test graph statistics"""
        stats = visualizer.get_graph_stats()
        
        assert 'Nodes' in stats
        assert 'Edges' in stats
        assert 'Density' in stats
        assert 'Is Connected' in stats
        
        assert stats['Nodes'] > 0
        assert stats['Edges'] > 0
        assert isinstance(stats['Density'], float)
        assert isinstance(stats['Is Connected'], bool)
    
    def test_visualize_with_plotly(self, visualizer):
        """Test Plotly visualization"""
        fig = visualizer.visualize_with_plotly(max_nodes=10)
        
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
    
    def test_visualize_empty_graph(self):
        """Test visualization with empty graph"""
        empty_graph = Graph()
        viz = GraphVisualizer(empty_graph)
        
        fig = viz.visualize_with_plotly()
        assert fig is not None
    
    def test_visualize_with_node_limit(self, visualizer):
        """Test visualization with node limit"""
        # Create a larger graph
        g = Graph()
        for i in range(150):
            g.add((
                URIRef(f"http://example.org/node{i}"),
                URIRef(f"http://example.org/connects"),
                URIRef(f"http://example.org/node{i+1}")
            ))
        
        viz = GraphVisualizer(g)
        fig = viz.visualize_with_plotly(max_nodes=50)
        
        assert fig is not None
        # Should have limited the nodes
    
    @pytest.mark.skipif(not AGRAPH_AVAILABLE, reason="streamlit-agraph not installed")
    def test_visualize_with_agraph(self, visualizer):
        """Test agraph visualization"""
        nodes, edges, config = visualizer.visualize_with_agraph(max_nodes=10)
        
        assert isinstance(nodes, list)
        assert isinstance(edges, list)
        assert config is not None
        
        assert len(nodes) > 0
        assert len(edges) > 0
    
    def test_visualize_with_agraph_not_available(self, visualizer):
        """Test agraph visualization when package not available"""
        if not AGRAPH_AVAILABLE:
            nodes, edges, config = visualizer.visualize_with_agraph(max_nodes=10)
            assert nodes == []
            assert edges == []
            assert config is None
    
    def test_get_central_nodes(self, visualizer):
        """Test centrality calculation"""
        central_nodes = visualizer.get_central_nodes(top_n=5)
        
        assert isinstance(central_nodes, list)
        assert len(central_nodes) > 0
        
        # Check format: list of tuples (node, centrality)
        for node, centrality in central_nodes:
            assert isinstance(node, str)
            assert isinstance(centrality, (int, float))
            assert 0 <= centrality <= 1
    
    def test_get_central_nodes_empty_graph(self):
        """Test centrality on empty graph"""
        empty_graph = Graph()
        viz = GraphVisualizer(empty_graph)
        
        central_nodes = viz.get_central_nodes()
        assert central_nodes == []
    
    def test_find_paths(self, visualizer):
        """Test path finding"""
        # This might not work if nodes aren't connected
        # Just test that it doesn't crash
        paths = visualizer.find_paths(
            "http://example.org/John",
            "http://example.org/Jane",
            max_length=3
        )
        
        assert isinstance(paths, list)
    
    def test_find_paths_no_connection(self, visualizer):
        """Test path finding with no connection"""
        paths = visualizer.find_paths(
            "http://example.org/NonExistent1",
            "http://example.org/NonExistent2"
        )
        
        assert paths == []
    
    def test_node_types(self, sample_graph):
        """Test different node types are handled"""
        # Add different types
        ex = "http://example.org/"
        sample_graph.add((URIRef(ex + "Test"), URIRef(ex + "prop"), Literal("literal value")))
        
        viz = GraphVisualizer(sample_graph)
        
        # Check that both URI and literal nodes exist
        has_literal = False
        has_uri = False
        
        for node, data in viz.nx_graph.nodes(data=True):
            node_type = data.get('node_type')
            if node_type == 'literal':
                has_literal = True
            elif node_type in ['subject', 'uri']:
                has_uri = True
        
        assert has_uri  # Should have at least URI nodes
    
    def test_edge_labels(self, visualizer):
        """Test that edges have labels"""
        has_labels = False
        
        for u, v, data in visualizer.nx_graph.edges(data=True):
            if 'label' in data:
                has_labels = True
                break
        
        assert has_labels
    
    def test_large_graph_performance(self):
        """Test with larger graph"""
        g = Graph()
        
        # Create a graph with 500 triples
        for i in range(500):
            g.add((
                URIRef(f"http://example.org/subject{i}"),
                URIRef(f"http://example.org/predicate{i % 10}"),
                Literal(f"Object {i}")
            ))
        
        viz = GraphVisualizer(g)
        
        # Should handle without crashing
        stats = viz.get_graph_stats()
        assert stats['Nodes'] > 0
        
        # Visualization with limit
        fig = viz.visualize_with_plotly(max_nodes=100)
        assert fig is not None


class TestGraphVisualizerEdgeCases:
    """Test edge cases"""
    
    def test_circular_references(self):
        """Test graph with circular references"""
        g = Graph()
        ex = "http://example.org/"
        
        g.add((URIRef(ex + "A"), URIRef(ex + "knows"), URIRef(ex + "B")))
        g.add((URIRef(ex + "B"), URIRef(ex + "knows"), URIRef(ex + "C")))
        g.add((URIRef(ex + "C"), URIRef(ex + "knows"), URIRef(ex + "A")))
        
        viz = GraphVisualizer(g)
        stats = viz.get_graph_stats()
        
        assert stats['Nodes'] == 3
        assert stats['Edges'] == 3
    
    def test_self_loops(self):
        """Test graph with self-loops"""
        g = Graph()
        ex = "http://example.org/"
        
        g.add((URIRef(ex + "A"), URIRef(ex + "knows"), URIRef(ex + "A")))
        
        viz = GraphVisualizer(g)
        stats = viz.get_graph_stats()
        
        assert stats['Nodes'] >= 1
    
    def test_disconnected_components(self):
        """Test graph with disconnected components"""
        g = Graph()
        ex = "http://example.org/"
        
        # Component 1
        g.add((URIRef(ex + "A"), URIRef(ex + "knows"), URIRef(ex + "B")))
        
        # Component 2 (disconnected)
        g.add((URIRef(ex + "X"), URIRef(ex + "knows"), URIRef(ex + "Y")))
        
        viz = GraphVisualizer(g)
        stats = viz.get_graph_stats()
        
        assert stats['Is Connected'] == False
    
    def test_special_characters_in_uris(self):
        """Test URIs with special characters"""
        g = Graph()
        
        g.add((
            URIRef("http://example.org/node-with-dash"),
            URIRef("http://example.org/has_underscore"),
            URIRef("http://example.org/has.dot")
        ))
        
        viz = GraphVisualizer(g)
        # In NetworkX graph: subject and object are nodes, predicate is edge label
        # So we expect 2 nodes (subject and object)
        assert viz.nx_graph.number_of_nodes() == 2
        assert viz.nx_graph.number_of_edges() == 1
        
        # Verify special characters are handled in node names
        nodes = list(viz.nx_graph.nodes())
        assert any('-' in node or '.' in node for node in nodes)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

