# 🔗 RDF/OWL Visualizer & Editor for Snowflake

A comprehensive Streamlit application designed to run in Snowflake that provides complete functionality for working with RDF (Resource Description Framework) and OWL (Web Ontology Language) data.

## 🌟 Features

### 1. **Reader** 📁
- Load RDF/OWL from multiple sources:
  - File upload (local files)
  - URL loading (remote ontologies)
  - Sample data generation
- Support for multiple RDF formats:
  - RDF/XML
  - Turtle (TTL)
  - N-Triples (NT)
  - N3
  - JSON-LD
  - TriG
  - NQuads

### 2. **Visualizer** 📊
- **Interactive Graph Visualization**
  - Plotly-based interactive graphs
  - Network graph visualization with streamlit-agraph
  - Configurable node limits for performance
- **Graph Statistics**
  - Node and edge counts
  - Graph density metrics
  - Centrality analysis
- **Entity Browser**
  - Browse OWL Classes
  - Explore Properties (Object, Datatype, Annotation)
  - View Individuals/Instances
- **Triple Explorer**
  - View all RDF triples in tabular format
  - Filter and search capabilities
  - Export to CSV

### 3. **Annotator** ✏️
- **Add/Remove Triples**
  - Create new RDF statements
  - Remove existing triples
  - Support for both URIs and literals
- **Metadata Management**
  - Add RDFS labels (with language support)
  - Add RDFS comments
  - Annotation statistics
- **Graph Editing**
  - Update existing triples
  - Merge multiple graphs

### 4. **Converter** 🔄
- Convert between all supported RDF formats
- Live preview of converted output
- Download converted files
- Syntax validation

### 5. **Snowflake Integration** ❄️
- **Triples Table**
  - Store all RDF triples with metadata
  - Includes subject, predicate, object, type, datatype, and language
- **Entity Views**
  - Create denormalized views of entities
  - Optional filtering by entity type
  - Property columns dynamically generated
- **Semantic Views**
  - Generate SQL for semantic views based on OWL classes
  - Align with Snowflake's semantic modeling capabilities
  - Downloadable SQL scripts
- **Namespace Table**
  - Store namespace prefix mappings
  - Enable compact URI representation

### 6. **Query Engine** 🔍
- Full SPARQL query support
- Pre-built example queries
- Result export to CSV
- Query history and templates

## 📋 Requirements

### Core Requirements
- Python 3.8 or higher
- streamlit, rdflib, networkx, plotly, pandas
- Snowflake account (for Snowflake deployment only)

### Optional Dependencies
- `streamlit-agraph` - For network graph visualization (not required; app uses Plotly by default)
- `pyvis` - Alternative visualization (not currently used)

**Note:** The application works perfectly without optional dependencies. Plotly provides excellent interactive visualization for all graph needs.

See `requirements.txt` for full dependency list.

## 🚀 Installation

### For Snowflake Deployment

1. **Upload to Snowflake**
   ```sql
   -- Create a stage for the application
   CREATE STAGE IF NOT EXISTS RDF_APP_STAGE;
   
   -- Upload files
   PUT file:///path/to/streamlit_app.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
   PUT file:///path/to/rdf_reader.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
   PUT file:///path/to/graph_visualizer.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
   PUT file:///path/to/rdf_converter.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
   PUT file:///path/to/snowflake_writer.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
   PUT file:///path/to/requirements.txt @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
   ```

2. **Create Streamlit Application**
   ```sql
   CREATE STREAMLIT RDF_OWL_VISUALIZER
   ROOT_LOCATION = '@RDF_APP_STAGE'
   MAIN_FILE = 'streamlit_app.py'
   QUERY_WAREHOUSE = YOUR_WAREHOUSE;
   ```

3. **Access the Application**
   - Navigate to Apps > Streamlit in Snowflake UI
   - Click on RDF_OWL_VISUALIZER

### For Local Development

1. **Clone or download the repository**
   ```bash
   cd RDFOwlVisualizerAndEditor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access the application**
   - Open browser to `http://localhost:8501`

## 📖 Usage Guide

### Loading RDF Data

1. Navigate to **📁 Load RDF/OWL** page
2. Choose your input method:
   - **Upload File**: Select a local RDF file
   - **Load from URL**: Enter a URL to a remote ontology
   - **Sample Data**: Generate a test ontology
3. Select the appropriate RDF format
4. Click the load button

### Visualizing Graphs

1. Navigate to **📊 Visualize Graph** page
2. Choose visualization type:
   - **Plotly Interactive**: Best for exploration
   - **Network Graph**: Force-directed layout
3. Adjust the node limit slider for performance
4. Explore tabs:
   - **Interactive Graph**: Visual representation
   - **Graph Statistics**: Metrics and analysis
   - **Browse Entities**: Explore classes, properties, individuals
   - **Explore Triples**: View and filter all triples

### Annotating and Editing

1. Navigate to **✏️ Annotate & Edit** page
2. Available operations:
   - **Add Triple**: Create new RDF statements
   - **Remove Triple**: Delete existing statements
   - **Add Metadata**: Add labels and comments
   - **Statistics**: View annotation metrics

### Converting Formats

1. Navigate to **🔄 Convert Formats** page
2. Select target format from dropdown
3. Click **Convert**
4. Preview the output
5. Download converted file

### Exporting to Snowflake

1. Navigate to **❄️ Export to Snowflake** page
2. Click **Connect to Snowflake** (automatic in Snowflake Streamlit)
3. Choose export type:
   - **Triples Table**: Store raw RDF triples
   - **Entity View**: Create denormalized entity view
   - **Semantic View**: Generate semantic view SQL
   - **Namespace Table**: Store namespace mappings
4. Configure database, schema, and table/view names
5. Click the create button

### Querying Data

1. Navigate to **🔍 Query Data** page
2. Enter a SPARQL query or select an example
3. Click **Execute Query**
4. View results in tabular format
5. Download results as CSV

## 🏗️ Architecture

### Module Structure

```
RDFOwlVisualizerAndEditor/
├── streamlit_app.py          # Main Streamlit application
├── rdf_reader.py              # RDF/OWL reading and parsing
├── graph_visualizer.py        # Graph visualization
├── rdf_converter.py           # Format conversion and annotation
├── snowflake_writer.py        # Snowflake integration
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

### Data Flow

```
Input (File/URL) → RDFReader → RDFLib Graph
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
            GraphVisualizer  RDFConverter  RDFAnnotator
                    ↓               ↓               ↓
            Visualization    Format Output    Modified Graph
                                                    ↓
                                            SnowflakeWriter
                                                    ↓
                                    Snowflake Tables/Views
```

## 🔧 Configuration

### Snowflake Connection

When running in Snowflake Streamlit, the connection is automatic. For local development, you can configure connection parameters in `snowflake_writer.py`.

### Performance Tuning

- Adjust `max_nodes` slider in visualization for large graphs
- Use filtering in triple explorer for large datasets
- Consider creating entity views instead of querying raw triples

## 📊 Example Use Cases

### 1. Ontology Visualization
Load a domain ontology (e.g., FOAF, Dublin Core) and explore its structure visually.

### 2. Knowledge Graph Management
Import knowledge graphs, add annotations, and export to Snowflake for analytics.

### 3. Data Integration
Convert RDF data between formats for interoperability with different systems.

### 4. Semantic Data Warehouse
Create semantic views in Snowflake that map to OWL classes for business intelligence.

### 5. Metadata Management
Store and manage metadata about your data assets using RDF in Snowflake.

## 🐛 Troubleshooting

### Common Issues

**Issue**: Large graphs are slow to visualize
- **Solution**: Use the node limit slider to reduce displayed nodes
- **Solution**: Filter data before visualization

**Issue**: SPARQL query timeout
- **Solution**: Add LIMIT clause to queries
- **Solution**: Use more specific WHERE clauses

**Issue**: File format not recognized
- **Solution**: Ensure correct format is selected in dropdown
- **Solution**: Validate file format using external RDF validator

**Issue**: Snowflake connection fails
- **Solution**: Verify you're running in Snowflake Streamlit environment
- **Solution**: Check warehouse is running and accessible

## 🔐 Security Considerations

- Validate uploaded files before processing
- Sanitize SPARQL queries to prevent injection
- Use appropriate Snowflake role-based access controls
- Limit file upload sizes in production

## 🚦 Performance Best Practices

1. **Large Graphs**: Use filtering and sampling
2. **Batch Operations**: Export multiple resources at once
3. **Indexing**: Create indexes on Snowflake tables for better query performance
4. **Caching**: Session state caching reduces repeated parsing

## 📝 License

This project is provided as-is for use in Snowflake environments.

## 🤝 Contributing

To contribute:
1. Test changes locally
2. Ensure all modules work in Snowflake environment
3. Update documentation for new features
4. Follow Python PEP 8 style guidelines

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review Snowflake Streamlit documentation
- Consult RDFLib documentation for RDF-specific questions

## 🎯 Future Enhancements

- [ ] SHACL validation support
- [ ] Reasoning engine integration
- [ ] Graph diff and merge capabilities
- [ ] Export to additional formats (GraphML, Cypher)
- [ ] Custom visualization layouts
- [ ] Batch file processing
- [ ] Version control for ontologies
- [ ] Collaborative editing features

## 📚 References

- [RDFLib Documentation](https://rdflib.readthedocs.io/)
- [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

---

Built with ❤️ for the Snowflake and Semantic Web communities

