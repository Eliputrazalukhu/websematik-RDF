"""
Snowflake Writer Module
Handles writing RDF data to Snowflake tables, views, and semantic views
"""
import pandas as pd
from typing import Dict, List, Optional
import streamlit as st
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL


class SnowflakeWriter:
    """Class to write RDF data to Snowflake"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self, connection_params: Dict = None):
        """
        Connect to Snowflake using connection parameters or Streamlit connection
        
        Args:
            connection_params: Dict with connection parameters (optional for Snowflake in Streamlit)
        """
        try:
            # In Snowflake Streamlit, the connection is automatic
            if hasattr(st, 'connection'):
                self.connection = st.connection("snowflake")
            else:
                # For local development, would use snowflake.connector
                import snowflake.connector
                if connection_params:
                    self.connection = snowflake.connector.connect(**connection_params)
        except Exception as e:
            raise Exception(f"Failed to connect to Snowflake: {str(e)}")
    
    def rdf_to_triples_table(self, rdf_graph: Graph, table_name: str, 
                             database: str, schema: str) -> bool:
        """
        Convert RDF graph to a triples table in Snowflake
        
        Args:
            rdf_graph: RDFLib graph
            table_name: Name of the table to create
            database: Database name
            schema: Schema name
        
        Returns:
            bool: True if successful
        """
        try:
            # Convert RDF to DataFrame
            triples = []
            for s, p, o in rdf_graph:
                triples.append({
                    'SUBJECT': str(s),
                    'PREDICATE': str(p),
                    'OBJECT': str(o),
                    'OBJECT_TYPE': 'URI' if isinstance(o, URIRef) else 'LITERAL',
                    'DATATYPE': str(o.datatype) if isinstance(o, Literal) and o.datatype else None,
                    'LANGUAGE': o.language if isinstance(o, Literal) and o.language else None
                })
            
            df = pd.DataFrame(triples)
            
            # Create table SQL
            full_table_name = f"{database}.{schema}.{table_name}"
            
            create_table_sql = f"""
            CREATE OR REPLACE TABLE {full_table_name} (
                SUBJECT VARCHAR(16777216),
                PREDICATE VARCHAR(16777216),
                OBJECT VARCHAR(16777216),
                OBJECT_TYPE VARCHAR(20),
                DATATYPE VARCHAR(1000),
                LANGUAGE VARCHAR(10)
            )
            """
            
            # Execute in Snowflake
            if hasattr(st, 'connection'):
                session = self.connection.session()
                session.sql(create_table_sql).collect()
                
                # Insert data
                from snowflake.snowpark import Session
                snowpark_df = session.create_dataframe(df)
                snowpark_df.write.mode("append").save_as_table(full_table_name)
            else:
                cursor = self.connection.cursor()
                cursor.execute(create_table_sql)
                
                # Insert data (batch insert)
                insert_sql = f"""
                INSERT INTO {full_table_name} 
                (SUBJECT, PREDICATE, OBJECT, OBJECT_TYPE, DATATYPE, LANGUAGE)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(insert_sql, [tuple(row) for row in df.values])
                cursor.close()
            
            return True
        except Exception as e:
            raise Exception(f"Error creating triples table: {str(e)}")
    
    def create_entity_view(self, rdf_graph: Graph, view_name: str,
                          database: str, schema: str,
                          entity_type: Optional[str] = None) -> bool:
        """
        Create a view of entities (subjects) with their properties
        
        Args:
            rdf_graph: RDFLib graph
            view_name: Name of the view to create
            database: Database name
            schema: Schema name
            entity_type: Filter by specific RDF type (optional)
        
        Returns:
            bool: True if successful
        """
        try:
            # Extract entities and their properties
            entities = {}
            
            for s, p, o in rdf_graph:
                subject_uri = str(s)
                if subject_uri not in entities:
                    entities[subject_uri] = {
                        'URI': subject_uri,
                        'TYPE': [],
                        'LABEL': None,
                        'PROPERTIES': {}
                    }
                
                pred_name = self._get_short_name(str(p))
                
                if p == RDF.type:
                    entities[subject_uri]['TYPE'].append(str(o))
                elif p == RDFS.label:
                    entities[subject_uri]['LABEL'] = str(o)
                else:
                    if pred_name not in entities[subject_uri]['PROPERTIES']:
                        entities[subject_uri]['PROPERTIES'][pred_name] = []
                    entities[subject_uri]['PROPERTIES'][pred_name].append(str(o))
            
            # Filter by entity type if specified
            if entity_type:
                entities = {k: v for k, v in entities.items() 
                           if entity_type in v['TYPE']}
            
            # Convert to DataFrame
            rows = []
            for uri, data in entities.items():
                row = {
                    'URI': uri,
                    'TYPE': ', '.join(data['TYPE']),
                    'LABEL': data['LABEL']
                }
                # Add properties as columns
                for prop_name, prop_values in data['PROPERTIES'].items():
                    row[prop_name] = ', '.join(prop_values[:5])  # Limit to first 5 values
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # Create temp table then view
            temp_table = f"{database}.{schema}._TEMP_{view_name}"
            full_view_name = f"{database}.{schema}.{view_name}"
            
            if hasattr(st, 'connection'):
                session = self.connection.session()
                snowpark_df = session.create_dataframe(df)
                snowpark_df.write.mode("overwrite").save_as_table(temp_table)
                
                # Create view from temp table
                view_sql = f"CREATE OR REPLACE VIEW {full_view_name} AS SELECT * FROM {temp_table}"
                session.sql(view_sql).collect()
                
                # Drop temp table
                session.sql(f"DROP TABLE IF EXISTS {temp_table}").collect()
            
            return True
        except Exception as e:
            raise Exception(f"Error creating entity view: {str(e)}")
    
    def create_semantic_view(self, rdf_graph: Graph, view_name: str,
                            database: str, schema: str,
                            class_uri: str) -> str:
        """
        Generate a semantic view definition based on OWL class structure
        
        Args:
            rdf_graph: RDFLib graph
            view_name: Name of the semantic view
            database: Database name
            schema: Schema name
            class_uri: URI of the OWL class to model
        
        Returns:
            str: SQL for creating semantic view
        """
        try:
            class_ref = URIRef(class_uri)
            
            # Get properties for this class
            properties = []
            for s, p, o in rdf_graph:
                if p in [RDFS.domain, OWL.onProperty] and o == class_ref:
                    properties.append(str(s))
            
            # Generate semantic view SQL
            sql = f"""
CREATE OR REPLACE SEMANTIC VIEW {database}.{schema}.{view_name} AS
-- Semantic view for {class_uri}
SELECT 
    SUBJECT AS ID,
    MAX(CASE WHEN PREDICATE = '{RDFS.label}' THEN OBJECT END) AS LABEL,
"""
            
            # Add columns for each property
            for idx, prop in enumerate(properties):
                prop_name = self._get_short_name(prop).upper()
                sql += f"    MAX(CASE WHEN PREDICATE = '{prop}' THEN OBJECT END) AS {prop_name}"
                if idx < len(properties) - 1:
                    sql += ","
                sql += "\n"
            
            sql += f"""
FROM {database}.{schema}.RDF_TRIPLES
WHERE OBJECT_TYPE = 'URI' 
  AND OBJECT = '{class_uri}'
  AND PREDICATE = '{RDF.type}'
  OR SUBJECT IN (
    SELECT SUBJECT FROM {database}.{schema}.RDF_TRIPLES 
    WHERE PREDICATE = '{RDF.type}' AND OBJECT = '{class_uri}'
  )
GROUP BY SUBJECT;
"""
            
            return sql
        except Exception as e:
            raise Exception(f"Error creating semantic view: {str(e)}")
    
    def create_namespace_table(self, rdf_graph: Graph, table_name: str,
                               database: str, schema: str) -> bool:
        """
        Create a table storing namespace prefixes and URIs
        
        Args:
            rdf_graph: RDFLib graph
            table_name: Name of the table
            database: Database name
            schema: Schema name
        
        Returns:
            bool: True if successful
        """
        try:
            # Extract namespaces
            namespaces = []
            for prefix, namespace in rdf_graph.namespaces():
                namespaces.append({
                    'PREFIX': str(prefix),
                    'NAMESPACE_URI': str(namespace)
                })
            
            df = pd.DataFrame(namespaces)
            full_table_name = f"{database}.{schema}.{table_name}"
            
            if hasattr(st, 'connection'):
                session = self.connection.session()
                
                # Create table
                create_sql = f"""
                CREATE OR REPLACE TABLE {full_table_name} (
                    PREFIX VARCHAR(100),
                    NAMESPACE_URI VARCHAR(16777216)
                )
                """
                session.sql(create_sql).collect()
                
                # Insert data
                snowpark_df = session.create_dataframe(df)
                snowpark_df.write.mode("append").save_as_table(full_table_name)
            
            return True
        except Exception as e:
            raise Exception(f"Error creating namespace table: {str(e)}")
    
    def _get_short_name(self, uri: str) -> str:
        """Get short name from URI"""
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            parts = uri.split('/')
            return parts[-1] if parts[-1] else parts[-2]
        return uri
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute arbitrary SQL query and return results
        
        Args:
            query: SQL query string
        
        Returns:
            DataFrame with results
        """
        try:
            if hasattr(st, 'connection'):
                return self.connection.query(query)
            else:
                cursor = self.connection.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                cursor.close()
                return pd.DataFrame(results, columns=columns)
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")

