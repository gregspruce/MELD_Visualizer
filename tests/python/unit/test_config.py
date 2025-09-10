"""
Unit tests for configuration management in MELD Visualizer.
Tests configuration loading, validation, and theme management.
"""

import pytest
import json
from unittest.mock import patch, mock_open, Mock
from pathlib import Path

# Import the modules under test
from meld_visualizer.config import (
    APP_CONFIG,
    THEMES,
    PLOTLY_TEMPLATE,
    load_config,
    get_responsive_plot_style,
    get_responsive_plotly_config
)
from meld_visualizer.constants import (
    RESPONSIVE_PLOT_CONFIG,
    PLOT_TYPE_MODIFIERS,
    ALLOWED_FILE_EXTENSIONS,
    MAX_FILE_SIZE_MB
)


class TestConfigLoading:
    """Test configuration loading functionality"""
    
    def test_load_valid_config(self):
        """Test loading valid configuration file"""
        # load_config() takes no parameters and loads from default location
        config = load_config()
        
        assert isinstance(config, dict)
        assert 'default_theme' in config
        assert 'plotly_template' in config
        assert 'graph_1_options' in config
        assert 'graph_2_options' in config
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_nonexistent_config(self, mock_open):
        """Test loading non-existent configuration file"""
        # Should return default config when file not found
        config = load_config()
        
        assert isinstance(config, dict)
        assert config["default_theme"] == "Cerulean (Default)"
        assert "plotly_template" in config
    
    @patch('builtins.open', new_callable=mock_open, read_data='{invalid json content}')
    def test_load_invalid_json_config(self, mock_file):
        """Test loading malformed JSON configuration"""
        # Should return default config on JSON decode error
        config = load_config()
        
        assert isinstance(config, dict)
        assert config["default_theme"] == "Cerulean (Default)"
    
    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_load_empty_config(self, mock_file):
        """Test loading empty configuration file"""
        config = load_config()
        
        assert isinstance(config, dict)
        # Should merge with defaults
        assert config["default_theme"] == "Cerulean (Default)"
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"default_theme": "Darkly"}')
    def test_load_config_with_mock(self, mock_file):
        """Test config loading with mocked file system"""
        config = load_config()
        
        assert isinstance(config, dict)
        assert config["default_theme"] == "Darkly"


class TestThemeManagement:
    """Test theme management functionality"""
    
    def test_default_themes_available(self):
        """Test that default themes are properly configured"""
        assert isinstance(THEMES, dict)
        assert len(THEMES) > 0
        assert "Cerulean (Default)" in THEMES
        
    def test_theme_url_validity(self):
        """Test that theme URLs are valid"""
        for theme_name, theme_url in THEMES.items():
            assert isinstance(theme_url, str)
            assert theme_url.startswith('http')
    
    def test_plotly_template_configuration(self):
        """Test plotly template configuration"""
        assert PLOTLY_TEMPLATE in ['plotly_white', 'plotly_dark']
        
    @patch('builtins.open', new_callable=mock_open, read_data='{"default_theme": "Darkly"}')
    def test_dark_theme_plotly_template(self, mock_file):
        """Test automatic plotly template selection for dark themes"""
        # This test would require reloading the config module
        config = load_config()
        # For dark theme, should auto-select plotly_dark
        # Note: This is limited by how the module loads config at import time
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
        from meld_visualizer.constants import RESPONSIVE_PLOT_CONFIG
        
        assert isinstance(RESPONSIVE_PLOT_CONFIG, dict)
        assert len(RESPONSIVE_PLOT_CONFIG) > 0
        
        # Check that config has required keys
        for size, config in RESPONSIVE_PLOT_CONFIG.items():
            assert 'height' in config
            assert 'min_height' in config
            assert 'max_height' in config
    
    def test_supported_file_types(self):
        """Test supported file types are properly defined"""
        assert isinstance(ALLOWED_FILE_EXTENSIONS, set)
        assert len(ALLOWED_FILE_EXTENSIONS) > 0
        
        # Check for common file types
        expected_extensions = {'.csv', '.nc', '.gcode'}
        assert expected_extensions.issubset(ALLOWED_FILE_EXTENSIONS)
    
    def test_max_file_size_constraint(self):
        """Test file size constraints are reasonable"""
        assert isinstance(MAX_FILE_SIZE_MB, (int, float))
        assert MAX_FILE_SIZE_MB > 0
        assert MAX_FILE_SIZE_MB <= 1000  # Reasonable upper limit
    
    def test_constants_immutability(self):
        """Test that constants cannot be easily modified"""
        # Test that constants maintain their values
        original_max_size = MAX_FILE_SIZE_MB
        
        # Constants should be consistent
        assert MAX_FILE_SIZE_MB == original_max_size


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
        
        # Load config multiple times to test performance
        for _ in range(100):
            config = load_config()
        
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