"""
RDF Converter Module
Handles conversion between different RDF/OWL formats
"""
from rdflib import Graph
from typing import Optional
import io


class RDFConverter:
    """Class to convert between RDF formats"""
    
    def __init__(self, rdf_graph: Graph):
        self.graph = rdf_graph
        self.supported_formats = {
            'RDF/XML': 'xml',
            'Turtle': 'turtle',
            'N-Triples': 'nt',
            'N3': 'n3',
            'JSON-LD': 'json-ld',
            'TriG': 'trig',
            'NQuads': 'nquads'
        }
    
    def convert_to_format(self, format_name: str, pretty_print: bool = True) -> str:
        """
        Convert the RDF graph to specified format
        
        Args:
            format_name: Target format name (e.g., 'Turtle', 'RDF/XML')
            pretty_print: Whether to format output nicely
        
        Returns:
            str: Serialized RDF in target format
        """
        try:
            format_code = self.supported_formats.get(format_name, 'xml')
            
            # Serialize to string
            serialized = self.graph.serialize(format=format_code)
            
            # rdflib returns bytes for some formats, str for others
            if isinstance(serialized, bytes):
                serialized = serialized.decode('utf-8')
            
            return serialized
        except Exception as e:
            raise Exception(f"Error converting to {format_name}: {str(e)}")
    
    def convert_to_bytes(self, format_name: str) -> bytes:
        """
        Convert the RDF graph to bytes for download
        
        Args:
            format_name: Target format name
        
        Returns:
            bytes: Serialized RDF as bytes
        """
        try:
            format_code = self.supported_formats.get(format_name, 'xml')
            serialized = self.graph.serialize(format=format_code)
            
            if isinstance(serialized, str):
                return serialized.encode('utf-8')
            return serialized
        except Exception as e:
            raise Exception(f"Error converting to bytes: {str(e)}")
    
    def get_format_extension(self, format_name: str) -> str:
        """Get file extension for a format"""
        extensions = {
            'RDF/XML': 'rdf',
            'Turtle': 'ttl',
            'N-Triples': 'nt',
            'N3': 'n3',
            'JSON-LD': 'jsonld',
            'TriG': 'trig',
            'NQuads': 'nq'
        }
        return extensions.get(format_name, 'rdf')
    
    def validate_syntax(self, content: str, format_name: str) -> tuple[bool, Optional[str]]:
        """
        Validate RDF syntax
        
        Args:
            content: RDF content as string
            format_name: Format of the content
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            format_code = self.supported_formats.get(format_name, 'xml')
            test_graph = Graph()
            test_graph.parse(data=content, format=format_code)
            return True, None
        except Exception as e:
            return False, str(e)


class RDFAnnotator:
    """Class to handle RDF annotations and metadata"""
    
    def __init__(self, rdf_graph: Graph):
        self.graph = rdf_graph
    
    def add_triple(self, subject: str, predicate: str, object_value: str, 
                   is_literal: bool = False) -> bool:
        """
        Add a new triple to the graph
        
        Args:
            subject: Subject URI
            predicate: Predicate URI
            object_value: Object URI or literal value
            is_literal: Whether object is a literal
        
        Returns:
            bool: True if successful
        """
        try:
            from rdflib import URIRef, Literal
            
            s = URIRef(subject)
            p = URIRef(predicate)
            o = Literal(object_value) if is_literal else URIRef(object_value)
            
            self.graph.add((s, p, o))
            return True
        except Exception as e:
            raise Exception(f"Error adding triple: {str(e)}")
    
    def remove_triple(self, subject: str, predicate: str, object_value: str) -> bool:
        """
        Remove a triple from the graph
        
        Args:
            subject: Subject URI
            predicate: Predicate URI
            object_value: Object URI or literal value
        
        Returns:
            bool: True if successful
        """
        try:
            from rdflib import URIRef, Literal
            
            s = URIRef(subject)
            p = URIRef(predicate)
            
            # Try both as URI and Literal
            removed = False
            for o in [URIRef(object_value), Literal(object_value)]:
                if (s, p, o) in self.graph:
                    self.graph.remove((s, p, o))
                    removed = True
                    break
            
            return removed
        except Exception as e:
            raise Exception(f"Error removing triple: {str(e)}")
    
    def add_label(self, resource_uri: str, label: str, language: str = None) -> bool:
        """
        Add an RDFS label to a resource
        
        Args:
            resource_uri: URI of the resource
            label: Label text
            language: Optional language tag
        
        Returns:
            bool: True if successful
        """
        try:
            from rdflib import URIRef, Literal, RDFS
            
            s = URIRef(resource_uri)
            p = RDFS.label
            o = Literal(label, lang=language) if language else Literal(label)
            
            self.graph.add((s, p, o))
            return True
        except Exception as e:
            raise Exception(f"Error adding label: {str(e)}")
    
    def add_comment(self, resource_uri: str, comment: str, language: str = None) -> bool:
        """
        Add an RDFS comment to a resource
        
        Args:
            resource_uri: URI of the resource
            comment: Comment text
            language: Optional language tag
        
        Returns:
            bool: True if successful
        """
        try:
            from rdflib import URIRef, Literal, RDFS
            
            s = URIRef(resource_uri)
            p = RDFS.comment
            o = Literal(comment, lang=language) if language else Literal(comment)
            
            self.graph.add((s, p, o))
            return True
        except Exception as e:
            raise Exception(f"Error adding comment: {str(e)}")
    
    def update_triple(self, old_subject: str, old_predicate: str, old_object: str,
                     new_subject: str = None, new_predicate: str = None, 
                     new_object: str = None, is_literal: bool = False) -> bool:
        """
        Update an existing triple
        
        Args:
            old_subject: Current subject URI
            old_predicate: Current predicate URI
            old_object: Current object
            new_subject: New subject URI (optional)
            new_predicate: New predicate URI (optional)
            new_object: New object (optional)
            is_literal: Whether new object is a literal
        
        Returns:
            bool: True if successful
        """
        try:
            # Remove old triple
            self.remove_triple(old_subject, old_predicate, old_object)
            
            # Add new triple with updated values
            final_subject = new_subject if new_subject else old_subject
            final_predicate = new_predicate if new_predicate else old_predicate
            final_object = new_object if new_object else old_object
            
            return self.add_triple(final_subject, final_predicate, final_object, is_literal)
        except Exception as e:
            raise Exception(f"Error updating triple: {str(e)}")
    
    def merge_graphs(self, other_graph: Graph) -> bool:
        """
        Merge another graph into this one
        
        Args:
            other_graph: RDFLib graph to merge
        
        Returns:
            bool: True if successful
        """
        try:
            self.graph += other_graph
            return True
        except Exception as e:
            raise Exception(f"Error merging graphs: {str(e)}")
    
    def get_statistics(self) -> dict:
        """Get statistics about annotations and metadata"""
        from rdflib import RDFS, OWL, RDF
        
        stats = {
            'Labels': len(list(self.graph.triples((None, RDFS.label, None)))),
            'Comments': len(list(self.graph.triples((None, RDFS.comment, None)))),
            'Classes': len(list(self.graph.triples((None, RDF.type, OWL.Class)))) + 
                      len(list(self.graph.triples((None, RDF.type, RDFS.Class)))),
            'Properties': len(list(self.graph.triples((None, RDF.type, RDF.Property)))),
            'Annotations': 0
        }
        
        # Count annotation properties
        for s, p, o in self.graph.triples((None, RDF.type, OWL.AnnotationProperty)):
            stats['Annotations'] += len(list(self.graph.triples((None, s, None))))
        
        return stats

