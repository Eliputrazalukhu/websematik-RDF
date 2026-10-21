# 🚀 Quick Start Guide

## For Snowflake Users (Recommended)

### Step 1: Prepare Your Snowflake Environment

1. Open a Snowflake worksheet
2. Run the setup script:
   ```sql
   -- Execute snowflake_setup.sql
   ```

### Step 2: Upload Application Files

Using SnowSQL:
```bash
snowsql -a your_account -u your_username

# Once connected:
USE DATABASE RDF_DB;
USE SCHEMA PUBLIC;

PUT file://streamlit_app.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://rdf_reader.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://graph_visualizer.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://rdf_converter.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://snowflake_writer.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://requirements.txt @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

Or use Snowflake UI:
- Navigate to: Data → Databases → RDF_DB → PUBLIC → Stages → RDF_APP_STAGE
- Click "Upload Files" and select all 6 files

### Step 3: Create the Streamlit App

```sql
CREATE STREAMLIT RDF_OWL_VISUALIZER
    ROOT_LOCATION = '@RDF_DB.PUBLIC.RDF_APP_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'RDF_WAREHOUSE';
```

### Step 4: Launch the Application

1. In Snowflake UI, go to: **Apps** → **Streamlit**
2. Find **RDF_OWL_VISUALIZER**
3. Click to open

## For Local Development

### Step 1: Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
streamlit run streamlit_app.py
```

### Step 3: Open in Browser

The application will automatically open at `http://localhost:8501`

## First Time Usage

### 1. Load Sample Data

- Go to **📁 Load RDF/OWL** page
- Click **Sample Data** tab
- Click **Create Sample Graph**
- ✅ You now have data loaded!

### 2. Visualize the Graph

- Go to **📊 Visualize Graph** page
- Choose **Plotly (Interactive)** visualization
- Explore the interactive graph
- Check out **Graph Statistics** tab

### 3. Try a SPARQL Query

- Go to **🔍 Query Data** page
- Click **Example Queries** tab
- Select "Get All Classes"
- Click **Run This Example**
- View the results

### 4. Export to Snowflake (Snowflake version only)

- Go to **❄️ Export to Snowflake** page
- Click **Connect to Snowflake**
- Go to **Triples Table** tab
- Click **Create Triples Table**
- ✅ Your RDF data is now in Snowflake!

## Common Workflows

### Loading Your Own Ontology

1. **From File:**
   - Go to **📁 Load RDF/OWL**
   - Select format (e.g., Turtle, RDF/XML)
   - Upload your file
   - Click **Load File**

2. **From URL:**
   - Go to **📁 Load RDF/OWL** → **Load from URL** tab
   - Enter ontology URL (e.g., `http://xmlns.com/foaf/spec/index.rdf`)
   - Select format
   - Click **Load from URL**

### Annotating Your Data

1. Go to **✏️ Annotate & Edit**
2. To add a label:
   - Enter Resource URI
   - Enter Label text
   - (Optional) Add language code
   - Click **Add Label**

3. To add a triple:
   - Enter Subject, Predicate, Object
   - Check if Object is literal
   - Click **Add Triple**

### Converting Formats

1. Load your RDF data
2. Go to **🔄 Convert Formats**
3. Select target format
4. Click **🔄 Convert**
5. Preview and download

### Creating Snowflake Views

1. Export triples to Snowflake first
2. Go to **❄️ Export to Snowflake** → **Entity View**
3. Configure database/schema/view name
4. Click **Create Entity View**
5. Query the view in Snowflake:
   ```sql
   SELECT * FROM RDF_DB.PUBLIC.RDF_ENTITIES;
   ```

## Example Ontologies to Try

### Public Ontologies (Load from URL)

1. **Friend of a Friend (FOAF)**
   - URL: `http://xmlns.com/foaf/spec/index.rdf`
   - Format: RDF/XML

2. **Dublin Core Terms**
   - URL: `https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl`
   - Format: Turtle

3. **Schema.org**
   - URL: `https://schema.org/version/latest/schemaorg-current-https.ttl`
   - Format: Turtle
   - Note: Large file, may take time to load

## Troubleshooting

### "No graph loaded" Warning

**Solution:** Load an RDF/OWL file first from the **📁 Load RDF/OWL** page

### Visualization is Slow

**Solutions:**
- Reduce the "Maximum nodes" slider
- Use sample data for testing
- Filter your data before visualizing

### SPARQL Query Returns No Results

**Solutions:**
- Check your query syntax
- Try an example query first
- Verify data is loaded (check Graph Statistics)

### Snowflake Connection Failed

**Solutions:**
- Ensure you're running in Snowflake Streamlit (not local)
- Verify warehouse is active
- Check database/schema permissions

### File Upload Fails

**Solutions:**
- Check file format matches selected format
- Ensure file is valid RDF (test with online validator)
- Try with sample data first

## Performance Tips

1. **Large Files:** Load incrementally or filter before upload
2. **Visualization:** Use node limit slider (start with 50 nodes)
3. **Queries:** Add LIMIT clauses to SPARQL queries
4. **Snowflake:** Create indexes on frequently queried columns

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed features
- 🔧 Review [snowflake_setup.sql](snowflake_setup.sql) for advanced setup
- 🌐 Explore public ontologies and knowledge graphs
- 💡 Build your own domain ontology

## Getting Help

- Check module documentation in each Python file
- Review SPARQL query examples in the Query tab
- Consult [RDFLib documentation](https://rdflib.readthedocs.io/)
- See [Snowflake Streamlit docs](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

---

**Ready to explore the Semantic Web? Start with the sample data and experiment!** 🎉

