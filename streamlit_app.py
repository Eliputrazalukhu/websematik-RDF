"""
RDF/OWL Visualizer and Editor for Snowflake
A comprehensive Streamlit application for working with RDF and OWL ontologies
"""
import streamlit as st
from rdflib import Graph
import pandas as pd
from io import BytesIO

# Import custom modules
from rdf_reader import RDFReader
from graph_visualizer import GraphVisualizer
from rdf_converter import RDFConverter, RDFAnnotator
from snowflake_writer import SnowflakeWriter


# Page configuration
st.set_page_config(
    page_title="RDF/OWL Visualizer & Editor",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'rdf_reader' not in st.session_state:
    st.session_state.rdf_reader = RDFReader()
if 'graph_loaded' not in st.session_state:
    st.session_state.graph_loaded = False
if 'snowflake_connected' not in st.session_state:
    st.session_state.snowflake_connected = False


def main():
    """Main application function"""
    
    st.title("🔗 RDF/OWL Visualizer & Editor for Snowflake")
    st.markdown("""
    A comprehensive tool for reading, visualizing, annotating, and converting RDF/OWL ontologies,
    with direct integration to Snowflake tables, views, and semantic views.
    """)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Module",
        ["📁 Load RDF/OWL", "📊 Visualize Graph", "✏️ Annotate & Edit", 
         "🔄 Convert Formats", "❄️ Export to Snowflake", "🔍 Query Data"]
    )
    
    # Display current graph status
    if st.session_state.graph_loaded:
        stats = st.session_state.rdf_reader.get_stats()
        st.sidebar.success("✅ Graph Loaded")
        st.sidebar.metric("Triples", stats['Total Triples'])
        st.sidebar.metric("Subjects", stats['Unique Subjects'])
    else:
        st.sidebar.warning("⚠️ No graph loaded")
    
    # Route to appropriate page
    if page == "📁 Load RDF/OWL":
        load_rdf_page()
    elif page == "📊 Visualize Graph":
        visualize_page()
    elif page == "✏️ Annotate & Edit":
        annotate_page()
    elif page == "🔄 Convert Formats":
        convert_page()
    elif page == "❄️ Export to Snowflake":
        snowflake_export_page()
    elif page == "🔍 Query Data":
        query_page()


def load_rdf_page():
    """Page for loading RDF/OWL files"""
    st.header("📁 Load RDF/OWL Data")
    
    tab1, tab2, tab3 = st.tabs(["Upload File", "Load from URL", "Sample Data"])
    
    with tab1:
        st.subheader("Upload RDF/OWL File")
        
        format_choice = st.selectbox(
            "Select RDF Format",
            ["RDF/XML", "Turtle", "N-Triples", "N3", "JSON-LD", "TriG", "NQuads"]
        )
        
        uploaded_file = st.file_uploader(
            "Choose an RDF/OWL file",
            type=['rdf', 'owl', 'ttl', 'nt', 'n3', 'jsonld', 'trig', 'nq', 'xml']
        )
        
        if uploaded_file is not None:
            if st.button("Load File", type="primary"):
                try:
                    with st.spinner("Loading RDF data..."):
                        content = uploaded_file.read()
                        st.session_state.rdf_reader.load_from_file(content, format_choice)
                        st.session_state.graph_loaded = True
                        st.success("✅ RDF data loaded successfully!")
                        
                        # Display statistics
                        stats = st.session_state.rdf_reader.get_stats()
                        col1, col2, col3, col4, col5 = st.columns(5)
                        col1.metric("Triples", stats['Total Triples'])
                        col2.metric("Subjects", stats['Unique Subjects'])
                        col3.metric("Predicates", stats['Unique Predicates'])
                        col4.metric("Objects", stats['Unique Objects'])
                        col5.metric("Namespaces", stats['Namespaces'])
                        
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
    
    with tab2:
        st.subheader("Load from URL")
        
        url = st.text_input("Enter RDF/OWL URL")
        format_choice_url = st.selectbox(
            "Select RDF Format",
            ["RDF/XML", "Turtle", "N-Triples", "N3", "JSON-LD"],
            key="url_format"
        )
        
        if st.button("Load from URL", type="primary"):
            if url:
                try:
                    with st.spinner("Loading from URL..."):
                        st.session_state.rdf_reader.load_from_url(url, format_choice_url)
                        st.session_state.graph_loaded = True
                        st.success("✅ RDF data loaded successfully!")
                        
                        stats = st.session_state.rdf_reader.get_stats()
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Triples", stats['Total Triples'])
                        col2.metric("Subjects", stats['Unique Subjects'])
                        col3.metric("Namespaces", stats['Namespaces'])
                        
                except Exception as e:
                    st.error(f"❌ Error loading from URL: {str(e)}")
            else:
                st.warning("Please enter a URL")
    
    with tab3:
        st.subheader("Load Sample Ontology")
        st.info("Create a simple sample RDF graph for testing")
        
        if st.button("Create Sample Graph", type="primary"):
            try:
                sample_rdf = """
                @prefix ex: <http://example.org/> .
                @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
                @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                
                ex:Person rdf:type owl:Class ;
                    rdfs:label "Person" ;
                    rdfs:comment "A human being" .
                
                ex:Organization rdf:type owl:Class ;
                    rdfs:label "Organization" ;
                    rdfs:comment "A social entity" .
                
                ex:worksFor rdf:type owl:ObjectProperty ;
                    rdfs:label "works for" ;
                    rdfs:domain ex:Person ;
                    rdfs:range ex:Organization .
                
                ex:hasName rdf:type owl:DatatypeProperty ;
                    rdfs:label "has name" ;
                    rdfs:domain ex:Person .
                
                ex:John rdf:type ex:Person ;
                    ex:hasName "John Smith" ;
                    ex:worksFor ex:TechCorp .
                
                ex:Jane rdf:type ex:Person ;
                    ex:hasName "Jane Doe" ;
                    ex:worksFor ex:TechCorp .
                
                ex:TechCorp rdf:type ex:Organization ;
                    ex:hasName "TechCorp Inc." .
                """
                
                st.session_state.rdf_reader.load_from_file(
                    sample_rdf.encode('utf-8'), 
                    'Turtle'
                )
                st.session_state.graph_loaded = True
                st.success("✅ Sample graph created!")
                
            except Exception as e:
                st.error(f"❌ Error creating sample: {str(e)}")


def visualize_page():
    """Page for visualizing RDF graphs"""
    st.header("📊 Visualize Graph")
    
    if not st.session_state.graph_loaded:
        st.warning("⚠️ Please load an RDF/OWL file first")
        return
    
    visualizer = GraphVisualizer(st.session_state.rdf_reader.graph)
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Interactive Graph", "Graph Statistics", "Browse Entities", "Explore Triples"]
    )
    
    with tab1:
        st.subheader("Interactive Graph Visualization")
        
        viz_type = st.radio(
            "Visualization Type",
            ["Plotly (Interactive)", "Network Graph"],
            horizontal=True
        )
        
        max_nodes = st.slider("Maximum nodes to display", 10, 200, 50)
        
        if viz_type == "Plotly (Interactive)":
            try:
                fig = visualizer.visualize_with_plotly(max_nodes=max_nodes)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating visualization: {str(e)}")
        else:
            try:
                nodes, edges, config = visualizer.visualize_with_agraph(max_nodes=max_nodes)
                
                if config is None:
                    st.warning("⚠️ streamlit-agraph is not installed. Using Plotly visualization instead.")
                    st.info("To enable network graph visualization, install: `pip install streamlit-agraph`")
                    fig = visualizer.visualize_with_plotly(max_nodes=max_nodes)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    from streamlit_agraph import agraph
                    agraph(nodes=nodes, edges=edges, config=config)
            except Exception as e:
                st.error(f"Error creating network graph: {str(e)}")
    
    with tab2:
        st.subheader("Graph Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### RDF Statistics")
            stats = st.session_state.rdf_reader.get_stats()
            for key, value in stats.items():
                st.metric(key, value)
        
        with col2:
            st.markdown("### Network Statistics")
            graph_stats = visualizer.get_graph_stats()
            for key, value in graph_stats.items():
                if isinstance(value, float):
                    st.metric(key, f"{value:.4f}")
                else:
                    st.metric(key, value)
        
        st.markdown("### Most Central Nodes")
        central_nodes = visualizer.get_central_nodes(top_n=10)
        if central_nodes:
            df = pd.DataFrame(central_nodes, columns=['Node', 'Centrality'])
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.subheader("Browse Entities")
        
        entity_type = st.selectbox(
            "Select Entity Type",
            ["Classes", "Properties", "Individuals"]
        )
        
        if entity_type == "Classes":
            classes = st.session_state.rdf_reader.get_classes()
            if classes:
                df = pd.DataFrame(classes, columns=['URI', 'Label'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No classes found")
        
        elif entity_type == "Properties":
            properties = st.session_state.rdf_reader.get_properties()
            if properties:
                df = pd.DataFrame(properties, columns=['URI', 'Label', 'Type'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No properties found")
        
        elif entity_type == "Individuals":
            individuals = st.session_state.rdf_reader.get_individuals()
            if individuals:
                df = pd.DataFrame(individuals, columns=['URI', 'Label', 'Classes'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No individuals found")
    
    with tab4:
        st.subheader("Explore Triples")
        
        df = st.session_state.rdf_reader.get_triples_as_dataframe()
        
        st.markdown(f"**Total Triples: {len(df)}**")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            search_subject = st.text_input("Filter by Subject (contains)")
        with col2:
            search_predicate = st.text_input("Filter by Predicate (contains)")
        
        # Apply filters
        filtered_df = df
        if search_subject:
            filtered_df = filtered_df[filtered_df['Subject'].str.contains(search_subject, case=False, na=False)]
        if search_predicate:
            filtered_df = filtered_df[filtered_df['Predicate'].str.contains(search_predicate, case=False, na=False)]
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="rdf_triples.csv",
            mime="text/csv"
        )


def annotate_page():
    """Page for annotating and editing RDF"""
    st.header("✏️ Annotate & Edit RDF")
    
    if not st.session_state.graph_loaded:
        st.warning("⚠️ Please load an RDF/OWL file first")
        return
    
    annotator = RDFAnnotator(st.session_state.rdf_reader.graph)
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Add Triple", "Remove Triple", "Add Metadata", "Statistics"]
    )
    
    with tab1:
        st.subheader("Add New Triple")
        
        with st.form("add_triple_form"):
            subject = st.text_input("Subject URI", placeholder="http://example.org/subject")
            predicate = st.text_input("Predicate URI", placeholder="http://example.org/property")
            object_value = st.text_input("Object", placeholder="http://example.org/object or literal value")
            is_literal = st.checkbox("Object is a literal value (not URI)")
            
            submitted = st.form_submit_button("Add Triple", type="primary")
            
            if submitted:
                if subject and predicate and object_value:
                    try:
                        annotator.add_triple(subject, predicate, object_value, is_literal)
                        st.success("✅ Triple added successfully!")
                    except Exception as e:
                        st.error(f"❌ Error adding triple: {str(e)}")
                else:
                    st.warning("Please fill in all fields")
    
    with tab2:
        st.subheader("Remove Triple")
        
        # Show existing triples for selection
        df = st.session_state.rdf_reader.get_triples_as_dataframe()
        
        with st.form("remove_triple_form"):
            subject_rm = st.text_input("Subject URI", key="rm_subject")
            predicate_rm = st.text_input("Predicate URI", key="rm_predicate")
            object_rm = st.text_input("Object", key="rm_object")
            
            submitted_rm = st.form_submit_button("Remove Triple", type="primary")
            
            if submitted_rm:
                if subject_rm and predicate_rm and object_rm:
                    try:
                        result = annotator.remove_triple(subject_rm, predicate_rm, object_rm)
                        if result:
                            st.success("✅ Triple removed successfully!")
                            st.rerun()
                        else:
                            st.warning("Triple not found in graph")
                    except Exception as e:
                        st.error(f"❌ Error removing triple: {str(e)}")
                else:
                    st.warning("Please fill in all fields")
    
    with tab3:
        st.subheader("Add Metadata (Labels & Comments)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Add Label")
            with st.form("add_label_form"):
                resource_uri_label = st.text_input("Resource URI", key="label_uri")
                label_text = st.text_input("Label")
                language_label = st.text_input("Language (optional)", placeholder="en")
                
                if st.form_submit_button("Add Label", type="primary"):
                    if resource_uri_label and label_text:
                        try:
                            lang = language_label if language_label else None
                            annotator.add_label(resource_uri_label, label_text, lang)
                            st.success("✅ Label added!")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("Please fill in required fields")
        
        with col2:
            st.markdown("#### Add Comment")
            with st.form("add_comment_form"):
                resource_uri_comment = st.text_input("Resource URI", key="comment_uri")
                comment_text = st.text_area("Comment")
                language_comment = st.text_input("Language (optional)", placeholder="en", key="lang_comment")
                
                if st.form_submit_button("Add Comment", type="primary"):
                    if resource_uri_comment and comment_text:
                        try:
                            lang = language_comment if language_comment else None
                            annotator.add_comment(resource_uri_comment, comment_text, lang)
                            st.success("✅ Comment added!")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("Please fill in required fields")
    
    with tab4:
        st.subheader("Annotation Statistics")
        
        stats = annotator.get_statistics()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Labels", stats['Labels'])
        col2.metric("Comments", stats['Comments'])
        col3.metric("Classes", stats['Classes'])
        col4.metric("Properties", stats['Properties'])
        col5.metric("Annotations", stats['Annotations'])


def convert_page():
    """Page for converting between RDF formats"""
    st.header("🔄 Convert RDF Formats")
    
    if not st.session_state.graph_loaded:
        st.warning("⚠️ Please load an RDF/OWL file first")
        return
    
    converter = RDFConverter(st.session_state.rdf_reader.graph)
    
    st.markdown("""
    Convert your loaded RDF graph to different formats.
    All standard RDF serialization formats are supported.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        target_format = st.selectbox(
            "Select Target Format",
            ["RDF/XML", "Turtle", "N-Triples", "N3", "JSON-LD", "TriG", "NQuads"]
        )
    
    with col2:
        st.markdown("###")
        convert_btn = st.button("🔄 Convert", type="primary", use_container_width=True)
    
    if convert_btn:
        try:
            with st.spinner(f"Converting to {target_format}..."):
                converted = converter.convert_to_format(target_format)
                
                st.success(f"✅ Converted to {target_format}")
                
                # Preview
                st.subheader("Preview")
                st.code(converted[:2000] + ("..." if len(converted) > 2000 else ""), 
                       language="xml" if target_format == "RDF/XML" else "turtle")
                
                # Download button
                file_extension = converter.get_format_extension(target_format)
                filename = f"converted_rdf.{file_extension}"
                
                converted_bytes = converter.convert_to_bytes(target_format)
                
                st.download_button(
                    label=f"📥 Download {target_format}",
                    data=converted_bytes,
                    file_name=filename,
                    mime="application/rdf+xml" if target_format == "RDF/XML" else "text/plain"
                )
                
        except Exception as e:
            st.error(f"❌ Conversion error: {str(e)}")


def snowflake_export_page():
    """Page for exporting to Snowflake"""
    st.header("❄️ Export to Snowflake")
    
    if not st.session_state.graph_loaded:
        st.warning("⚠️ Please load an RDF/OWL file first")
        return
    
    st.markdown("""
    Export your RDF data to Snowflake as tables, views, or semantic views.
    This enables querying RDF data using SQL and integrating with your data warehouse.
    """)
    
    writer = SnowflakeWriter()
    
    # Connection section
    with st.expander("🔌 Snowflake Connection", expanded=True):
        st.info("When running in Snowflake Streamlit, connection is automatic. For local development, configure connection parameters.")
        
        if st.button("Connect to Snowflake"):
            try:
                writer.connect()
                st.session_state.snowflake_connected = True
                st.success("✅ Connected to Snowflake")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
    
    if not st.session_state.snowflake_connected:
        st.warning("⚠️ Please connect to Snowflake first")
        return
    
    # Export options
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Triples Table", "Entity View", "Semantic View", "Namespace Table"]
    )
    
    with tab1:
        st.subheader("Create Triples Table")
        st.markdown("Store all RDF triples in a Snowflake table")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            db_name = st.text_input("Database", value="RDF_DB")
        with col2:
            schema_name = st.text_input("Schema", value="PUBLIC")
        with col3:
            table_name = st.text_input("Table Name", value="RDF_TRIPLES")
        
        if st.button("Create Triples Table", type="primary"):
            try:
                with st.spinner("Creating table..."):
                    writer.rdf_to_triples_table(
                        st.session_state.rdf_reader.graph,
                        table_name, db_name, schema_name
                    )
                    st.success(f"✅ Created table {db_name}.{schema_name}.{table_name}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.subheader("Create Entity View")
        st.markdown("Create a view of entities with their properties")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            db_name_view = st.text_input("Database", value="RDF_DB", key="view_db")
        with col2:
            schema_name_view = st.text_input("Schema", value="PUBLIC", key="view_schema")
        with col3:
            view_name = st.text_input("View Name", value="RDF_ENTITIES")
        
        entity_type_filter = st.text_input(
            "Filter by Entity Type (optional)", 
            placeholder="http://www.w3.org/2002/07/owl#Class"
        )
        
        if st.button("Create Entity View", type="primary"):
            try:
                with st.spinner("Creating view..."):
                    entity_type = entity_type_filter if entity_type_filter else None
                    writer.create_entity_view(
                        st.session_state.rdf_reader.graph,
                        view_name, db_name_view, schema_name_view,
                        entity_type
                    )
                    st.success(f"✅ Created view {db_name_view}.{schema_name_view}.{view_name}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("Generate Semantic View")
        st.markdown("Generate SQL for a semantic view based on OWL class structure")
        
        classes = st.session_state.rdf_reader.get_classes()
        if classes:
            class_options = [f"{label} ({uri})" for uri, label in classes]
            selected_class = st.selectbox("Select OWL Class", class_options)
            
            if selected_class:
                # Extract URI from selection
                class_uri = selected_class.split("(")[1].rstrip(")")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    db_name_sem = st.text_input("Database", value="RDF_DB", key="sem_db")
                with col2:
                    schema_name_sem = st.text_input("Schema", value="PUBLIC", key="sem_schema")
                with col3:
                    view_name_sem = st.text_input("View Name", value="SEMANTIC_VIEW")
                
                if st.button("Generate Semantic View SQL", type="primary"):
                    try:
                        sql = writer.create_semantic_view(
                            st.session_state.rdf_reader.graph,
                            view_name_sem, db_name_sem, schema_name_sem,
                            class_uri
                        )
                        st.success("✅ Generated SQL")
                        st.code(sql, language="sql")
                        
                        st.download_button(
                            "📥 Download SQL",
                            data=sql,
                            file_name=f"{view_name_sem}.sql",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("No OWL classes found in the graph")
    
    with tab4:
        st.subheader("Create Namespace Table")
        st.markdown("Store namespace prefixes and URIs")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            db_name_ns = st.text_input("Database", value="RDF_DB", key="ns_db")
        with col2:
            schema_name_ns = st.text_input("Schema", value="PUBLIC", key="ns_schema")
        with col3:
            table_name_ns = st.text_input("Table Name", value="RDF_NAMESPACES")
        
        if st.button("Create Namespace Table", type="primary"):
            try:
                with st.spinner("Creating table..."):
                    writer.create_namespace_table(
                        st.session_state.rdf_reader.graph,
                        table_name_ns, db_name_ns, schema_name_ns
                    )
                    st.success(f"✅ Created table {db_name_ns}.{schema_name_ns}.{table_name_ns}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def query_page():
    """Page for querying RDF data"""
    st.header("🔍 Query RDF Data")
    
    if not st.session_state.graph_loaded:
        st.warning("⚠️ Please load an RDF/OWL file first")
        return
    
    st.markdown("""
    Execute SPARQL queries on your loaded RDF graph.
    """)
    
    tab1, tab2 = st.tabs(["SPARQL Query", "Example Queries"])
    
    with tab1:
        st.subheader("Execute SPARQL Query")
        
        query = st.text_area(
            "Enter SPARQL Query",
            height=200,
            placeholder="""SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object .
}
LIMIT 10"""
        )
        
        if st.button("Execute Query", type="primary"):
            if query:
                try:
                    with st.spinner("Executing query..."):
                        results = st.session_state.rdf_reader.query_sparql(query)
                        
                        st.success(f"✅ Query executed. {len(results)} results returned.")
                        st.dataframe(results, use_container_width=True)
                        
                        # Download option
                        csv = results.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"❌ Query error: {str(e)}")
            else:
                st.warning("Please enter a SPARQL query")
    
    with tab2:
        st.subheader("Example SPARQL Queries")
        
        examples = {
            "Get All Triples (Limited)": """SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object .
}
LIMIT 100""",
            
            "Get All Classes": """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?class ?label
WHERE {
  ?class rdf:type owl:Class .
  OPTIONAL { ?class rdfs:label ?label }
}""",
            
            "Get All Properties": """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?property ?label ?type
WHERE {
  {?property rdf:type owl:ObjectProperty}
  UNION
  {?property rdf:type owl:DatatypeProperty}
  UNION
  {?property rdf:type rdf:Property}
  BIND(COALESCE(
    IF(?property rdf:type owl:ObjectProperty, "ObjectProperty", ""),
    IF(?property rdf:type owl:DatatypeProperty, "DatatypeProperty", ""),
    "Property"
  ) AS ?type)
  OPTIONAL { ?property rdfs:label ?label }
}""",
            
            "Get Resource with Details": """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?resource ?predicate ?value
WHERE {
  ?resource ?predicate ?value .
  ?resource rdfs:label ?label .
}
LIMIT 50"""
        }
        
        selected_example = st.selectbox("Select Example Query", list(examples.keys()))
        
        if selected_example:
            st.code(examples[selected_example], language="sparql")
            
            if st.button("Run This Example", type="secondary"):
                try:
                    with st.spinner("Executing query..."):
                        results = st.session_state.rdf_reader.query_sparql(examples[selected_example])
                        st.success(f"✅ Query executed. {len(results)} results returned.")
                        st.dataframe(results, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Query error: {str(e)}")


if __name__ == "__main__":
    main()

