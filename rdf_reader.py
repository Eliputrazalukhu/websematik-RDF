"""
RDF/OWL Reader Module
Handles reading and parsing of RDF and OWL files in various formats
"""
import rdflib
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from typing import Dict, List, Tuple, Optional
import pandas as pd


class RDFReader:
    """Class to read and parse RDF/OWL files"""
    
    def __init__(self):
        self.graph = Graph()
        self.namespaces = {}
        self.format_map = {
            'RDF/XML': 'xml',
            'Turtle': 'turtle',
            'N-Triples': 'nt',
            'N3': 'n3',
            'JSON-LD': 'json-ld',
            'TriG': 'trig',
            'NQuads': 'nquads'
        }
    
    def load_from_file(self, file_content: bytes, format_name: str) -> bool:
        """
        Load RDF/OWL from file content
        
        Args:
            file_content: Bytes content of the file
            format_name: Format name (e.g., 'RDF/XML', 'Turtle')
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            format_code = self.format_map.get(format_name, 'xml')
            self.graph.parse(data=file_content, format=format_code)
            self._extract_namespaces()
            return True
        except Exception as e:
            raise Exception(f"Error parsing RDF: {str(e)}")
    
    def load_from_url(self, url: str, format_name: str = 'xml') -> bool:
        """
        Load RDF/OWL from URL
        
        Args:
            url: URL to load from
            format_name: Format name
        
        Returns:
            bool: True if successful
        """
        try:
            format_code = self.format_map.get(format_name, 'xml')
            self.graph.parse(url, format=format_code)
            self._extract_namespaces()
            return True
        except Exception as e:
            raise Exception(f"Error loading from URL: {str(e)}")
    
    def _extract_namespaces(self):
        """Extract namespaces from the graph"""
        self.namespaces = {prefix: str(ns) for prefix, ns in self.graph.namespaces()}
    
    def get_stats(self) -> Dict:
        """Get statistics about the loaded RDF graph"""
        return {
            'Total Triples': len(self.graph),
            'Unique Subjects': len(set(self.graph.subjects())),
            'Unique Predicates': len(set(self.graph.predicates())),
            'Unique Objects': len(set(self.graph.objects())),
            'Namespaces': len(self.namespaces)
        }
    
    def get_classes(self) -> List[Tuple]:
        """Get all OWL/RDFS classes"""
        classes = []
        for s in self.graph.subjects(RDF.type, OWL.Class):
            label = self._get_label(s)
            classes.append((str(s), label))
        for s in self.graph.subjects(RDF.type, RDFS.Class):
            label = self._get_label(s)
            classes.append((str(s), label))
        return list(set(classes))
    
    def get_properties(self) -> List[Tuple]:
        """Get all OWL properties"""
        properties = []
        property_types = [
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.AnnotationProperty,
            RDF.Property
        ]
        for prop_type in property_types:
            for s in self.graph.subjects(RDF.type, prop_type):
                label = self._get_label(s)
                properties.append((str(s), label, str(prop_type)))
        return list(set(properties))
    
    def get_individuals(self) -> List[Tuple]:
        """Get all OWL individuals/instances"""
        individuals = []
        for s in self.graph.subjects(RDF.type, OWL.NamedIndividual):
            label = self._get_label(s)
            classes = [str(c) for c in self.graph.objects(s, RDF.type) if c != OWL.NamedIndividual]
            individuals.append((str(s), label, ', '.join(classes)))
        return individuals
    
    def _get_label(self, resource) -> str:
        """Get label for a resource"""
        for label in self.graph.objects(resource, RDFS.label):
            return str(label)
        # If no label, return the last part of URI
        uri = str(resource)
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            return uri.split('/')[-1]
        return uri
    
    def get_triples_as_dataframe(self) -> pd.DataFrame:
        """Convert all triples to a pandas DataFrame"""
        triples = []
        for s, p, o in self.graph:
            triples.append({
                'Subject': str(s),
                'Predicate': str(p),
                'Object': str(o),
                'Object_Type': 'URI' if isinstance(o, rdflib.URIRef) else 'Literal'
            })
        return pd.DataFrame(triples)
    
    def query_sparql(self, query: str) -> pd.DataFrame:
        """
        Execute SPARQL query on the graph
        
        Args:
            query: SPARQL query string
        
        Returns:
            DataFrame with query results
        """
        try:
            results = self.graph.query(query)
            data = []
            for row in results:
                data.append([str(val) for val in row])
            
            # Get column names from results
            if results.vars:
                columns = [str(var) for var in results.vars]
            else:
                columns = [f"col_{i}" for i in range(len(data[0]) if data else 0)]
            
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            raise Exception(f"SPARQL query error: {str(e)}")
    
    def get_resource_details(self, resource_uri: str) -> Dict:
        """Get all details about a specific resource"""
        resource = rdflib.URIRef(resource_uri)
        details = {
            'URI': resource_uri,
            'Outgoing': [],
            'Incoming': []
        }
        
        # Outgoing triples (resource as subject)
        for p, o in self.graph.predicate_objects(resource):
            details['Outgoing'].append({
                'Predicate': str(p),
                'Object': str(o)
            })
        
        # Incoming triples (resource as object)
        for s, p in self.graph.subject_predicates(resource):
            details['Incoming'].append({
                'Subject': str(s),
                'Predicate': str(p)
            })
        
        return details

