"""
Unit tests for rdf_converter module
"""
import pytest
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL
from rdf_converter import RDFConverter, RDFAnnotator


class TestRDFConverter:
    """Test cases for RDFConverter class"""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample RDF graph"""
        g = Graph()
        ex = "http://example.org/"
        
        g.add((URIRef(ex + "Person"), RDF.type, OWL.Class))
        g.add((URIRef(ex + "Person"), RDFS.label, Literal("Person")))
        g.add((URIRef(ex + "John"), RDF.type, URIRef(ex + "Person")))
        
        return g
    
    @pytest.fixture
    def converter(self, sample_graph):
        """Create a RDFConverter instance"""
        return RDFConverter(sample_graph)
    
    def test_initialization(self, converter):
        """Test RDFConverter initialization"""
        assert isinstance(converter.graph, Graph)
        assert len(converter.supported_formats) == 7
    
    def test_convert_to_turtle(self, converter):
        """Test conversion to Turtle format"""
        result = converter.convert_to_format('Turtle')
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert '@prefix' in result or 'PREFIX' in result or '<http' in result
    
    def test_convert_to_rdfxml(self, converter):
        """Test conversion to RDF/XML format"""
        result = converter.convert_to_format('RDF/XML')
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert '<?xml' in result or '<rdf:RDF' in result
    
    def test_convert_to_ntriples(self, converter):
        """Test conversion to N-Triples format"""
        result = converter.convert_to_format('N-Triples')
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert '<http' in result
        assert '.' in result
    
    def test_convert_to_jsonld(self, converter):
        """Test conversion to JSON-LD format"""
        result = converter.convert_to_format('JSON-LD')
        
        assert isinstance(result, str)
        assert len(result) > 0
        # JSON-LD should have JSON structure
        assert '{' in result or '[' in result
    
    def test_convert_to_n3(self, converter):
        """Test conversion to N3 format"""
        result = converter.convert_to_format('N3')
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_convert_all_formats(self, converter):
        """Test conversion to all supported formats"""
        for format_name in converter.supported_formats.keys():
            # Skip NQuads and TriG for simple graphs (they require context-aware stores)
            if format_name in ['NQuads', 'TriG']:
                continue
            
            result = converter.convert_to_format(format_name)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_convert_to_bytes(self, converter):
        """Test conversion to bytes"""
        result = converter.convert_to_bytes('Turtle')
        
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_get_format_extension(self, converter):
        """Test getting file extensions"""
        assert converter.get_format_extension('Turtle') == 'ttl'
        assert converter.get_format_extension('RDF/XML') == 'rdf'
        assert converter.get_format_extension('N-Triples') == 'nt'
        assert converter.get_format_extension('JSON-LD') == 'jsonld'
    
    def test_validate_syntax_valid(self, converter):
        """Test syntax validation with valid RDF"""
        valid_turtle = """
        @prefix ex: <http://example.org/> .
        ex:Test ex:has ex:Value .
        """
        
        is_valid, error = converter.validate_syntax(valid_turtle, 'Turtle')
        assert is_valid is True
        assert error is None
    
    def test_validate_syntax_invalid(self, converter):
        """Test syntax validation with invalid RDF"""
        invalid_turtle = "@prefix ex: <http://example.org/> . ex:Test ex:has"
        
        is_valid, error = converter.validate_syntax(invalid_turtle, 'Turtle')
        assert is_valid is False
        assert error is not None
    
    def test_empty_graph_conversion(self):
        """Test converting empty graph"""
        empty_graph = Graph()
        converter = RDFConverter(empty_graph)
        
        result = converter.convert_to_format('Turtle')
        assert isinstance(result, str)
    
    def test_large_graph_conversion(self):
        """Test converting large graph"""
        g = Graph()
        for i in range(1000):
            g.add((
                URIRef(f"http://example.org/subject{i}"),
                URIRef(f"http://example.org/predicate"),
                Literal(f"Object {i}")
            ))
        
        converter = RDFConverter(g)
        result = converter.convert_to_format('N-Triples')
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestRDFAnnotator:
    """Test cases for RDFAnnotator class"""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample RDF graph"""
        g = Graph()
        ex = "http://example.org/"
        
        g.add((URIRef(ex + "Person"), RDF.type, OWL.Class))
        g.add((URIRef(ex + "Person"), RDFS.label, Literal("Person")))
        
        return g
    
    @pytest.fixture
    def annotator(self, sample_graph):
        """Create a RDFAnnotator instance"""
        return RDFAnnotator(sample_graph)
    
    def test_initialization(self, annotator):
        """Test RDFAnnotator initialization"""
        assert isinstance(annotator.graph, Graph)
    
    def test_add_triple_uri(self, annotator):
        """Test adding triple with URI object"""
        result = annotator.add_triple(
            "http://example.org/John",
            "http://example.org/worksFor",
            "http://example.org/Company",
            is_literal=False
        )
        
        assert result is True
        assert len(annotator.graph) > 0
        
        # Verify triple was added
        exists = (
            URIRef("http://example.org/John"),
            URIRef("http://example.org/worksFor"),
            URIRef("http://example.org/Company")
        ) in annotator.graph
        
        assert exists is True
    
    def test_add_triple_literal(self, annotator):
        """Test adding triple with literal object"""
        result = annotator.add_triple(
            "http://example.org/John",
            "http://example.org/hasName",
            "John Smith",
            is_literal=True
        )
        
        assert result is True
        
        # Verify triple was added
        exists = (
            URIRef("http://example.org/John"),
            URIRef("http://example.org/hasName"),
            Literal("John Smith")
        ) in annotator.graph
        
        assert exists is True
    
    def test_remove_triple(self, annotator):
        """Test removing a triple"""
        # First add a triple
        annotator.add_triple(
            "http://example.org/Test",
            "http://example.org/hasValue",
            "TestValue",
            is_literal=True
        )
        
        initial_count = len(annotator.graph)
        
        # Now remove it
        result = annotator.remove_triple(
            "http://example.org/Test",
            "http://example.org/hasValue",
            "TestValue"
        )
        
        assert result is True
        assert len(annotator.graph) < initial_count
    
    def test_remove_nonexistent_triple(self, annotator):
        """Test removing a triple that doesn't exist"""
        result = annotator.remove_triple(
            "http://example.org/NonExistent",
            "http://example.org/hasValue",
            "Value"
        )
        
        assert result is False
    
    def test_add_label(self, annotator):
        """Test adding a label"""
        result = annotator.add_label(
            "http://example.org/NewResource",
            "New Resource Label"
        )
        
        assert result is True
        
        # Verify label was added
        exists = (
            URIRef("http://example.org/NewResource"),
            RDFS.label,
            Literal("New Resource Label")
        ) in annotator.graph
        
        assert exists is True
    
    def test_add_label_with_language(self, annotator):
        """Test adding a label with language tag"""
        result = annotator.add_label(
            "http://example.org/Resource",
            "English Label",
            language="en"
        )
        
        assert result is True
        
        # Check that a label exists (language-tagged literals are tricky to check exactly)
        has_label = False
        for s, p, o in annotator.graph.triples((
            URIRef("http://example.org/Resource"),
            RDFS.label,
            None
        )):
            if str(o) == "English Label":
                has_label = True
                break
        
        assert has_label is True
    
    def test_add_comment(self, annotator):
        """Test adding a comment"""
        result = annotator.add_comment(
            "http://example.org/Resource",
            "This is a comment"
        )
        
        assert result is True
        
        # Verify comment was added
        exists = (
            URIRef("http://example.org/Resource"),
            RDFS.comment,
            Literal("This is a comment")
        ) in annotator.graph
        
        assert exists is True
    
    def test_update_triple(self, annotator):
        """Test updating a triple"""
        # Add initial triple
        annotator.add_triple(
            "http://example.org/John",
            "http://example.org/hasAge",
            "25",
            is_literal=True
        )
        
        # Update it
        result = annotator.update_triple(
            "http://example.org/John",
            "http://example.org/hasAge",
            "25",
            new_object="26",
            is_literal=True
        )
        
        assert result is True
        
        # Verify old triple is gone
        old_exists = (
            URIRef("http://example.org/John"),
            URIRef("http://example.org/hasAge"),
            Literal("25")
        ) in annotator.graph
        
        # Verify new triple exists
        new_exists = (
            URIRef("http://example.org/John"),
            URIRef("http://example.org/hasAge"),
            Literal("26")
        ) in annotator.graph
        
        assert old_exists is False
        assert new_exists is True
    
    def test_merge_graphs(self, annotator):
        """Test merging graphs"""
        # Create another graph
        other_graph = Graph()
        other_graph.add((
            URIRef("http://example.org/NewSubject"),
            URIRef("http://example.org/hasProperty"),
            Literal("Value")
        ))
        
        initial_count = len(annotator.graph)
        
        result = annotator.merge_graphs(other_graph)
        
        assert result is True
        assert len(annotator.graph) > initial_count
    
    def test_get_statistics(self, annotator):
        """Test getting annotation statistics"""
        # Add some annotations
        annotator.add_label("http://example.org/Test1", "Test 1")
        annotator.add_label("http://example.org/Test2", "Test 2")
        annotator.add_comment("http://example.org/Test1", "A comment")
        
        stats = annotator.get_statistics()
        
        assert 'Labels' in stats
        assert 'Comments' in stats
        assert 'Classes' in stats
        assert 'Properties' in stats
        assert 'Annotations' in stats
        
        assert stats['Labels'] >= 2  # We added 2, plus initial graph might have more
        assert stats['Comments'] >= 1
    
    def test_multiple_labels(self, annotator):
        """Test adding multiple labels to same resource"""
        resource = "http://example.org/MultiLabel"
        
        annotator.add_label(resource, "English Label", "en")
        annotator.add_label(resource, "French Label", "fr")
        annotator.add_label(resource, "German Label", "de")
        
        # Count labels for this resource
        labels = list(annotator.graph.triples((
            URIRef(resource),
            RDFS.label,
            None
        )))
        
        assert len(labels) == 3


class TestRDFConverterEdgeCases:
    """Test edge cases"""
    
    def test_special_characters_in_literals(self):
        """Test handling special characters"""
        g = Graph()
        g.add((
            URIRef("http://example.org/test"),
            URIRef("http://example.org/hasValue"),
            Literal('Special: \n\t\r"\'\\')
        ))
        
        converter = RDFConverter(g)
        
        # Should not crash on any format
        for format_name in ['Turtle', 'N-Triples', 'RDF/XML']:
            result = converter.convert_to_format(format_name)
            assert len(result) > 0
    
    def test_unicode_characters(self):
        """Test Unicode character handling"""
        g = Graph()
        g.add((
            URIRef("http://example.org/test"),
            RDFS.label,
            Literal("日本語テスト", lang="ja")
        ))
        
        converter = RDFConverter(g)
        result = converter.convert_to_format('Turtle')
        
        assert len(result) > 0
    
    def test_very_long_literals(self):
        """Test with very long literal values"""
        g = Graph()
        long_text = "x" * 10000
        g.add((
            URIRef("http://example.org/test"),
            URIRef("http://example.org/hasText"),
            Literal(long_text)
        ))
        
        converter = RDFConverter(g)
        result = converter.convert_to_format('N-Triples')
        
        assert len(result) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

