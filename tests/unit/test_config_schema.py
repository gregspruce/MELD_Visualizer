import json
from pathlib import Path
import pytest
from src.meld_visualizer.constants import (
    FEEDSTOCK_TYPES, DEFAULT_FEEDSTOCK_TYPE, SAFE_CONFIG_KEYS,
    FEEDSTOCK_DIMENSION_INCHES, FEEDSTOCK_AREA_MM2
)


def test_config_json_parses_if_present():
    # Look for config.json in the config/ directory
    p = Path("config/config.json")
    if not p.exists():
        pytest.skip("config/config.json not present; skipping schema check.")
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "config.json must be a JSON object"


class TestFeedstockConfiguration:
    """Test feedstock type configuration support."""
    
    def test_feedstock_types_defined(self):
        """Test that feedstock types are properly defined."""
        assert isinstance(FEEDSTOCK_TYPES, dict)
        assert len(FEEDSTOCK_TYPES) > 0
        
        # Should have at least square and circular types
        assert 'square' in FEEDSTOCK_TYPES
        assert 'circular' in FEEDSTOCK_TYPES
    
    def test_default_feedstock_type_valid(self):
        """Test that default feedstock type is valid."""
        assert DEFAULT_FEEDSTOCK_TYPE in FEEDSTOCK_TYPES
        assert DEFAULT_FEEDSTOCK_TYPE == 'square'  # MELD uses square rod
    
    def test_feedstock_type_schema(self):
        """Test that all feedstock types have required schema."""
        required_square_fields = ['dimension_mm', 'area_mm2', 'description']
        required_circular_fields = ['diameter_mm', 'area_mm2', 'description']
        
        for feedstock_type, config in FEEDSTOCK_TYPES.items():
            assert isinstance(config, dict)
            assert 'area_mm2' in config
            assert 'description' in config
            assert isinstance(config['description'], str)
            assert config['area_mm2'] > 0
            
            if feedstock_type == 'square':
                for field in required_square_fields:
                    assert field in config
                assert 'dimension_mm' in config
                assert config['dimension_mm'] > 0
            
            elif feedstock_type == 'circular':
                for field in required_circular_fields:
                    assert field in config
                assert 'diameter_mm' in config
                assert config['diameter_mm'] > 0
    
    def test_feedstock_area_calculations(self):
        """Test that feedstock area calculations are correct."""
        square_config = FEEDSTOCK_TYPES['square']
        circular_config = FEEDSTOCK_TYPES['circular']
        
        # Square area = side²
        expected_square_area = square_config['dimension_mm'] ** 2
        assert square_config['area_mm2'] == pytest.approx(expected_square_area, rel=1e-6)
        
        # Circular area = π * (diameter/2)²
        import math
        expected_circular_area = math.pi * (circular_config['diameter_mm'] / 2) ** 2
        assert circular_config['area_mm2'] == pytest.approx(expected_circular_area, rel=1e-6)
    
    def test_feedstock_configuration_safety(self):
        """Test that feedstock configuration keys are marked as safe."""
        assert 'feedstock_type' in SAFE_CONFIG_KEYS
        assert 'feedstock_dimension_inches' in SAFE_CONFIG_KEYS
    
    def test_config_backward_compatibility(self):
        """Test that configuration maintains backward compatibility."""
        # Test that current constants match the square feedstock type
        square_config = FEEDSTOCK_TYPES[DEFAULT_FEEDSTOCK_TYPE]
        
        assert square_config['dimension_mm'] == pytest.approx(FEEDSTOCK_DIMENSION_INCHES * 25.4, rel=1e-6)
        assert square_config['area_mm2'] == pytest.approx(FEEDSTOCK_AREA_MM2, rel=1e-6)


class TestConfigurationValidation:
    """Test configuration validation and loading."""
    
    def test_config_with_feedstock_type(self):
        """Test configuration loading with feedstock type specified."""
        # Test configuration structure for feedstock settings
        test_config = {
            'feedstock_type': 'square',
            'feedstock_dimension_inches': 0.5,
            'default_theme': 'bootstrap',
            'plotly_template': 'plotly_white'
        }
        
        # Should be valid configuration
        for key in test_config.keys():
            if key.startswith('feedstock') or key in ['default_theme', 'plotly_template']:
                assert key in SAFE_CONFIG_KEYS or key == 'feedstock_dimension_inches'
    
    def test_config_with_different_feedstock_types(self):
        """Test that different feedstock types can be configured."""
        valid_types = ['square', 'circular']
        
        for feedstock_type in valid_types:
            test_config = {'feedstock_type': feedstock_type}
            
            # Should be a valid feedstock type
            assert feedstock_type in FEEDSTOCK_TYPES
            
            # Configuration should have all required fields
            config = FEEDSTOCK_TYPES[feedstock_type]
            assert 'area_mm2' in config
            assert 'description' in config
    
    def test_config_validation_prevents_invalid_types(self):
        """Test that invalid feedstock types are handled."""
        invalid_types = ['wire', 'rod', 'invalid', '', None]
        
        for invalid_type in invalid_types:
            # Invalid types should not be in FEEDSTOCK_TYPES
            if invalid_type is not None:
                assert invalid_type not in FEEDSTOCK_TYPES
    
    def test_config_dimensions_validation(self):
        """Test that feedstock dimensions are validated."""
        for feedstock_type, config in FEEDSTOCK_TYPES.items():
            # All dimensions should be positive
            if 'dimension_mm' in config:
                assert config['dimension_mm'] > 0
            if 'diameter_mm' in config:
                assert config['diameter_mm'] > 0
            
            # Area should be positive and reasonable
            assert config['area_mm2'] > 0
            assert config['area_mm2'] < 10000  # Less than 100x100 mm square


class TestConfigurationMigration:
    """Test configuration migration and compatibility."""
    
    def test_legacy_config_compatibility(self):
        """Test that legacy configurations still work."""
        # Older configurations might not have feedstock settings
        legacy_config = {
            'default_theme': 'bootstrap',
            'plotly_template': 'plotly_white'
        }
        
        # Should still be valid (defaults will be used for missing feedstock settings)
        for key in legacy_config.keys():
            assert key in SAFE_CONFIG_KEYS
    
    def test_config_upgrade_path(self):
        """Test that configurations can be upgraded with new feedstock settings."""
        # Start with minimal config
        base_config = {'default_theme': 'bootstrap'}
        
        # Add feedstock settings
        upgraded_config = {
            **base_config,
            'feedstock_type': DEFAULT_FEEDSTOCK_TYPE,
            'feedstock_dimension_inches': FEEDSTOCK_DIMENSION_INCHES
        }
        
        # All keys should be safe
        for key in upgraded_config.keys():
            assert key in SAFE_CONFIG_KEYS
    
    def test_mathematical_consistency_across_configs(self):
        """Test that mathematical relationships are consistent across configurations."""
        for feedstock_type, config in FEEDSTOCK_TYPES.items():
            area = config['area_mm2']
            
            # Area should be reasonable for manufacturing
            assert area > 1  # At least 1 mm²
            assert area < 1000  # Less than 1000 mm² (reasonable for MELD)
            
            # Description should mention dimensions
            description = config['description'].lower()
            assert '0.5' in description  # Should mention the 0.5" dimension
