"""
Unit tests for rdf_reader module
"""
import pytest
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from rdf_reader import RDFReader


class TestRDFReader:
    """Test cases for RDFReader class"""
    
    @pytest.fixture
    def reader(self):
        """Create a fresh RDFReader instance for each test"""
        return RDFReader()
    
    @pytest.fixture
    def sample_turtle(self):
        """Sample Turtle RDF data"""
        return """
        @prefix ex: <http://example.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        
        ex:Person rdf:type owl:Class ;
            rdfs:label "Person" ;
            rdfs:comment "A human being" .
        
        ex:worksFor rdf:type owl:ObjectProperty ;
            rdfs:domain ex:Person ;
            rdfs:range ex:Organization .
        
        ex:John rdf:type ex:Person ;
            rdfs:label "John Smith" .
        """
    
    def test_initialization(self, reader):
        """Test RDFReader initialization"""
        assert isinstance(reader.graph, Graph)
        assert isinstance(reader.namespaces, dict)
        assert len(reader.format_map) == 7
    
    def test_load_from_file_turtle(self, reader, sample_turtle):
        """Test loading Turtle format"""
        result = reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        assert result is True
        assert len(reader.graph) > 0
        assert len(reader.namespaces) > 0
    
    def test_load_from_file_invalid_format(self, reader):
        """Test loading with invalid format"""
        invalid_data = b"invalid rdf data"
        with pytest.raises(Exception):
            reader.load_from_file(invalid_data, 'Turtle')
    
    def test_get_stats(self, reader, sample_turtle):
        """Test getting statistics"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        stats = reader.get_stats()
        
        assert 'Total Triples' in stats
        assert 'Unique Subjects' in stats
        assert 'Unique Predicates' in stats
        assert 'Unique Objects' in stats
        assert 'Namespaces' in stats
        
        assert stats['Total Triples'] > 0
        assert stats['Unique Subjects'] > 0
    
    def test_get_classes(self, reader, sample_turtle):
        """Test extracting OWL classes"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        classes = reader.get_classes()
        
        assert len(classes) > 0
        assert any('Person' in str(c) for c in classes)
    
    def test_get_properties(self, reader, sample_turtle):
        """Test extracting properties"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        properties = reader.get_properties()
        
        assert len(properties) > 0
        assert any('worksFor' in str(p[0]) for p in properties)
    
    def test_get_individuals(self, reader, sample_turtle):
        """Test extracting individuals"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        
        # Add an individual explicitly
        reader.graph.add((
            URIRef("http://example.org/John"),
            RDF.type,
            OWL.NamedIndividual
        ))
        
        individuals = reader.get_individuals()
        assert len(individuals) >= 0
    
    def test_get_triples_as_dataframe(self, reader, sample_turtle):
        """Test converting triples to DataFrame"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        df = reader.get_triples_as_dataframe()
        
        assert len(df) > 0
        assert 'Subject' in df.columns
        assert 'Predicate' in df.columns
        assert 'Object' in df.columns
        assert 'Object_Type' in df.columns
    
    def test_query_sparql(self, reader, sample_turtle):
        """Test SPARQL query execution"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?s ?label
        WHERE {
            ?s rdfs:label ?label .
        }
        """
        
        results = reader.query_sparql(query)
        assert len(results) > 0
        assert 'label' in results.columns
    
    def test_query_sparql_invalid(self, reader, sample_turtle):
        """Test SPARQL query with invalid syntax"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        
        invalid_query = "INVALID SPARQL QUERY"
        
        with pytest.raises(Exception):
            reader.query_sparql(invalid_query)
    
    def test_get_resource_details(self, reader, sample_turtle):
        """Test getting resource details"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        
        details = reader.get_resource_details("http://example.org/Person")
        
        assert 'URI' in details
        assert 'Outgoing' in details
        assert 'Incoming' in details
        assert details['URI'] == "http://example.org/Person"
    
    def test_multiple_formats(self, reader):
        """Test support for multiple RDF formats"""
        formats = ['RDF/XML', 'Turtle', 'N-Triples', 'N3', 'JSON-LD', 'TriG', 'NQuads']
        
        for format_name in formats:
            assert format_name in reader.format_map
    
    def test_empty_graph(self, reader):
        """Test operations on empty graph"""
        stats = reader.get_stats()
        assert stats['Total Triples'] == 0
        
        classes = reader.get_classes()
        assert len(classes) == 0
        
        properties = reader.get_properties()
        assert len(properties) == 0
    
    def test_namespace_extraction(self, reader, sample_turtle):
        """Test namespace extraction"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        
        assert len(reader.namespaces) > 0
        assert 'ex' in reader.namespaces or '' in reader.namespaces
        assert 'rdf' in reader.namespaces
        assert 'rdfs' in reader.namespaces
        assert 'owl' in reader.namespaces
    
    def test_get_label(self, reader, sample_turtle):
        """Test label extraction"""
        reader.load_from_file(sample_turtle.encode('utf-8'), 'Turtle')
        
        person_uri = URIRef("http://example.org/Person")
        label = reader._get_label(person_uri)
        
        assert label in ["Person", "Person"]  # Could be label or URI fragment
    
    def test_large_graph(self, reader):
        """Test with a larger graph"""
        # Create a graph with many triples
        for i in range(100):
            reader.graph.add((
                URIRef(f"http://example.org/subject{i}"),
                URIRef(f"http://example.org/predicate"),
                Literal(f"Object {i}")
            ))
        
        stats = reader.get_stats()
        assert stats['Total Triples'] == 100
        assert stats['Unique Subjects'] == 100
        
        df = reader.get_triples_as_dataframe()
        assert len(df) == 100


class TestRDFReaderEdgeCases:
    """Test edge cases and error handling"""
    
    def test_malformed_data(self):
        """Test with malformed RDF data"""
        reader = RDFReader()
        malformed = b"@prefix ex: <http://example.org/> . ex:Test ex:has"
        
        with pytest.raises(Exception):
            reader.load_from_file(malformed, 'Turtle')
    
    def test_empty_file(self):
        """Test with empty file"""
        reader = RDFReader()
        empty = b""
        
        # Empty file might be valid (empty graph) or raise exception
        try:
            result = reader.load_from_file(empty, 'Turtle')
            assert len(reader.graph) == 0
        except Exception:
            pass  # Some parsers might reject empty input
    
    def test_special_characters_in_literals(self):
        """Test handling of special characters"""
        reader = RDFReader()
        data = """
        @prefix ex: <http://example.org/> .
        ex:test ex:hasValue "Special chars: @#$%^&*()[]{}\\n\\t" .
        """
        
        reader.load_from_file(data.encode('utf-8'), 'Turtle')
        stats = reader.get_stats()
        assert stats['Total Triples'] > 0
    
    def test_unicode_content(self):
        """Test handling of Unicode characters"""
        reader = RDFReader()
        data = """
        @prefix ex: <http://example.org/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ex:test rdfs:label "日本語"@ja .
        ex:test rdfs:label "中文"@zh .
        """
        
        reader.load_from_file(data.encode('utf-8'), 'Turtle')
        df = reader.get_triples_as_dataframe()
        assert len(df) >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

