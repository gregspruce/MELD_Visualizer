# MELD Visualizer - Code Patterns and Conventions

## Coding Conventions

### Package Structure
```
src/
└── meld_visualizer/
    ├── __init__.py          # Package initialization
    ├── __main__.py          # Module execution entry
    ├── app.py              # Main application
    ├── layout.py           # UI components
    ├── config.py           # Configuration management
    ├── data_processing.py  # Data operations
    ├── callbacks/          # Modular callbacks
    │   ├── __init__.py
    │   ├── main_callbacks.py
    │   ├── filter_callbacks.py
    │   ├── config_callbacks.py
    │   └── plot_callbacks.py
    └── utils/              # Utility modules
        ├── __init__.py
        ├── hot_reload.py
        ├── security_utils.py
        └── performance.py
```

### Import Conventions
```python
# Absolute imports for external packages
import pandas as pd
import numpy as np
from dash import callback, Input, Output, State

# Relative imports within package
from ..data_processing import parse_csv_file
from ..utils.security_utils import InputValidator
from ..config import load_config, APP_CONFIG
```

### Type Hints
```python
from typing import Optional, Tuple, List, Dict, Any

def process_data(
    file_path: str,
    options: Optional[Dict[str, Any]] = None
) -> Tuple[pd.DataFrame, Optional[str], bool]:
    """
    Process data file with optional configuration.
    
    Returns:
        Tuple of (dataframe, error_message, conversion_flag)
    """
    pass
```

## Common Patterns and Abstractions

### Data Processing Pipeline
```python
# Standard pipeline pattern
def process_upload(contents: str, filename: str) -> Tuple[Any, str, bool]:
    # 1. Validate input
    if not InputValidator.is_valid_file(filename):
        return None, "Invalid file type", False
    
    # 2. Parse data
    try:
        data = parse_file(contents, filename)
    except Exception as e:
        return None, f"Parse error: {str(e)}", False
    
    # 3. Transform data
    data = apply_transformations(data)
    
    # 4. Validate output
    if not validate_data(data):
        return None, "Invalid data format", False
    
    return data, None, True
```

### Callback Pattern with Error Handling
```python
@callback(
    Output('output-id', 'children'),
    Output('error-id', 'children'),
    Input('trigger-id', 'n_clicks'),
    State('data-store', 'data'),
    prevent_initial_call=True
)
def update_output(n_clicks, stored_data):
    if not n_clicks:
        raise PreventUpdate
    
    try:
        # Process data
        result = process_data(stored_data)
        return result, ""
    except Exception as e:
        # Return empty result with error message
        return "", f"Error: {str(e)}"
```

### Hot-Reload Pattern
```python
# Hot-reload callback with allow_duplicate
@callback(
    Output('theme-css', 'href'),
    Output('config-store', 'data'),
    Input('save-settings-btn', 'n_clicks'),
    State('theme-dropdown', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def hot_reload_settings(n_clicks, theme):
    # Update runtime config
    APP_CONFIG['theme']['bootstrap'] = theme
    
    # Save to file
    save_config(APP_CONFIG)
    
    # Return new theme URL
    theme_url = get_theme_url(theme)
    return theme_url, APP_CONFIG
```

### Component Factory Pattern
```python
def create_graph_component(
    graph_id: str,
    graph_type: str = "scatter",
    options: Optional[Dict] = None
) -> dcc.Graph:
    """Factory for creating configured graph components."""
    config = {
        'displayModeBar': True,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{graph_type}_plot'
        }
    }
    
    if options:
        config.update(options)
    
    return dcc.Graph(
        id={'type': 'graph-component', 'index': graph_id},
        config=config
    )
```

## Testing Patterns

### Unit Test Pattern
```python
import pytest
from unittest.mock import Mock, patch

class TestDataProcessing:
    @pytest.fixture
    def sample_data(self):
        """Fixture providing test data."""
        return pd.DataFrame({
            'TIME': [1, 2, 3],
            'TEMP': [100, 150, 200]
        })
    
    def test_parse_csv_file(self, sample_data, tmp_path):
        # Arrange
        file_path = tmp_path / "test.csv"
        sample_data.to_csv(file_path, index=False)
        
        # Act
        result, error, converted = parse_csv_file(str(file_path))
        
        # Assert
        assert error is None
        assert not converted
        assert len(result) == 3
```

### Integration Test Pattern
```python
@pytest.mark.integration
def test_callback_integration(dash_app):
    """Test callback chain integration."""
    # Setup app context
    with dash_app.server.app_context():
        # Trigger callback
        output = trigger_callback(
            'upload-data',
            contents='base64,encoded,data'
        )
        
        # Verify callback chain
        assert output['data-store'] is not None
        assert output['graph-output'] is not None
```

### E2E Test Pattern
```python
@pytest.mark.e2e
def test_user_workflow(selenium_driver, live_server):
    """Test complete user workflow."""
    # Navigate to app
    selenium_driver.get(live_server.url)
    
    # Upload file
    upload = selenium_driver.find_element(By.ID, "upload-data")
    upload.send_keys("/path/to/test.csv")
    
    # Wait for processing
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_element_located((By.ID, "graph-output"))
    )
    
    # Verify result
    graph = selenium_driver.find_element(By.ID, "graph-output")
    assert graph.is_displayed()
```

## Error Handling Approaches

### Graceful Degradation
```python
def load_config_with_fallback():
    """Load config with fallback to defaults."""
    try:
        return load_config()
    except FileNotFoundError:
        logger.warning("Config not found, using defaults")
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        logger.error("Invalid config, using defaults")
        return DEFAULT_CONFIG
```

### Validation and Sanitization
```python
def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean dataframe."""
    # Remove invalid values
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Drop rows with critical missing data
    required_cols = ['TIME', 'X', 'Y', 'Z']
    df = df.dropna(subset=required_cols)
    
    # Ensure numeric types
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df
```

### Logging Pattern
```python
import logging

logger = logging.getLogger(__name__)

def process_with_logging(data):
    """Process with comprehensive logging."""
    logger.info(f"Starting processing of {len(data)} records")
    
    try:
        result = heavy_processing(data)
        logger.info("Processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise
```

## Performance Patterns

### Caching Decorator
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param1: str, param2: int) -> float:
    """Cache expensive calculations."""
    # Complex calculation here
    return result
```

### Batch Processing
```python
def process_in_batches(data: List, batch_size: int = 1000):
    """Process large datasets in batches."""
    results = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        result = process_batch(batch)
        results.extend(result)
        
        # Allow garbage collection
        del batch
    
    return results
```

### Lazy Loading
```python
class LazyDataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data = None
    
    @property
    def data(self):
        """Load data only when accessed."""
        if self._data is None:
            self._data = pd.read_csv(self.file_path)
        return self._data
```