"""
Integration tests for RDF/OWL Visualizer
Tests interactions between modules
"""
import pytest
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL
from rdf_reader import RDFReader
from graph_visualizer import GraphVisualizer
from rdf_converter import RDFConverter, RDFAnnotator
import pandas as pd


class TestWorkflowIntegration:
    """Test complete workflows"""
    
    @pytest.fixture
    def sample_rdf_turtle(self):
        """Sample Turtle RDF data"""
        return """
        @prefix ex: <http://example.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        
        ex:Organization a owl:Class ;
            rdfs:label "Organization"@en ;
            rdfs:comment "A social or legal entity"@en .
        
        ex:Person a owl:Class ;
            rdfs:label "Person"@en ;
            rdfs:comment "A human being"@en .
        
        ex:worksFor a owl:ObjectProperty ;
            rdfs:label "works for"@en ;
            rdfs:domain ex:Person ;
            rdfs:range ex:Organization .
        
        ex:hasName a owl:DatatypeProperty ;
            rdfs:label "has name"@en ;
            rdfs:domain ex:Person .
        
        ex:TechCorp a ex:Organization ;
            ex:hasName "TechCorp Inc." .
        
        ex:John a ex:Person ;
            ex:hasName "John Smith" ;
            ex:worksFor ex:TechCorp .
        
        ex:Jane a ex:Person ;
            ex:hasName "Jane Doe" ;
            ex:worksFor ex:TechCorp .
        """
    
    def test_load_and_visualize(self, sample_rdf_turtle):
        """Test loading RDF and visualizing it"""
        # Load
        reader = RDFReader()
        result = reader.load_from_file(sample_rdf_turtle.encode('utf-8'), 'Turtle')
        assert result is True
        
        # Get stats
        stats = reader.get_stats()
        assert stats['Total Triples'] > 0
        
        # Visualize
        visualizer = GraphVisualizer(reader.graph)
        fig = visualizer.visualize_with_plotly(max_nodes=20)
        assert fig is not None
        
        # Get graph stats
        graph_stats = visualizer.get_graph_stats()
        assert graph_stats['Nodes'] > 0
    
    def test_load_annotate_convert(self, sample_rdf_turtle):
        """Test loading, annotating, and converting RDF"""
        # Load
        reader = RDFReader()
        reader.load_from_file(sample_rdf_turtle.encode('utf-8'), 'Turtle')
        
        # Annotate
        annotator = RDFAnnotator(reader.graph)
        annotator.add_label("http://example.org/Bob", "Bob Johnson")
        annotator.add_triple(
            "http://example.org/Bob",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            "http://example.org/Person",
            is_literal=False
        )
        
        # Convert
        converter = RDFConverter(reader.graph)
        ntriples = converter.convert_to_format('N-Triples')
        assert len(ntriples) > 0
        assert 'Bob' in ntriples or 'bob' in ntriples.lower()
        
        # Convert to another format
        rdfxml = converter.convert_to_format('RDF/XML')
        assert len(rdfxml) > 0
    
    def test_load_query_export(self, sample_rdf_turtle):
        """Test loading, querying, and exporting data"""
        # Load
        reader = RDFReader()
        reader.load_from_file(sample_rdf_turtle.encode('utf-8'), 'Turtle')
        
        # Query
        query = """
        PREFIX ex: <http://example.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?person ?name
        WHERE {
            ?person a ex:Person .
            ?person ex:hasName ?name .
        }
        """
        
        results = reader.query_sparql(query)
        assert isinstance(results, pd.DataFrame)
        assert len(results) >= 2  # John and Jane
        
        # Export triples as DataFrame
        df = reader.get_triples_as_dataframe()
        assert len(df) > 0
        assert 'Subject' in df.columns
    
    def test_round_trip_conversion(self, sample_rdf_turtle):
        """Test round-trip format conversion"""
        # Load Turtle
        reader1 = RDFReader()
        reader1.load_from_file(sample_rdf_turtle.encode('utf-8'), 'Turtle')
        original_count = len(reader1.graph)
        
        # Convert to N-Triples
        converter = RDFConverter(reader1.graph)
        ntriples = converter.convert_to_bytes('N-Triples')
        
        # Load N-Triples
        reader2 = RDFReader()
        reader2.load_from_file(ntriples, 'N-Triples')
        
        # Should have same number of triples
        assert len(reader2.graph) == original_count
    
    def test_merge_and_visualize(self, sample_rdf_turtle):
        """Test merging graphs and visualizing"""
        # Load first graph
        reader = RDFReader()
        reader.load_from_file(sample_rdf_turtle.encode('utf-8'), 'Turtle')
        
        # Create second graph
        additional_rdf = """
        @prefix ex: <http://example.org/> .
        ex:Alice a ex:Person ;
            ex:hasName "Alice Wilson" ;
            ex:worksFor ex:TechCorp .
        """
        
        graph2 = Graph()
        graph2.parse(data=additional_rdf.encode('utf-8'), format='turtle')
        
        # Merge
        annotator = RDFAnnotator(reader.graph)
        annotator.merge_graphs(graph2)
        
        # Visualize merged graph
        visualizer = GraphVisualizer(reader.graph)
        stats = visualizer.get_graph_stats()
        
        assert stats['Nodes'] > 0
        
        # Check that Alice was added
        df = reader.get_triples_as_dataframe()
        assert any('Alice' in str(obj) for obj in df['Object'])
    
    def test_complex_workflow(self, sample_rdf_turtle):
        """Test complex workflow with multiple operations"""
        # 1. Load RDF
        reader = RDFReader()
        reader.load_from_file(sample_rdf_turtle.encode('utf-8'), 'Turtle')
        
        # 2. Add annotations
        annotator = RDFAnnotator(reader.graph)
        annotator.add_label("http://example.org/John", "Jean", language="fr")
        annotator.add_comment("http://example.org/John", "Employee of the month")
        
        # 3. Query for persons
        query = """
        PREFIX ex: <http://example.org/>
        SELECT ?person WHERE {
            ?person a ex:Person .
        }
        """
        persons = reader.query_sparql(query)
        assert len(persons) >= 2
        
        # 4. Get classes and properties
        classes = reader.get_classes()
        properties = reader.get_properties()
        assert len(classes) >= 2  # Person, Organization
        assert len(properties) >= 2  # worksFor, hasName
        
        # 5. Visualize
        visualizer = GraphVisualizer(reader.graph)
        central_nodes = visualizer.get_central_nodes(top_n=5)
        assert len(central_nodes) > 0
        
        # 6. Convert to multiple formats
        converter = RDFConverter(reader.graph)
        formats = ['Turtle', 'N-Triples', 'RDF/XML']
        
        for fmt in formats:
            output = converter.convert_to_format(fmt)
            assert len(output) > 0
            
            # Validate by re-parsing
            is_valid, error = converter.validate_syntax(output, fmt)
            if not is_valid:
                print(f"Validation failed for {fmt}: {error}")
        
        # 7. Get statistics
        stats = reader.get_stats()
        annotation_stats = annotator.get_statistics()
        graph_stats = visualizer.get_graph_stats()
        
        assert stats['Total Triples'] > 0
        assert annotation_stats['Labels'] > 0
        assert graph_stats['Nodes'] > 0


class TestDataFlowIntegration:
    """Test data flow between modules"""
    
    def test_reader_to_visualizer(self):
        """Test data flow from reader to visualizer"""
        reader = RDFReader()
        
        # Create simple graph
        rdf = """
        @prefix ex: <http://example.org/> .
        ex:A ex:connects ex:B .
        ex:B ex:connects ex:C .
        """
        
        reader.load_from_file(rdf.encode('utf-8'), 'Turtle')
        
        # Pass to visualizer
        visualizer = GraphVisualizer(reader.graph)
        
        # Check data is accessible
        assert visualizer.nx_graph.number_of_nodes() > 0
        assert visualizer.nx_graph.number_of_edges() > 0
    
    def test_reader_to_converter(self):
        """Test data flow from reader to converter"""
        reader = RDFReader()
        
        rdf = """
        @prefix ex: <http://example.org/> .
        ex:Test ex:has ex:Value .
        """
        
        reader.load_from_file(rdf.encode('utf-8'), 'Turtle')
        
        # Pass to converter
        converter = RDFConverter(reader.graph)
        
        # Convert should work
        output = converter.convert_to_format('N-Triples')
        assert 'Test' in output or 'test' in output.lower()
    
    def test_annotator_to_converter(self):
        """Test data flow from annotator to converter"""
        graph = Graph()
        annotator = RDFAnnotator(graph)
        
        # Add data via annotator
        annotator.add_triple(
            "http://example.org/Subject",
            "http://example.org/predicate",
            "http://example.org/Object",
            is_literal=False
        )
        
        # Pass to converter
        converter = RDFConverter(graph)
        output = converter.convert_to_format('Turtle')
        
        assert 'Subject' in output or 'subject' in output.lower()


class TestErrorHandlingIntegration:
    """Test error handling across modules"""
    
    def test_invalid_rdf_recovery(self):
        """Test recovery from invalid RDF"""
        reader = RDFReader()
        
        # Try to load invalid RDF
        try:
            reader.load_from_file(b"invalid rdf", 'Turtle')
            assert False, "Should have raised exception"
        except Exception:
            pass
        
        # Should still be able to use reader with valid data
        valid_rdf = """
        @prefix ex: <http://example.org/> .
        ex:Valid ex:has ex:Data .
        """
        
        result = reader.load_from_file(valid_rdf.encode('utf-8'), 'Turtle')
        assert result is True
    
    def test_empty_graph_handling(self):
        """Test handling of empty graphs across modules"""
        empty_graph = Graph()
        
        # Visualizer should handle empty graph
        visualizer = GraphVisualizer(empty_graph)
        stats = visualizer.get_graph_stats()
        assert stats['Nodes'] == 0
        
        # Converter should handle empty graph
        converter = RDFConverter(empty_graph)
        output = converter.convert_to_format('Turtle')
        assert isinstance(output, str)
        
        # Annotator should work with empty graph
        annotator = RDFAnnotator(empty_graph)
        annotator.add_triple("http://ex.org/s", "http://ex.org/p", "http://ex.org/o")
        assert len(empty_graph) == 1


class TestPerformanceIntegration:
    """Test performance with realistic data sizes"""
    
    def test_medium_graph_workflow(self):
        """Test workflow with medium-sized graph"""
        # Create graph with 100 triples
        rdf_lines = ["@prefix ex: <http://example.org/> ."]
        for i in range(100):
            rdf_lines.append(f"ex:Subject{i} ex:predicate{i % 10} ex:Object{i} .")
        
        rdf = "\n".join(rdf_lines)
        
        # Load
        reader = RDFReader()
        reader.load_from_file(rdf.encode('utf-8'), 'Turtle')
        
        # Visualize
        visualizer = GraphVisualizer(reader.graph)
        fig = visualizer.visualize_with_plotly(max_nodes=50)
        assert fig is not None
        
        # Convert
        converter = RDFConverter(reader.graph)
        output = converter.convert_to_format('N-Triples')
        assert len(output) > 0
        
        # Query
        query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
        results = reader.query_sparql(query)
        assert len(results) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

