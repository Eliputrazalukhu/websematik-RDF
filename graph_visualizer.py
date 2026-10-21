"""
Graph Visualizer Module
Handles visualization of RDF graphs using NetworkX and interactive plotting
"""
import networkx as nx
import plotly.graph_objects as go
from rdflib import Graph, URIRef, Literal
from typing import Dict, List, Tuple, Optional
import streamlit as st

# Optional dependency - streamlit-agraph
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    AGRAPH_AVAILABLE = True
except ImportError:
    AGRAPH_AVAILABLE = False
    # Create dummy classes for type hints
    Node = None
    Edge = None
    Config = None


class GraphVisualizer:
    """Class to visualize RDF graphs"""
    
    def __init__(self, rdf_graph: Graph):
        self.rdf_graph = rdf_graph
        self.nx_graph = nx.MultiDiGraph()
        self._build_networkx_graph()
    
    def _build_networkx_graph(self):
        """Convert RDF graph to NetworkX graph"""
        self.nx_graph.clear()
        
        for s, p, o in self.rdf_graph:
            subject = self._shorten_uri(str(s))
            predicate = self._shorten_uri(str(p))
            obj = self._shorten_uri(str(o))
            
            # Add nodes
            self.nx_graph.add_node(subject, uri=str(s), node_type='subject')
            
            if isinstance(o, URIRef):
                self.nx_graph.add_node(obj, uri=str(o), node_type='uri')
            else:
                self.nx_graph.add_node(obj, uri=str(o), node_type='literal')
            
            # Add edge
            self.nx_graph.add_edge(subject, obj, label=predicate, uri=str(p))
    
    def _shorten_uri(self, uri: str, max_length: int = 50) -> str:
        """Shorten URI for display"""
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            parts = uri.split('/')
            return parts[-1] if parts[-1] else parts[-2]
        elif len(uri) > max_length:
            return uri[:max_length] + '...'
        return uri
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the graph"""
        return {
            'Nodes': self.nx_graph.number_of_nodes(),
            'Edges': self.nx_graph.number_of_edges(),
            'Density': nx.density(self.nx_graph),
            'Is Connected': nx.is_weakly_connected(self.nx_graph) if self.nx_graph.number_of_nodes() > 0 else False
        }
    
    def visualize_with_plotly(self, max_nodes: int = 100) -> go.Figure:
        """
        Create interactive Plotly visualization
        
        Args:
            max_nodes: Maximum number of nodes to display
        
        Returns:
            Plotly figure
        """
        if self.nx_graph.number_of_nodes() == 0:
            fig = go.Figure()
            fig.add_annotation(text="No data to visualize", 
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Limit nodes for performance
        if self.nx_graph.number_of_nodes() > max_nodes:
            # Get subgraph with most connected nodes
            nodes_by_degree = sorted(self.nx_graph.degree, key=lambda x: x[1], reverse=True)
            top_nodes = [n for n, d in nodes_by_degree[:max_nodes]]
            G = self.nx_graph.subgraph(top_nodes)
        else:
            G = self.nx_graph
        
        # Use spring layout for positioning
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color='#888'),
                hoverinfo='text',
                text=edge[2].get('label', ''),
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes(data=True):
            x, y = pos[node[0]]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node[0])
            
            # Color by node type
            node_type = node[1].get('node_type', 'unknown')
            if node_type == 'literal':
                node_color.append('lightblue')
            elif node_type == 'subject':
                node_color.append('lightcoral')
            else:
                node_color.append('lightgreen')
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='top center',
            hoverinfo='text',
            marker=dict(
                size=15,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title='RDF Graph Visualization',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=700
        )
        
        return fig
    
    def visualize_with_agraph(self, max_nodes: int = 50) -> Tuple[List, List, Optional[object]]:
        """
        Create interactive visualization using streamlit-agraph
        
        Args:
            max_nodes: Maximum number of nodes to display
        
        Returns:
            Tuple of (nodes, edges, config) or ([], [], None) if streamlit-agraph not available
        """
        if not AGRAPH_AVAILABLE:
            import warnings
            warnings.warn("streamlit-agraph is not installed. Install it with: pip install streamlit-agraph")
            return [], [], None
        
        nodes = []
        edges = []
        node_set = set()
        
        # Limit for performance
        edge_count = 0
        max_edges = max_nodes * 3
        
        for s, p, o in self.rdf_graph:
            if edge_count >= max_edges:
                break
            
            subject = self._shorten_uri(str(s))
            predicate = self._shorten_uri(str(p))
            obj = self._shorten_uri(str(o))
            
            # Add subject node
            if subject not in node_set:
                nodes.append(Node(
                    id=subject,
                    label=subject,
                    size=25,
                    color='#FF6B6B'
                ))
                node_set.add(subject)
            
            # Add object node
            if obj not in node_set:
                if isinstance(o, Literal):
                    color = '#4ECDC4'
                else:
                    color = '#95E1D3'
                
                nodes.append(Node(
                    id=obj,
                    label=obj,
                    size=20,
                    color=color
                ))
                node_set.add(obj)
            
            # Add edge
            edges.append(Edge(
                source=subject,
                target=obj,
                label=predicate,
                type='CURVE_SMOOTH'
            ))
            
            edge_count += 1
        
        config = Config(
            width='100%',
            height=600,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#F7A7A6",
            collapsible=True,
            node={'labelProperty': 'label'},
            link={'labelProperty': 'label', 'renderLabel': True}
        )
        
        return nodes, edges, config
    
    def get_central_nodes(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get most central nodes using degree centrality
        
        Args:
            top_n: Number of top nodes to return
        
        Returns:
            List of (node, centrality_score) tuples
        """
        if self.nx_graph.number_of_nodes() == 0:
            return []
        
        centrality = nx.degree_centrality(self.nx_graph)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_n]
    
    def find_paths(self, source: str, target: str, max_length: int = 5) -> List[List[str]]:
        """
        Find paths between two nodes
        
        Args:
            source: Source node URI
            target: Target node URI
            max_length: Maximum path length
        
        Returns:
            List of paths
        """
        try:
            source_short = self._shorten_uri(source)
            target_short = self._shorten_uri(target)
            
            if source_short in self.nx_graph and target_short in self.nx_graph:
                paths = nx.all_simple_paths(self.nx_graph, source_short, target_short, cutoff=max_length)
                return [list(path) for path in paths]
            return []
        except:
            return []

