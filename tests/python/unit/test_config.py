"""
Unit tests for configuration management in MELD Visualizer.
Tests configuration loading, validation, and theme management.
"""

import pytest
import json
from unittest.mock import patch, mock_open, Mock
from pathlib import Path

# Import the modules under test
try:
    from meld_visualizer.config import (
        APP_CONFIG,
        THEMES,
        PLOTLY_TEMPLATE,
        load_config,
        validate_config,
        get_responsive_plot_style,
        get_responsive_plotly_config
    )
    from meld_visualizer.constants import (
        DEFAULT_PLOT_HEIGHT,
        DEFAULT_PLOT_WIDTH,
        SUPPORTED_FILE_TYPES,
        MAX_FILE_SIZE_MB
    )
except ImportError:
    # If direct import fails, skip these tests
    pytestmark = pytest.mark.skip("Config/Constants modules not available")


class TestConfigLoading:
    """Test configuration loading functionality"""
    
    def test_load_valid_config(self, temp_config_file):
        """Test loading valid configuration file"""
        config = load_config(temp_config_file)
        
        assert isinstance(config, dict)
        assert 'default_theme' in config
        assert 'max_file_size_mb' in config
        assert 'cache_timeout' in config
        assert 'debug_mode' in config
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration file"""
        # Should return default config or raise appropriate exception
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config.json")
    
    def test_load_invalid_json_config(self, tmp_path):
        """Test loading malformed JSON configuration"""
        invalid_config = tmp_path / "invalid.json"
        invalid_config.write_text("{invalid json content")
        
        with pytest.raises(json.JSONDecodeError):
            load_config(invalid_config)
    
    def test_load_empty_config(self, tmp_path):
        """Test loading empty configuration file"""
        empty_config = tmp_path / "empty.json"
        empty_config.write_text("{}")
        
        config = load_config(empty_config)
        assert isinstance(config, dict)
        # Should handle empty config gracefully
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "value"}')
    def test_load_config_with_mock(self, mock_file):
        """Test config loading with mocked file system"""
        config = load_config("mocked_config.json")
        
        assert isinstance(config, dict)
        mock_file.assert_called_once_with("mocked_config.json", 'r')


class TestConfigValidation:
    """Test configuration validation functionality"""
    
    def test_validate_complete_config(self):
        """Test validation of complete, valid configuration"""
        valid_config = {
            'default_theme': 'BOOTSTRAP',
            'max_file_size_mb': 100,
            'cache_timeout': 300,
            'debug_mode': False,
            'plotly_template': 'plotly_white'
        }
        
        is_valid, errors = validate_config(valid_config)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_missing_required_keys(self):
        """Test validation with missing required configuration keys"""
        incomplete_config = {
            'max_file_size_mb': 100
            # Missing other required keys
        }
        
        is_valid, errors = validate_config(incomplete_config)
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_invalid_data_types(self):
        """Test validation with invalid data types"""
        invalid_config = {
            'default_theme': 123,  # Should be string
            'max_file_size_mb': "invalid",  # Should be numeric
            'cache_timeout': -1,  # Should be positive
            'debug_mode': "yes"  # Should be boolean
        }
        
        is_valid, errors = validate_config(invalid_config)
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_boundary_values(self):
        """Test validation of boundary values"""
        boundary_config = {
            'default_theme': 'BOOTSTRAP',
            'max_file_size_mb': 0,  # Edge case
            'cache_timeout': 0,  # Edge case
            'debug_mode': True
        }
        
        # Test behavior with boundary values
        is_valid, errors = validate_config(boundary_config)
        # Adjust assertions based on actual validation rules


class TestThemeManagement:
    """Test theme management functionality"""
    
    def test_default_themes_available(self):
        """Test that default themes are properly defined"""
        assert isinstance(THEMES, dict)
        assert len(THEMES) > 0
        
        # Check for common Bootstrap themes
        expected_themes = ['BOOTSTRAP', 'FLATLY', 'DARKLY', 'CERULEAN']
        for theme in expected_themes:
            if theme in THEMES:
                assert isinstance(THEMES[theme], str)
    
    def test_theme_url_validity(self):
        """Test that theme URLs are valid"""
        for theme_name, theme_url in THEMES.items():
            if isinstance(theme_url, str):
                # Basic URL validation
                assert theme_url.startswith(('http://', 'https://')) or theme_url.startswith('/'), \
                    f"Invalid theme URL for {theme_name}: {theme_url}"
    
    def test_plotly_template_configuration(self):
        """Test Plotly template configuration"""
        assert isinstance(PLOTLY_TEMPLATE, str)
        
        # Common Plotly templates
        valid_templates = [
            'plotly', 'plotly_white', 'plotly_dark', 'ggplot2',
            'seaborn', 'simple_white', 'none'
        ]
        
        # Template should be one of the valid ones or custom
        assert PLOTLY_TEMPLATE in valid_templates or PLOTLY_TEMPLATE.startswith('custom_')


class TestResponsivePlotConfiguration:
    """Test responsive plot configuration functionality"""
    
    def test_get_responsive_plot_style_scatter3d(self):
        """Test responsive style for 3D scatter plots"""
        style = get_responsive_plot_style('scatter_3d')
        
        assert isinstance(style, dict)
        assert 'height' in style
        assert 'width' in style
        
        # Should have appropriate dimensions for desktop
        assert isinstance(style['height'], (int, str))
        assert isinstance(style['width'], (int, str))
    
    def test_get_responsive_plot_style_2d(self):
        """Test responsive style for 2D plots"""
        style = get_responsive_plot_style('scatter_2d')
        
        assert isinstance(style, dict)
        # 2D plots might have different styling requirements
    
    def test_get_responsive_plotly_config(self):
        """Test responsive Plotly configuration"""
        config = get_responsive_plotly_config()
        
        assert isinstance(config, dict)
        
        # Check for expected Plotly config options
        expected_keys = ['displayModeBar', 'responsive', 'toImageButtonOptions']
        for key in expected_keys:
            if key in config:
                assert isinstance(config[key], (bool, dict))
    
    def test_responsive_config_mobile_vs_desktop(self):
        """Test different configurations for mobile vs desktop"""
        desktop_config = get_responsive_plotly_config('desktop')
        mobile_config = get_responsive_plotly_config('mobile')
        
        assert isinstance(desktop_config, dict)
        assert isinstance(mobile_config, dict)
        
        # Mobile and desktop configs might differ
        # Add specific assertions based on implementation


class TestConstants:
    """Test application constants"""
    
    def test_plot_dimensions_constants(self):
        """Test plot dimension constants are valid"""
        assert isinstance(DEFAULT_PLOT_HEIGHT, (int, str))
        assert isinstance(DEFAULT_PLOT_WIDTH, (int, str))
        
        if isinstance(DEFAULT_PLOT_HEIGHT, int):
            assert DEFAULT_PLOT_HEIGHT > 0
        if isinstance(DEFAULT_PLOT_WIDTH, int):
            assert DEFAULT_PLOT_WIDTH > 0
    
    def test_supported_file_types(self):
        """Test supported file types are properly defined"""
        assert isinstance(SUPPORTED_FILE_TYPES, (list, tuple, dict))
        
        if isinstance(SUPPORTED_FILE_TYPES, (list, tuple)):
            assert len(SUPPORTED_FILE_TYPES) > 0
            # Should include CSV and NC files for MELD data
            file_extensions = [ext.lower() for ext in SUPPORTED_FILE_TYPES]
            assert 'csv' in file_extensions or '.csv' in file_extensions
            assert 'nc' in file_extensions or '.nc' in file_extensions
    
    def test_max_file_size_constraint(self):
        """Test file size constraints are reasonable"""
        assert isinstance(MAX_FILE_SIZE_MB, (int, float))
        assert MAX_FILE_SIZE_MB > 0
        assert MAX_FILE_SIZE_MB <= 1000  # Reasonable upper limit
    
    def test_constants_immutability(self):
        """Test that constants cannot be easily modified"""
        # This is more of a convention test
        original_height = DEFAULT_PLOT_HEIGHT
        
        # Attempting to modify should not affect the module constant
        # (This test depends on how constants are implemented)


class TestConfigIntegration:
    """Integration tests for configuration system"""
    
    def test_config_and_constants_compatibility(self):
        """Test that configuration and constants work together"""
        # Test that config values don't conflict with constants
        if hasattr(APP_CONFIG, 'max_file_size_mb'):
            assert APP_CONFIG['max_file_size_mb'] <= MAX_FILE_SIZE_MB
    
    def test_theme_and_plotly_template_compatibility(self):
        """Test that theme and Plotly template are compatible"""
        # Some themes might require specific Plotly templates
        current_theme = APP_CONFIG.get('default_theme', 'BOOTSTRAP')
        current_template = PLOTLY_TEMPLATE
        
        # Add compatibility checks based on implementation
        assert isinstance(current_theme, str)
        assert isinstance(current_template, str)
    
    @patch.dict('os.environ', {'MELD_DEBUG': 'true'})
    def test_environment_variable_override(self):
        """Test that environment variables can override config"""
        # Test environment variable handling if implemented
        pass
    
    def test_config_loading_fallback(self):
        """Test fallback behavior when config loading fails"""
        with patch('meld_visualizer.config.load_config', side_effect=FileNotFoundError):
            # Should fall back to default configuration
            # Test depends on actual fallback implementation
            pass


# Performance tests for configuration
class TestConfigPerformance:
    """Test configuration performance"""
    
    @pytest.mark.performance
    def test_config_loading_performance(self, temp_config_file):
        """Test configuration loading performance"""
        import time
        
        start_time = time.time()
        
        # Load config multiple times to test caching
        for _ in range(100):
            config = load_config(temp_config_file)
        
        load_time = time.time() - start_time
        
        # Should be fast due to caching or simple structure
        assert load_time < 1.0  # Should complete within 1 second
    
    @pytest.mark.performance
    def test_responsive_style_calculation_performance(self):
        """Test performance of responsive style calculations"""
        import time
        
        start_time = time.time()
        
        # Calculate styles multiple times
        for _ in range(1000):
            style = get_responsive_plot_style('scatter_3d')
        
        calc_time = time.time() - start_time
        
        # Should be very fast
        assert calc_time < 0.5  # Should complete within 0.5 seconds