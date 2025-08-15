"""
Integration tests for MELD Visualizer.
Tests complete workflows and component interactions.
"""

import pytest
import pandas as pd
import numpy as np
import json
import base64
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dash.testing import DashCompositeTest

from app import create_app
from services import get_data_service, get_cache
from callbacks import register_all_callbacks


class TestFileUploadWorkflow:
    """Test complete file upload workflow."""
    
    @pytest.fixture
    def app(self):
        """Create test app instance."""
        app = create_app(testing=True)
        return app
    
    @pytest.fixture
    def sample_csv_content(self):
        """Create sample CSV content."""
        df = pd.DataFrame({
            'XPos': [0, 10, 20, 30, 40],
            'YPos': [0, 10, 20, 30, 40],
            'ZPos': [0, 1, 2, 3, 4],
            'FeedVel': [0, 50, 100, 150, 200],
            'PathVel': [0, 25, 50, 75, 100],
            'ToolTemp': [20, 100, 150, 200, 250],
            'Time': pd.date_range('2024-01-01', periods=5, freq='S')
        })
        csv_string = df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        return f"data:text/csv;base64,{encoded}"
    
    def test_csv_upload_to_visualization(self, app, sample_csv_content):
        """Test complete CSV upload to visualization workflow."""
        # Clear cache for clean test
        get_cache().clear()
        
        # Simulate file upload through callbacks
        from callbacks.data_callbacks import update_data_and_configs
        
        # Call the callback
        result = update_data_and_configs(sample_csv_content, "test.csv")
        
        # Unpack results
        df_json, filename_msg, layout_config, warnings, column_ranges = result
        
        # Verify results
        assert df_json is not None
        assert "test.csv" in filename_msg
        assert layout_config is not None
        assert 'axis_options' in layout_config
        assert column_ranges is not None
        
        # Verify DataFrame was cached
        data_service = get_data_service()
        cached_df = data_service.cache.get_dataframe("test.csv")
        assert cached_df is not None
    
    def test_imperial_to_metric_conversion_workflow(self):
        """Test imperial to metric conversion during upload."""
        # Create imperial data
        df_imperial = pd.DataFrame({
            'XPos': [0, 1, 2, 3],  # inches
            'YPos': [0, 1, 2, 3],  # inches
            'ZPos': [0, 0.1, 0.2, 0.3],  # inches
            'FeedVel': [0, 10, 20, 30],  # Low values = imperial
            'PathVel': [0, 5, 10, 15],
            'ToolTemp': [20, 100, 150, 200],
            'Time': pd.date_range('2024-01-01', periods=4, freq='S')
        })
        
        csv_string = df_imperial.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        from callbacks.data_callbacks import update_data_and_configs
        
        # Upload imperial file
        df_json, filename_msg, _, _, _ = update_data_and_configs(contents, "imperial.csv")
        
        # Check conversion message
        assert "converted to mm" in filename_msg.lower()
        
        # Parse the returned JSON
        import io
        df_result = pd.read_json(io.StringIO(df_json), orient='split')
        
        # Verify conversion applied
        from constants import INCH_TO_MM
        assert df_result['XPos'].iloc[1] == pytest.approx(1 * INCH_TO_MM, rel=1e-3)
        assert df_result['YPos'].iloc[2] == pytest.approx(2 * INCH_TO_MM, rel=1e-3)
    
    def test_gcode_upload_workflow(self):
        """Test G-code file upload workflow."""
        gcode_content = """
        G0 X0 Y0 Z0
        G1 X10 Y10 F100
        M34 S4200
        G1 X20 Y20 Z5
        M35
        """
        
        encoded = base64.b64encode(gcode_content.encode()).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        from callbacks.data_callbacks import handle_gcode_upload
        
        # Upload G-code file
        df_json, message, show_alert = handle_gcode_upload(contents, "test.nc")
        
        # Verify results
        assert df_json is not None
        assert show_alert is True
        
        # Parse the result
        import io
        df_result = pd.read_json(io.StringIO(df_json), orient='split')
        
        # Verify G-code was parsed
        assert 'XPos' in df_result.columns
        assert 'FeedVel' in df_result.columns
        assert df_result['XPos'].iloc[-1] == 20


class TestVisualizationWorkflow:
    """Test visualization generation workflows."""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame for visualization."""
        return pd.DataFrame({
            'XPos': np.linspace(0, 100, 100),
            'YPos': np.linspace(0, 100, 100),
            'ZPos': np.repeat(np.arange(10), 10),
            'FeedVel': np.random.rand(100) * 200,
            'PathVel': np.random.rand(100) * 100,
            'ToolTemp': np.random.rand(100) * 300,
            'TimeInSeconds': np.arange(100),
            'Time': pd.date_range('2024-01-01', periods=100, freq='S')
        })
    
    def test_3d_scatter_plot_generation(self, sample_dataframe):
        """Test 3D scatter plot generation workflow."""
        from callbacks.graph_callbacks import update_graph_1
        
        # Serialize DataFrame
        df_json = sample_dataframe.to_json(date_format='iso', orient='split')
        
        # Generate plot
        fig = update_graph_1(
            df_json,
            col_chosen='ToolTemp',
            slider_range=[0, 5],
            config_updated=None
        )
        
        # Verify figure
        assert fig is not None
        assert len(fig.data) > 0
        assert fig.data[0].type == 'scatter3d'
    
    def test_mesh_generation_workflow(self, sample_dataframe):
        """Test mesh generation workflow."""
        from callbacks.visualization_callbacks import update_mesh_plot
        
        # Filter active data
        df_active = sample_dataframe[sample_dataframe['FeedVel'] > 0]
        df_json = df_active.to_json(date_format='iso', orient='split')
        
        # Generate mesh
        fig = update_mesh_plot(
            n_clicks=1,
            jsonified_df=df_json,
            color_col='ToolTemp',
            cmin=0,
            cmax=300,
            z_stretch_factor=2.0
        )
        
        # Verify mesh figure
        assert fig is not None
        assert len(fig.data) > 0
        assert fig.data[0].type == 'mesh3d'
    
    def test_line_plot_generation(self, sample_dataframe):
        """Test 3D line plot generation."""
        from callbacks.visualization_callbacks import update_line_plot
        
        df_json = sample_dataframe.to_json(date_format='iso', orient='split')
        
        # Generate line plot
        fig = update_line_plot(
            n_clicks=1,
            jsonified_df=df_json,
            z_stretch_factor=1.5
        )
        
        # Verify figure
        assert fig is not None
        assert len(fig.data) > 0
        assert fig.data[0].type == 'scatter3d'
        assert fig.data[0].mode == 'lines+markers'


class TestConfigurationWorkflow:
    """Test configuration management workflows."""
    
    def test_save_configuration_workflow(self):
        """Test saving configuration settings."""
        from callbacks.config_callbacks import save_config_and_advise_restart
        
        # Test configuration
        test_config = {
            'theme': 'Cerulean',
            'template': 'plotly_dark',
            'g1_opts': ['XPos', 'YPos'],
            'g2_opts': ['ZPos'],
            'y_2d_opts': ['FeedVel'],
            'color_2d_opts': ['ToolTemp']
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            
            # Mock the configuration manager to use temp file
            with patch('callbacks.config_callbacks.ConfigurationManager.save_config') as mock_save:
                mock_save.return_value = (True, "Success")
                
                # Call save callback
                show_alert, message, updated = save_config_and_advise_restart(
                    n_clicks=1,
                    theme=test_config['theme'],
                    template=test_config['template'],
                    g1_opts=test_config['g1_opts'],
                    g2_opts=test_config['g2_opts'],
                    y_2d_opts=test_config['y_2d_opts'],
                    color_2d_opts=test_config['color_2d_opts']
                )
                
                # Verify results
                assert show_alert is True
                assert "saved" in message.lower()
                assert updated == 1
    
    def test_load_configuration_workflow(self):
        """Test loading configuration on startup."""
        from config import load_config
        
        # Create test config
        test_config = {
            "default_theme": "TestTheme",
            "graph_1_options": ["TestColumn1"],
            "graph_2_options": ["TestColumn2"]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text(json.dumps(test_config))
            
            # Load config
            with patch('config.Path.cwd') as mock_cwd:
                mock_cwd.return_value = Path(tmpdir)
                loaded = load_config()
            
            # Verify loaded config
            assert loaded["default_theme"] == "TestTheme"
            assert "TestColumn1" in loaded["graph_1_options"]


class TestFilteringWorkflow:
    """Test data filtering workflows."""
    
    def test_range_filter_workflow(self):
        """Test range filtering workflow."""
        from callbacks.filter_callbacks import sync_filter_controls
        
        # Test filter synchronization
        result = sync_filter_controls(
            slider_val=[10, 20],
            lower_in=10,
            upper_in=20,
            s_min_in=0,
            s_max_in=100,
            column_ranges={'ZPos': [0, 100]},
            custom_filter_col='ZPos'
        )
        
        # Verify outputs
        out_s_min, out_s_max, out_range, out_lower, out_upper, _, _ = result
        
        assert out_s_min == 0
        assert out_s_max == 100
        assert out_range == [10, 20]
        assert out_lower == 10
        assert out_upper == 20
    
    def test_custom_filter_workflow(self):
        """Test custom column filtering."""
        from services import get_data_service
        
        data_service = get_data_service()
        
        # Create test data
        df = pd.DataFrame({
            'CustomCol': np.arange(100),
            'Value': np.random.randn(100)
        })
        
        # Apply custom filter
        filtered = data_service.filter_by_range(df, 'CustomCol', 25, 75)
        
        # Verify filtering
        assert len(filtered) == 51  # 25 to 75 inclusive
        assert filtered['CustomCol'].min() == 25
        assert filtered['CustomCol'].max() == 75


class TestCachingWorkflow:
    """Test caching workflows."""
    
    def test_cache_hit_workflow(self):
        """Test that cache is used for repeated operations."""
        from services import get_data_service
        
        data_service = get_data_service()
        data_service.clear_cache()
        
        # Create test data
        df = pd.DataFrame({
            'A': np.arange(100),
            'B': np.random.randn(100)
        })
        
        # First operation - cache miss
        stats1 = data_service.get_column_statistics(df)
        cache_stats1 = data_service.get_cache_stats()
        
        # Second operation - cache hit
        stats2 = data_service.get_column_statistics(df)
        cache_stats2 = data_service.get_cache_stats()
        
        # Verify cache was used
        assert cache_stats2['hits'] > cache_stats1['hits']
        assert stats1 == stats2
    
    def test_cache_expiration_workflow(self):
        """Test cache expiration and refresh."""
        from services.cache_service import CacheService
        import time
        
        # Create cache with short TTL
        cache = CacheService(max_size_mb=1, ttl_seconds=0.5)
        
        # Store data
        cache.set("test_key", "test_value")
        
        # Should be available immediately
        assert cache.get("test_key") == "test_value"
        
        # Wait for expiration
        time.sleep(0.6)
        
        # Should be expired
        assert cache.get("test_key") is None


class TestErrorHandlingWorkflow:
    """Test error handling workflows."""
    
    def test_invalid_file_upload(self):
        """Test handling of invalid file uploads."""
        from callbacks.data_callbacks import update_data_and_configs
        
        # Invalid file content
        invalid_content = "not_base64_encoded"
        
        # Try to upload
        result = update_data_and_configs(invalid_content, "bad.csv")
        
        # Should handle gracefully
        df_json, error_msg, _, _, _ = result
        assert error_msg is not None
        assert "error" in error_msg.lower()
    
    def test_missing_column_handling(self):
        """Test handling of missing columns."""
        from callbacks.graph_callbacks import update_graph_1
        
        # DataFrame missing expected columns
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        df_json = df.to_json(date_format='iso', orient='split')
        
        # Try to plot with missing column
        fig = update_graph_1(
            df_json,
            col_chosen='NonExistent',
            slider_range=[0, 10],
            config_updated=None
        )
        
        # Should return empty figure with error message
        assert fig is not None
        assert len(fig.data) == 0 or fig.layout.annotations
    
    def test_security_validation_failure(self):
        """Test security validation failure handling."""
        from callbacks.data_callbacks import update_data_and_configs
        
        # Create malicious content
        malicious = "<script>alert('xss')</script>"
        encoded = base64.b64encode(malicious.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        # Try to upload
        with patch('data_processing.FileValidator.validate_file_upload') as mock_validate:
            mock_validate.return_value = (False, "Security risk detected")
            
            result = update_data_and_configs(contents, "malicious.csv")
            
            # Should reject the file
            df_json, error_msg, _, _, _ = result
            assert error_msg is not None
            assert "risk" in error_msg.lower() or "error" in error_msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])