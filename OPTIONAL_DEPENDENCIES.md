# 📦 Optional Dependencies Guide

## Overview

The RDF/OWL Visualizer has been designed to work with or without optional dependencies. Core functionality is fully available with just the base requirements.

## Required vs Optional

### ✅ Required (Always Needed)

These packages are essential for core functionality:

```
streamlit>=1.28.0          # UI framework
rdflib>=6.3.2              # RDF processing
networkx>=3.1              # Graph algorithms
plotly>=5.17.0             # Interactive visualization
pandas>=2.0.0              # Data manipulation
openpyxl>=3.1.2            # Excel export support
```

For Snowflake deployment:
```
snowflake-connector-python>=3.2.0
snowflake-snowpark-python>=1.9.0
```

### 🔧 Optional (Nice to Have)

These packages provide additional features but are NOT required:

```
streamlit-agraph>=0.0.45   # Alternative network graph visualization
pyvis>=0.3.2               # Alternative visualization library (not used)
```

## What Happens Without Optional Dependencies?

### Without `streamlit-agraph`

**Impact:** ✅ **None - Application works perfectly**

**What changes:**
- The "Network Graph" visualization option automatically falls back to Plotly
- You'll see a friendly message: "Using Plotly visualization instead"
- All other features work normally

**Plotly provides:**
- ✅ Interactive graphs
- ✅ Zoom and pan
- ✅ Node and edge labels
- ✅ Color-coded nodes
- ✅ Export capabilities
- ✅ Better performance on large graphs

**Conclusion:** Most users won't need `streamlit-agraph` at all.

## Installation Options

### Option 1: Minimal Installation (Recommended)

Install only required dependencies:

```bash
pip install streamlit rdflib networkx plotly pandas openpyxl
```

Or use requirements.txt (streamlit-agraph is commented out):
```bash
pip install -r requirements.txt
```

### Option 2: Full Installation (Optional)

If you specifically want the network graph visualization:

```bash
pip install streamlit rdflib networkx plotly pandas openpyxl streamlit-agraph
```

Or uncomment in requirements.txt:
```txt
# Uncomment if you want network graph visualization
streamlit-agraph>=0.0.45
```

Then:
```bash
pip install -r requirements.txt
```

## Testing with Optional Dependencies

The test suite automatically handles optional dependencies:

```bash
# Run all tests (skips streamlit-agraph tests if not installed)
pytest

# Tests will show:
# test_visualize_with_agraph SKIPPED (streamlit-agraph not installed)
```

This is expected and normal behavior.

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'streamlit_agraph'"

**This is not an error!** The application handles this automatically.

**What to do:**
1. **Nothing** - The app will use Plotly instead
2. If you see this error, just click past it - the app will work fine
3. Optionally, install streamlit-agraph if you want: `pip install streamlit-agraph`

### The app shows a warning about streamlit-agraph

**This is normal!** The warning is informational:

```
⚠️ streamlit-agraph is not installed. Using Plotly visualization instead.
ℹ️ To enable network graph visualization, install: pip install streamlit-agraph
```

**What to do:**
1. **Ignore it** - Plotly visualization works great
2. Or install streamlit-agraph if you prefer network graphs

## Why is streamlit-agraph Optional?

1. **Installation Issues**: streamlit-agraph can have dependency conflicts
2. **Not Essential**: Plotly provides excellent visualization
3. **Performance**: Plotly often performs better on large graphs
4. **Maintenance**: Fewer dependencies = easier maintenance
5. **Compatibility**: Better compatibility across Python versions

## Feature Comparison

| Feature | Plotly | streamlit-agraph |
|---------|--------|------------------|
| Interactive | ✅ Yes | ✅ Yes |
| Zoom/Pan | ✅ Yes | ✅ Yes |
| Node Labels | ✅ Yes | ✅ Yes |
| Edge Labels | ✅ Yes | ✅ Yes |
| Color Coding | ✅ Yes | ✅ Yes |
| Export | ✅ Yes | ⚠️ Limited |
| Performance (Large) | ✅ Better | ⚠️ Slower |
| Force Layout | ⚠️ Spring | ✅ Physics |
| Installation | ✅ Easy | ⚠️ Can be tricky |

**Recommendation:** Use Plotly (default) unless you specifically need physics-based force layout.

## For Developers

### Making Dependencies Optional in Code

The pattern used in this project:

```python
# Optional dependency pattern
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    AGRAPH_AVAILABLE = True
except ImportError:
    AGRAPH_AVAILABLE = False
    Node = None
    Edge = None
    Config = None

# Later in code
def visualize_with_agraph(self, max_nodes: int = 50):
    if not AGRAPH_AVAILABLE:
        warnings.warn("streamlit-agraph not installed")
        return [], [], None
    
    # Use agraph features...
```

### Testing Optional Dependencies

```python
import pytest

@pytest.mark.skipif(not AGRAPH_AVAILABLE, reason="streamlit-agraph not installed")
def test_with_optional_dependency():
    # Test code that requires optional dependency
    pass

def test_without_optional_dependency():
    if not AGRAPH_AVAILABLE:
        # Test fallback behavior
        pass
```

## Snowflake Deployment

For Snowflake deployment:
- **Don't include** streamlit-agraph in requirements.txt
- Snowflake will handle required dependencies automatically
- Optional dependencies can cause deployment issues

## Summary

✅ **You don't need streamlit-agraph**
✅ **The app works perfectly without it**
✅ **Plotly provides excellent visualization**
✅ **Tests handle it gracefully**
✅ **No action required on your part**

If you see any "streamlit_agraph" related messages, you can safely ignore them or install the package if you specifically want network graph visualization.

## Quick Reference

| Scenario | What to Do |
|----------|------------|
| Fresh install | `pip install -r requirements.txt` (streamlit-agraph is commented out) |
| Error message | Ignore - app works fine without it |
| Want network graphs | `pip install streamlit-agraph` |
| Running tests | Tests auto-skip if not installed |
| Deploying to Snowflake | Don't include streamlit-agraph |

---

**Bottom Line:** The application is designed to work beautifully without streamlit-agraph. You have full functionality with just the core dependencies. 🎉

