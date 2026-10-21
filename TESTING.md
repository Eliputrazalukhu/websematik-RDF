## 🧪 Testing Guide for RDF/OWL Visualizer

Comprehensive testing documentation for the RDF/OWL Visualizer and Editor.

## 📋 Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests](#running-tests)
3. [Test Coverage](#test-coverage)
4. [SQL Testing](#sql-testing)
5. [Manual Testing](#manual-testing)
6. [Performance Testing](#performance-testing)

## 🗂️ Test Structure

### Python Tests

```
RDFOwlVisualizerAndEditor/
├── test_rdf_reader.py          # Unit tests for RDF reader
├── test_graph_visualizer.py    # Unit tests for graph visualizer
├── test_rdf_converter.py       # Unit tests for converter & annotator
├── test_integration.py         # Integration tests
└── pytest.ini                  # Pytest configuration
```

### SQL Tests

```
sql/
├── queries.sql          # Query library (30+ queries)
├── procedures.sql       # Stored procedures & functions
├── views.sql           # 20+ pre-defined views
└── test_data.sql       # Test data and verification queries
```

## 🚀 Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term
```

### Run Specific Test Files

```bash
# Test RDF reader only
pytest test_rdf_reader.py -v

# Test graph visualizer only
pytest test_graph_visualizer.py -v

# Test converter only
pytest test_rdf_converter.py -v

# Test integration only
pytest test_integration.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pytest test_rdf_reader.py::TestRDFReader -v

# Run a specific test method
pytest test_rdf_reader.py::TestRDFReader::test_load_from_file_turtle -v
```

### Run Tests with Markers

```bash
# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run tests that don't require Snowflake
pytest -m "not requires_snowflake"
```

## 📊 Test Coverage

### Current Test Coverage

- **`rdf_reader.py`**: 95%+ coverage
  - File loading (all formats)
  - Statistics generation
  - SPARQL queries
  - Entity extraction
  - Edge cases

- **`graph_visualizer.py`**: 90%+ coverage
  - Graph construction
  - Visualizations (Plotly, agraph)
  - Statistics
  - Centrality analysis
  - Path finding

- **`rdf_converter.py`**: 95%+ coverage
  - Format conversions (all 7 formats)
  - Syntax validation
  - Triple manipulation
  - Annotations
  - Edge cases

- **Integration Tests**: 85%+ coverage
  - Complete workflows
  - Module interactions
  - Data flow
  - Error handling

### Generate Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open the report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Generate Terminal Coverage Report

```bash
pytest --cov=. --cov-report=term-missing
```

## 🗄️ SQL Testing

### Setup Test Environment

```sql
-- 1. Run setup script
USE DATABASE RDF_DB;
USE SCHEMA PUBLIC;

-- 2. Load test data
@sql/test_data.sql
```

### Verify Test Data

```sql
-- Check test triple count
SELECT COUNT(*) FROM RDF_TRIPLES 
WHERE SUBJECT LIKE 'http://test.example.org/%';

-- Should return ~50-60 triples
```

### Test Stored Procedures

```sql
-- Test 1: Validate RDF triples
CALL VALIDATE_RDF_TRIPLES();

-- Test 2: Get resource details
CALL GET_RESOURCE_DETAILS('http://test.example.org/John');

-- Test 3: Calculate statistics
CALL CALCULATE_GRAPH_STATISTICS();

-- Test 4: Analyze property usage
CALL ANALYZE_PROPERTY_USAGE();

-- Test 5: Find path between resources
CALL FIND_PATH_BETWEEN_RESOURCES(
    'http://test.example.org/John',
    'http://test.example.org/TechCorp',
    3
);
```

### Test Functions

```sql
-- Test 1: Extract local name
SELECT GET_LOCAL_NAME('http://test.example.org/Person');
-- Expected: 'Person'

-- Test 2: Get namespace
SELECT GET_NAMESPACE('http://test.example.org/Person');
-- Expected: 'http://test.example.org/'

-- Test 3: Check resource existence
SELECT RESOURCE_EXISTS('http://test.example.org/John');
-- Expected: TRUE

-- Test 4: Count properties
SELECT COUNT_RESOURCE_PROPERTIES('http://test.example.org/John');
-- Expected: > 0

-- Test 5: Get label
SELECT GET_RESOURCE_LABEL('http://test.example.org/John');
-- Expected: 'John Smith'
```

### Test Views

```sql
-- Test 1: View all classes
SELECT * FROM V_RDF_CLASSES;

-- Test 2: View all properties
SELECT * FROM V_RDF_PROPERTIES;

-- Test 3: View instances
SELECT * FROM V_RDF_INSTANCES WHERE CLASS_NAME = 'Person';

-- Test 4: View class hierarchy
SELECT * FROM V_CLASS_HIERARCHY;

-- Test 5: View relationships
SELECT * FROM V_RDF_RELATIONSHIPS 
WHERE SOURCE_URI LIKE 'http://test.example.org/%'
LIMIT 20;

-- Test 6: View statistics
SELECT * FROM V_PREDICATE_STATISTICS;

-- Test 7: View resource degree (connections)
SELECT * FROM V_RESOURCE_DEGREE 
WHERE RESOURCE_URI LIKE 'http://test.example.org/%'
ORDER BY TOTAL_DEGREE DESC;

-- Test 8: View unlabeled resources
SELECT * FROM V_UNLABELED_RESOURCES 
WHERE RESOURCE_URI LIKE 'http://test.example.org/%';

-- Test 9: View graph summary
SELECT * FROM V_GRAPH_SUMMARY;
```

### Test Queries

Run queries from `sql/queries.sql`:

```sql
-- Test basic queries (Queries 1-4)
-- See sql/queries.sql for full query text

-- Test class queries (Queries 5-7)
-- Test property queries (Queries 8-10)
-- Test instance queries (Queries 11-13)
-- Test relationship queries (Queries 14-16)
-- Test statistics queries (Queries 22-24)
```

## 🔧 Manual Testing

### Test Streamlit Application

#### 1. Start Application

```bash
streamlit run streamlit_app.py
```

#### 2. Test Load Module

- [ ] Upload sample_ontology.ttl
- [ ] Load from URL (try FOAF: http://xmlns.com/foaf/spec/index.rdf)
- [ ] Create sample data
- [ ] Verify statistics display correctly

#### 3. Test Visualize Module

- [ ] Generate Plotly visualization
- [ ] Generate network graph visualization
- [ ] Adjust node limit slider
- [ ] Browse classes
- [ ] Browse properties
- [ ] Browse individuals
- [ ] Explore triples with filtering
- [ ] Download triples as CSV

#### 4. Test Annotate Module

- [ ] Add a new triple (URI object)
- [ ] Add a new triple (literal object)
- [ ] Remove a triple
- [ ] Add a label
- [ ] Add a comment
- [ ] Add multi-language labels
- [ ] View annotation statistics

#### 5. Test Convert Module

- [ ] Convert to Turtle
- [ ] Convert to RDF/XML
- [ ] Convert to N-Triples
- [ ] Convert to JSON-LD
- [ ] Download converted file
- [ ] Verify preview displays

#### 6. Test Snowflake Export

**Note**: Requires Snowflake connection

- [ ] Connect to Snowflake
- [ ] Create triples table
- [ ] Create entity view
- [ ] Generate semantic view SQL
- [ ] Create namespace table
- [ ] Verify data in Snowflake

#### 7. Test Query Module

- [ ] Execute custom SPARQL query
- [ ] Run example queries
- [ ] Download results as CSV
- [ ] Test query with no results
- [ ] Test invalid query (should show error)

## ⚡ Performance Testing

### Small Dataset (< 100 triples)

```python
import time
from rdf_reader import RDFReader

reader = RDFReader()
start = time.time()
reader.load_from_file(small_data, 'Turtle')
print(f"Load time: {time.time() - start:.3f}s")

# Expected: < 0.1s
```

### Medium Dataset (100-1,000 triples)

```python
# Test with medium dataset
start = time.time()
reader.load_from_file(medium_data, 'Turtle')
print(f"Load time: {time.time() - start:.3f}s")

# Expected: < 1s
```

### Large Dataset (> 1,000 triples)

```python
# Test with large dataset
start = time.time()
reader.load_from_file(large_data, 'Turtle')
print(f"Load time: {time.time() - start:.3f}s")

# Test visualization performance
visualizer = GraphVisualizer(reader.graph)
start = time.time()
fig = visualizer.visualize_with_plotly(max_nodes=100)
print(f"Visualization time: {time.time() - start:.3f}s")

# Expected: < 5s
```

### SQL Query Performance

```sql
-- Test query performance
SET query_tag = 'performance_test';

-- Query 1: Count triples (should be fast)
SELECT COUNT(*) FROM RDF_TRIPLES;

-- Query 2: Complex join (test with EXPLAIN)
EXPLAIN
SELECT * FROM V_RDF_RELATIONSHIPS
WHERE SOURCE_URI LIKE '%Person%';

-- Query 3: Aggregation (test with timing)
SELECT 
    PREDICATE,
    COUNT(*) as CNT
FROM RDF_TRIPLES
GROUP BY PREDICATE
ORDER BY CNT DESC;

-- Check query history
SELECT 
    QUERY_TEXT,
    EXECUTION_TIME,
    ROWS_PRODUCED
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_TAG = 'performance_test'
ORDER BY START_TIME DESC;
```

## 🐛 Debugging Tests

### Run Tests with Debug Output

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb
```

### Debug Specific Test

```python
# Add to test file
import pytest

@pytest.mark.skip(reason="Debugging")
def test_my_function():
    # Your test code
    import pdb; pdb.set_trace()  # Breakpoint
```

## 📝 Test Checklist

### Before Committing

- [ ] All tests pass: `pytest -v`
- [ ] No linting errors
- [ ] Code coverage > 85%
- [ ] SQL tests verified in Snowflake
- [ ] Manual tests on key features
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)

### Before Release

- [ ] Full test suite passes
- [ ] Integration tests pass
- [ ] Performance tests acceptable
- [ ] SQL scripts tested in clean environment
- [ ] Sample data loads correctly
- [ ] All views and procedures work
- [ ] Deployment tested in Snowflake

## 🔬 Advanced Testing

### Test with Real Ontologies

```python
# Test with FOAF
reader = RDFReader()
reader.load_from_url('http://xmlns.com/foaf/spec/index.rdf', 'RDF/XML')

# Test with Dublin Core
reader.load_from_url('https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl', 'Turtle')

# Run full workflow
visualizer = GraphVisualizer(reader.graph)
converter = RDFConverter(reader.graph)
```

### Stress Testing

```python
# Create large graph
from rdflib import Graph, URIRef, Literal

g = Graph()
for i in range(10000):
    g.add((
        URIRef(f"http://test.org/s{i}"),
        URIRef(f"http://test.org/p"),
        Literal(f"Object {i}")
    ))

# Test performance
reader = RDFReader()
reader.graph = g

# Measure operations
import time

start = time.time()
stats = reader.get_stats()
print(f"Stats: {time.time() - start:.3f}s")

start = time.time()
df = reader.get_triples_as_dataframe()
print(f"DataFrame: {time.time() - start:.3f}s")
```

## 📊 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 🆘 Troubleshooting

### Common Issues

**Issue**: Tests fail with import errors
```bash
# Solution: Install in development mode
pip install -e .
```

**Issue**: Snowflake connection fails in tests
```bash
# Solution: Skip Snowflake tests
pytest -m "not requires_snowflake"
```

**Issue**: Performance tests timeout
```bash
# Solution: Increase timeout
pytest --timeout=300
```

**Issue**: SQL views don't exist
```sql
-- Solution: Create views first
@sql/views.sql
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Snowflake Testing Best Practices](https://docs.snowflake.com/en/user-guide/testing.html)
- [RDFLib Testing](https://rdflib.readthedocs.io/)

---

**Happy Testing!** 🎉

