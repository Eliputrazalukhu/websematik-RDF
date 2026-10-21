# 🔧 Troubleshooting Guide

Common issues and solutions for the RDF/OWL Visualizer.

## 📦 Installation Issues

### Issue: ModuleNotFoundError: No module named 'streamlit_agraph'

**Symptoms:**
```python
ModuleNotFoundError: No module named 'streamlit_agraph'
```

**Solution 1: Use Plotly Visualization (Recommended)**

The application will automatically fall back to Plotly visualization, which provides excellent interactive graphs without requiring `streamlit-agraph`.

**What happens:**
- The app detects that `streamlit-agraph` is not installed
- Automatically uses Plotly visualization instead
- You'll see a warning message in the UI
- All functionality works normally

**Solution 2: Install streamlit-agraph (Optional)**

If you specifically want the network graph visualization:

```bash
pip install streamlit-agraph
```

**Note:** `streamlit-agraph` is optional and not required for core functionality. Plotly provides excellent visualization capabilities.

### Issue: Other missing dependencies

**Symptoms:**
```python
ModuleNotFoundError: No module named 'xyz'
```

**Solution:**

Install all core dependencies:
```bash
pip install -r requirements.txt
```

Or install specific missing package:
```bash
pip install <package-name>
```

## 🗄️ Snowflake Connection Issues

### Issue: Connection failed

**Symptoms:**
- Cannot connect to Snowflake
- Authentication errors

**Solutions:**

1. **Verify credentials:**
   ```python
   # Check your account, user, password
   ```

2. **Check warehouse status:**
   ```sql
   SHOW WAREHOUSES;
   ALTER WAREHOUSE <name> RESUME;
   ```

3. **Verify permissions:**
   ```sql
   SHOW GRANTS TO ROLE <your_role>;
   ```

### Issue: Running locally instead of Snowflake

**Symptoms:**
- App tries to connect to Snowflake when running locally

**Solution:**

The app is designed to work both locally and in Snowflake:
- **In Snowflake**: Connection is automatic
- **Locally**: Snowflake features will show connection requirements

For local development without Snowflake features:
- All read, visualize, annotate, and convert features work without Snowflake
- Only the "Export to Snowflake" page requires connection

## 🧪 Test Failures

### Issue: Tests fail with import errors

**Solution:**

Install test dependencies:
```bash
pip install pytest pytest-cov
```

### Issue: streamlit-agraph tests skipped

**Expected Behavior:**

If `streamlit-agraph` is not installed, related tests are automatically skipped:
```
test_visualize_with_agraph SKIPPED (streamlit-agraph not installed)
```

This is normal and expected. The test suite handles optional dependencies gracefully.

### Issue: Snowflake tests fail

**Solution:**

Skip Snowflake-dependent tests:
```bash
pytest -m "not requires_snowflake"
```

## 📊 Visualization Issues

### Issue: Graph visualization is slow

**Solutions:**

1. **Reduce node limit:**
   - Use the slider to limit nodes (try 20-50)

2. **Filter your data:**
   - Load smaller ontologies for testing
   - Use SPARQL queries to filter data

3. **Use Plotly instead of network graph:**
   - Plotly is faster for large graphs

### Issue: Blank visualization

**Symptoms:**
- Graph area is empty
- No error message

**Solutions:**

1. **Check data is loaded:**
   - Look at statistics in sidebar
   - Verify "Total Triples" > 0

2. **Try different visualization:**
   - Switch between Plotly and Network Graph
   - Check other tabs (Browse Entities, Explore Triples)

## 📁 File Loading Issues

### Issue: Cannot load RDF file

**Symptoms:**
- Error message when uploading file
- "Error parsing RDF" message

**Solutions:**

1. **Check file format:**
   - Ensure selected format matches file content
   - Try auto-detect by trying different formats

2. **Validate file:**
   - Use an online RDF validator
   - Check for syntax errors

3. **Try different format:**
   - Convert file to Turtle format (usually more forgiving)
   - Try loading sample data first

### Issue: URL loading fails

**Symptoms:**
- Cannot load from URL
- Timeout or connection error

**Solutions:**

1. **Check URL accessibility:**
   - Try opening URL in browser
   - Verify it's publicly accessible

2. **Check format:**
   - Ensure correct format is selected
   - Some servers require specific format

3. **Try local file:**
   - Download file first
   - Upload as file instead of URL

## 🔄 Format Conversion Issues

### Issue: Conversion fails or produces invalid output

**Solutions:**

1. **Validate source data:**
   - Ensure source is valid RDF
   - Try with sample data first

2. **Try different target format:**
   - Some formats are more permissive
   - Turtle usually works well

3. **Check for special characters:**
   - Some formats have encoding issues
   - Try simpler data first

## ⚡ Performance Issues

### Issue: Application is slow

**Solutions:**

1. **For large ontologies:**
   ```python
   # Use node limits
   max_nodes = 50  # Start small
   
   # Filter data with SPARQL
   query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1000"
   ```

2. **Clear browser cache:**
   - Refresh page
   - Clear Streamlit cache

3. **Check system resources:**
   - Monitor RAM usage
   - Close other applications

### Issue: Queries are slow

**Solutions:**

1. **Add LIMIT clauses:**
   ```sparql
   SELECT ?s ?p ?o 
   WHERE { ?s ?p ?o }
   LIMIT 100
   ```

2. **Use specific predicates:**
   ```sparql
   SELECT ?s ?label
   WHERE { 
     ?s rdfs:label ?label 
   }
   ```

3. **Use views (in Snowflake):**
   ```sql
   SELECT * FROM V_RDF_CLASSES;  -- Pre-optimized
   ```

## 🐛 Common Errors

### Error: "No graph loaded"

**Solution:**
- Go to "📁 Load RDF/OWL" page
- Load a file, URL, or create sample data

### Error: "Cannot connect to Snowflake"

**Solution:**
- Check if running in Snowflake environment
- For local development, Snowflake export features won't work

### Error: "Invalid SPARQL query"

**Solution:**
1. **Check syntax:**
   ```sparql
   PREFIX ex: <http://example.org/>
   SELECT ?s ?p ?o
   WHERE {
     ?s ?p ?o
   }
   ```

2. **Use example queries:**
   - Go to Query Data tab
   - Try example queries first

### Error: "File too large"

**Solution:**
1. **Split the file:**
   - Process in smaller chunks

2. **Use streaming:**
   - Load directly to Snowflake
   - Process with SQL

3. **Filter first:**
   - Extract subset of ontology
   - Focus on specific classes

## 💾 Memory Issues

### Issue: Out of memory errors

**Solutions:**

1. **Reduce data size:**
   - Use node limits
   - Filter with SPARQL
   - Load smaller ontologies

2. **Increase available memory:**
   - Close other applications
   - Use larger Snowflake warehouse

3. **Process in batches:**
   - Export to Snowflake
   - Query in smaller chunks

## 🔐 Permission Issues

### Issue: Cannot create tables in Snowflake

**Solution:**

Check and grant permissions:
```sql
-- Check current role
SELECT CURRENT_ROLE();

-- Grant permissions
GRANT CREATE TABLE ON SCHEMA RDF_DB.PUBLIC TO ROLE <your_role>;
GRANT CREATE VIEW ON SCHEMA RDF_DB.PUBLIC TO ROLE <your_role>;
```

### Issue: Cannot access uploaded files

**Solution:**

Check stage permissions:
```sql
GRANT READ, WRITE ON STAGE RDF_APP_STAGE TO ROLE <your_role>;
```

## 📝 Logging and Debugging

### Enable Debug Mode

```python
# In streamlit_app.py (for local development)
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Streamlit Logs

```bash
streamlit run streamlit_app.py --logger.level=debug
```

### Check Browser Console

- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

## 🆘 Getting Help

### Before Asking for Help

1. **Check this guide** - Many issues are covered here
2. **Review documentation:**
   - README.md
   - QUICKSTART.md
   - DEPLOYMENT.md
3. **Try with sample data** - Isolate if issue is with your data
4. **Check test suite** - Run tests to verify installation

### Providing Information

When reporting issues, include:
- Error message (full traceback)
- Python version: `python --version`
- Package versions: `pip list`
- Steps to reproduce
- Sample data if possible

### Useful Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(streamlit|rdflib|networkx|plotly)"

# Run tests
pytest -v

# Check for dependency issues
pip check

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## ✅ Quick Fixes Checklist

- [ ] Reinstall dependencies: `pip install -r requirements.txt`
- [ ] Clear browser cache
- [ ] Restart Streamlit app
- [ ] Try with sample data
- [ ] Check error messages in browser console
- [ ] Verify file format matches selection
- [ ] Reduce node limit for visualization
- [ ] Use Plotly instead of network graph
- [ ] Skip optional dependency tests
- [ ] Check Snowflake connection (if using)

## 🔄 Reset and Start Fresh

If all else fails:

```bash
# 1. Clean Python environment
pip uninstall -y -r <(pip freeze)

# 2. Reinstall from scratch
pip install -r requirements.txt

# 3. Run tests
pytest

# 4. Start app
streamlit run streamlit_app.py
```

---

**Still having issues?** 

Review the main documentation:
- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started
- [TESTING.md](TESTING.md) - Testing guide

**Optional Dependencies:**

Remember that `streamlit-agraph` is optional. The application works perfectly fine without it, using Plotly for all visualizations.

