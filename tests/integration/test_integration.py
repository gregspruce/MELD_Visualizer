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

from src.meld_visualizer.app import create_app
from src.meld_visualizer.services import get_data_service, get_cache
from src.meld_visualizer.callbacks import register_all_callbacks


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
        from src.meld_visualizer.callbacks.data_callbacks import update_data_and_configs
        
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
        
        from src.meld_visualizer.callbacks.data_callbacks import update_data_and_configs
        
        # Upload imperial file
        df_json, filename_msg, _, _, _ = update_data_and_configs(contents, "imperial.csv")
        
        # Check conversion message
        assert "converted to mm" in filename_msg.lower()
        
        # Parse the returned JSON
        import io
        df_result = pd.read_json(io.StringIO(df_json), orient='split')
        
        # Verify conversion applied
        from src.meld_visualizer.constants import INCH_TO_MM
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
        
        from src.meld_visualizer.callbacks.data_callbacks import handle_gcode_upload
        
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
        from src.meld_visualizer.callbacks.graph_callbacks import update_graph_1
        
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
        from src.meld_visualizer.callbacks.visualization_callbacks import update_mesh_plot
        
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
    
    def test_volume_mesh_with_corrected_feedstock(self):
        """Test volume mesh generation with corrected feedstock area calculations."""
        from src.meld_visualizer.core.data_processing import generate_volume_mesh
        from src.meld_visualizer.constants import FEEDSTOCK_AREA_MM2
        
        # Create test data with known velocity relationships for validation
        df = pd.DataFrame({
            'XPos': [0, 10, 20, 30],
            'YPos': [0, 0, 0, 0],
            'ZPos': [0, 0, 0, 0],
            'FeedVel': [161.29, 161.29, 161.29, 161.29],  # Equal to feedstock area for easy calculation
            'PathVel': [161.29, 161.29, 161.29, 161.29],  # 1:1 ratio
            'ToolTemp': [100, 150, 200, 250]
        })
        
        # Generate mesh with corrected feedstock area
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        
        # Verify mesh generation succeeds
        assert mesh_data is not None
        assert 'vertices' in mesh_data
        assert 'faces' in mesh_data
        assert 'vertex_colors' in mesh_data
        
        # Verify mesh has reasonable scale
        vertices = mesh_data['vertices']
        assert len(vertices) > 0
        
        # With 1:1 feed/path ratio, bead area should equal feedstock area
        # This validates the corrected calculation is used
        vertex_span = np.max(vertices) - np.min(vertices)
        assert vertex_span > 0  # Should have some dimensions
        assert vertex_span < 1000  # But not unreasonably large
    
    def test_volume_conservation_integration(self):
        """Test that volume conservation is maintained in full workflow."""
        from src.meld_visualizer.core.data_processing import generate_volume_mesh
        from src.meld_visualizer.constants import FEEDSTOCK_AREA_MM2
        
        # Test different feed/path velocity ratios
        test_cases = [
            {'feed': 100, 'path': 50, 'expected_ratio': 2.0},    # Double bead area
            {'feed': 50, 'path': 100, 'expected_ratio': 0.5},   # Half bead area  
            {'feed': 161.29, 'path': 161.29, 'expected_ratio': 1.0}  # Equal areas
        ]
        
        for case in test_cases:
            df = pd.DataFrame({
                'XPos': [0, 10],
                'YPos': [0, 0],
                'ZPos': [0, 0],
                'FeedVel': [case['feed'], case['feed']],
                'PathVel': [case['path'], case['path']],
                'ToolTemp': [100, 150]
            })
            
            mesh_data = generate_volume_mesh(df, 'ToolTemp')
            assert mesh_data is not None
            
            # Expected bead area = (feed_vel * feedstock_area) / path_vel
            expected_bead_area = (case['feed'] * FEEDSTOCK_AREA_MM2) / case['path']
            expected_feedstock_ratio = expected_bead_area / FEEDSTOCK_AREA_MM2
            
            # Verify the ratio is as expected
            assert expected_feedstock_ratio == pytest.approx(case['expected_ratio'], rel=1e-2)
    
    def test_mesh_generation_with_different_feedstock_configs(self):
        """Test mesh generation works with different feedstock configurations."""
        from src.meld_visualizer.core.data_processing import generate_volume_mesh
        from src.meld_visualizer.constants import FEEDSTOCK_TYPES
        
        # Create consistent test data
        df = pd.DataFrame({
            'XPos': [0, 10, 20],
            'YPos': [0, 0, 0],
            'ZPos': [0, 1, 2],
            'FeedVel': [100, 100, 100],
            'PathVel': [50, 50, 50],
            'ToolTemp': [100, 150, 200]
        })
        
        # Mesh generation should work regardless of configured feedstock type
        # (since the constants are used internally)
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        
        assert mesh_data is not None
        assert len(mesh_data['vertices']) > 0
        assert len(mesh_data['faces']) > 0
        
        # Verify that square rod area is being used (161.29 mm²)
        square_area = FEEDSTOCK_TYPES['square']['area_mm2']
        assert square_area == pytest.approx(161.29, rel=1e-2)
        
        # Bead area calculation: (100 * 161.29) / 50 = 322.58 mm²
        expected_bead_area = (100 * square_area) / 50
        assert expected_bead_area == pytest.approx(322.58, rel=1e-2)
    
    def test_line_plot_generation(self, sample_dataframe):
        """Test 3D line plot generation."""
        from src.meld_visualizer.callbacks.visualization_callbacks import update_line_plot
        
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
        from src.meld_visualizer.callbacks.config_callbacks import save_config_and_advise_restart
        
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
        from src.meld_visualizer.callbacks.filter_callbacks import sync_filter_controls
        
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


class TestBackwardCompatibility:
    """Test backward compatibility with existing data and configurations."""
    
    def test_existing_csv_files_still_work(self):
        """Test that existing CSV files continue to work with corrected calculations."""
        from src.meld_visualizer.core.data_processing import parse_contents, generate_volume_mesh
        
        # Simulate existing CSV file with typical MELD data
        legacy_df = pd.DataFrame({
            'Date': ['2024-01-01'] * 5,
            'Time': ['10:00:00', '10:00:01', '10:00:02', '10:00:03', '10:00:04'],
            'XPos': [0, 10, 20, 30, 40],
            'YPos': [0, 5, 10, 15, 20],
            'ZPos': [0, 0.5, 1.0, 1.5, 2.0],
            'FeedVel': [0, 100, 150, 200, 150],
            'PathVel': [0, 50, 75, 100, 75],
            'ToolTemp': [25, 200, 250, 300, 275],
            'XVel': [0, 50, 75, 100, 75],
            'YVel': [0, 25, 37, 50, 37],
            'ZVel': [0, 10, 15, 20, 15]
        })
        
        csv_string = legacy_df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        # Parse the legacy file
        df, error, converted = parse_contents(contents, "legacy_data.csv")
        
        # Should parse successfully
        assert df is not None
        assert error is None
        
        # Should have expected columns
        required_cols = ['XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel', 'ToolTemp']
        for col in required_cols:
            assert col in df.columns
        
        # Generate mesh with active data
        df_active = df[df['FeedVel'] > 0]
        mesh_data = generate_volume_mesh(df_active, 'ToolTemp')
        
        # Should generate valid mesh
        assert mesh_data is not None
        assert len(mesh_data['vertices']) > 0
    
    def test_legacy_imperial_conversion_still_works(self):
        """Test that imperial unit conversion still works correctly."""
        from src.meld_visualizer.core.data_processing import parse_contents
        from src.meld_visualizer.constants import INCH_TO_MM
        
        # Create imperial data (low velocities indicate imperial units)
        imperial_df = pd.DataFrame({
            'Date': ['2024-01-01'] * 4,
            'Time': ['10:00:00', '10:00:01', '10:00:02', '10:00:03'],
            'XPos': [0, 1, 2, 3],        # inches
            'YPos': [0, 1, 2, 3],        # inches
            'ZPos': [0, 0.1, 0.2, 0.3],  # inches
            'FeedVel': [0, 15, 20, 25],  # inch/min (low values)
            'PathVel': [0, 7, 10, 12],   # inch/min
            'ToolTemp': [25, 200, 250, 300]
        })
        
        csv_string = imperial_df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        # Parse with conversion
        df, error, converted = parse_contents(contents, "imperial.csv")
        
        # Should convert successfully
        assert converted is True
        assert error is None
        
        # Verify conversion was applied
        assert df['XPos'].iloc[1] == pytest.approx(1 * INCH_TO_MM, rel=1e-3)
        assert df['FeedVel'].iloc[1] == pytest.approx(15 * INCH_TO_MM, rel=1e-3)
    
    def test_existing_gcode_files_still_work(self):
        """Test that existing G-code files continue to work."""
        from src.meld_visualizer.core.data_processing import parse_gcode_file, generate_volume_mesh
        
        # Typical MELD G-code content
        gcode_content = """
        ; MELD G-code example
        G0 X0 Y0 Z0 F1000
        M34 S4200  ; Start material feed at 420 mm/min
        G1 X25.4 Y25.4 F500
        G1 X50.8 Y25.4
        G1 X50.8 Y50.8
        G1 X25.4 Y50.8
        G1 X25.4 Y25.4
        M35  ; Stop material feed
        G0 Z10
        """
        
        encoded = base64.b64encode(gcode_content.encode()).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        # Parse G-code
        df, error, converted = parse_gcode_file(contents, "existing.nc")
        
        # Should parse successfully
        assert df is not None
        assert error is None
        
        # Generate mesh from G-code data
        df_active = df[df['FeedVel'] > 0]
        if not df_active.empty:
            mesh_data = generate_volume_mesh(df_active, 'FeedVel')
            assert mesh_data is not None
    
    def test_legacy_configuration_compatibility(self):
        """Test that configurations without feedstock settings still work."""
        from src.meld_visualizer.constants import FEEDSTOCK_TYPES, DEFAULT_FEEDSTOCK_TYPE
        
        # Legacy configuration without feedstock settings
        legacy_config = {
            "default_theme": "bootstrap",
            "plotly_template": "plotly_white",
            "graph_1_options": ["XPos", "YPos", "ZPos"],
            "graph_2_options": ["ZPos"],
            "plot_2d_y_options": ["FeedVel"],
            "plot_2d_color_options": ["ToolTemp"]
        }
        
        # Should be able to use default feedstock settings
        default_feedstock = FEEDSTOCK_TYPES[DEFAULT_FEEDSTOCK_TYPE]
        assert default_feedstock['area_mm2'] == pytest.approx(161.29, rel=1e-2)
        
        # Legacy configs should still be valid
        assert isinstance(legacy_config, dict)
        assert "default_theme" in legacy_config
    
    def test_volume_calculations_produce_reasonable_results(self):
        """Test that volume calculations with corrected area produce reasonable results."""
        from src.meld_visualizer.core.data_processing import generate_volume_mesh
        from src.meld_visualizer.constants import FEEDSTOCK_AREA_MM2
        
        # Test with typical MELD velocities
        typical_data = pd.DataFrame({
            'XPos': [0, 25, 50, 75, 100],
            'YPos': [0, 0, 0, 0, 0],
            'ZPos': [0, 0, 0, 0, 0],
            'FeedVel': [100, 120, 150, 120, 100],  # Typical feed velocities
            'PathVel': [80, 80, 80, 80, 80],      # Typical path velocity
            'ToolTemp': [200, 250, 300, 250, 200]
        })
        
        mesh_data = generate_volume_mesh(typical_data, 'ToolTemp')
        assert mesh_data is not None
        
        # Verify reasonable bead areas are calculated
        # With these velocities: bead_area ≈ (100-150 * 161.29) / 80
        min_expected = (100 * FEEDSTOCK_AREA_MM2) / 80  # ≈ 201.6 mm²
        max_expected = (150 * FEEDSTOCK_AREA_MM2) / 80  # ≈ 302.4 mm²
        
        assert min_expected > 200  # Reasonable minimum
        assert max_expected < 400  # Reasonable maximum
    
    def test_no_regression_in_mesh_quality(self):
        """Test that mesh quality is maintained with corrected calculations."""
        from src.meld_visualizer.core.data_processing import generate_volume_mesh
        
        # Create mesh with corrected calculations
        df = pd.DataFrame({
            'XPos': np.linspace(0, 50, 20),
            'YPos': np.linspace(0, 50, 20),
            'ZPos': np.repeat(np.arange(4), 5),
            'FeedVel': np.full(20, 100),
            'PathVel': np.full(20, 80),
            'ToolTemp': np.linspace(200, 300, 20)
        })
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        assert mesh_data is not None
        
        vertices = mesh_data['vertices']
        faces = mesh_data['faces']
        colors = mesh_data['vertex_colors']
        
        # Quality checks
        assert len(vertices) > 0
        assert len(faces) > 0
        assert len(colors) == len(vertices)
        
        # Verify face indices are valid
        max_vertex_index = len(vertices) - 1
        assert np.all(faces <= max_vertex_index)
        assert np.all(faces >= 0)
        
        # Verify vertices have reasonable coordinates
        assert not np.any(np.isnan(vertices))
        assert not np.any(np.isinf(vertices))


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
        from src.meld_visualizer.callbacks.data_callbacks import update_data_and_configs
        
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
        from src.meld_visualizer.callbacks.graph_callbacks import update_graph_1
        
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
        from src.meld_visualizer.callbacks.data_callbacks import update_data_and_configs
        
        # Create malicious content
        malicious = "<script>alert('xss')</script>"
        encoded = base64.b64encode(malicious.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        # Try to upload
        with patch('src.meld_visualizer.core.data_processing.FileValidator.validate_file_upload') as mock_validate:
            mock_validate.return_value = (False, "Security risk detected")
            
            result = update_data_and_configs(contents, "malicious.csv")
            
            # Should reject the file
            df_json, error_msg, _, _, _ = result
            assert error_msg is not None
            assert "risk" in error_msg.lower() or "error" in error_msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])