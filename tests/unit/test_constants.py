"""
Unit tests for constants module.
Tests feedstock geometry calculations and mathematical relationships.
"""

import pytest
import math
from src.meld_visualizer.constants import (
    INCH_TO_MM, 
    FEEDSTOCK_DIMENSION_INCHES, 
    FEEDSTOCK_DIMENSION_MM,
    FEEDSTOCK_AREA_MM2,
    FEEDSTOCK_TYPES,
    DEFAULT_FEEDSTOCK_TYPE,
    WIRE_DIAMETER_MM,
    BEAD_LENGTH_MM,
    BEAD_RADIUS_MM
)


class TestFeedstockGeometry:
    """Test feedstock geometry constants and calculations."""
    
    def test_feedstock_dimension_conversion(self):
        """Test that feedstock dimensions are correctly converted from inches to mm."""
        expected_mm = FEEDSTOCK_DIMENSION_INCHES * INCH_TO_MM
        assert FEEDSTOCK_DIMENSION_MM == pytest.approx(expected_mm, rel=1e-6)
        
        # Verify specific value for 0.5 inch square rod
        assert FEEDSTOCK_DIMENSION_INCHES == 0.5
        assert FEEDSTOCK_DIMENSION_MM == pytest.approx(12.7, rel=1e-3)
    
    def test_feedstock_area_calculation(self):
        """Test that feedstock area is correctly calculated for square rod."""
        # For square rod: Area = side²
        expected_area = FEEDSTOCK_DIMENSION_MM ** 2
        assert FEEDSTOCK_AREA_MM2 == pytest.approx(expected_area, rel=1e-6)
        
        # Verify specific calculation: (0.5 * 25.4)² = 12.7² = 161.29 mm²
        assert FEEDSTOCK_AREA_MM2 == pytest.approx(161.29, rel=1e-2)
    
    def test_legacy_compatibility(self):
        """Test that legacy WIRE_DIAMETER_MM constant maintains compatibility."""
        # Legacy constant should equal the square dimension for backward compatibility
        assert WIRE_DIAMETER_MM == FEEDSTOCK_DIMENSION_MM
    
    def test_feedstock_types_configuration(self):
        """Test that feedstock type configurations are correctly defined."""
        assert DEFAULT_FEEDSTOCK_TYPE in FEEDSTOCK_TYPES
        
        # Test square feedstock type
        square_config = FEEDSTOCK_TYPES['square']
        assert 'dimension_mm' in square_config
        assert 'area_mm2' in square_config
        assert 'description' in square_config
        assert square_config['dimension_mm'] == FEEDSTOCK_DIMENSION_MM
        assert square_config['area_mm2'] == FEEDSTOCK_AREA_MM2
        
        # Test circular feedstock type
        circular_config = FEEDSTOCK_TYPES['circular']
        assert 'diameter_mm' in circular_config
        assert 'area_mm2' in circular_config
        assert 'description' in circular_config
        
        # Circular area should be π * (d/2)²
        expected_circular_area = math.pi * (circular_config['diameter_mm'] / 2) ** 2
        assert circular_config['area_mm2'] == pytest.approx(expected_circular_area, rel=1e-6)
    
    def test_square_vs_circular_area_difference(self):
        """Test that square and circular areas are different and correct."""
        square_area = FEEDSTOCK_TYPES['square']['area_mm2']
        circular_area = FEEDSTOCK_TYPES['circular']['area_mm2']
        
        # Square should have larger area than circle for same dimension
        assert square_area > circular_area
        
        # Verify relationship: square area / circular area ≈ 4/π ≈ 1.273
        ratio = square_area / circular_area
        assert ratio == pytest.approx(4 / math.pi, rel=1e-3)


class TestUnitConversions:
    """Test unit conversion constants."""
    
    def test_inch_to_mm_constant(self):
        """Test inch to millimeter conversion constant."""
        assert INCH_TO_MM == 25.4
    
    def test_conversion_consistency(self):
        """Test that unit conversions are mathematically consistent."""
        # Test round-trip conversion
        inches = 1.0
        mm = inches * INCH_TO_MM
        back_to_inches = mm / INCH_TO_MM
        assert back_to_inches == pytest.approx(inches, rel=1e-10)


class TestMeshConstants:
    """Test mesh generation constants."""
    
    def test_bead_geometry_constants(self):
        """Test bead geometry constants are reasonable."""
        assert BEAD_LENGTH_MM > 0
        assert BEAD_RADIUS_MM > 0
        assert BEAD_RADIUS_MM == BEAD_LENGTH_MM / 2.0
    
    def test_bead_size_relative_to_feedstock(self):
        """Test that bead dimensions are reasonable relative to feedstock."""
        # Bead length should be much smaller than feedstock dimension
        assert BEAD_LENGTH_MM < FEEDSTOCK_DIMENSION_MM
        
        # But not too small to be meaningful
        assert BEAD_LENGTH_MM >= 0.1  # At least 0.1mm


class TestMathematicalRelationships:
    """Test mathematical relationships between constants."""
    
    def test_area_calculation_precision(self):
        """Test that area calculations maintain sufficient precision."""
        # Calculate area with high precision
        dimension_precise = 0.5 * 25.4  # 12.7 exactly
        area_precise = dimension_precise ** 2  # 161.29 exactly
        
        assert FEEDSTOCK_AREA_MM2 == pytest.approx(area_precise, abs=1e-10)
    
    def test_feedstock_volume_calculations(self):
        """Test volume calculations for different feedstock lengths."""
        # Volume = Area × Length
        test_length_mm = 100.0
        expected_volume_mm3 = FEEDSTOCK_AREA_MM2 * test_length_mm
        
        # This should be approximately 16,129 mm³ for 100mm of 0.5" square rod
        assert expected_volume_mm3 == pytest.approx(16129, rel=1e-2)
    
    def test_bead_area_ratio(self):
        """Test that bead cross-sectional area is reasonable compared to feedstock."""
        # Assuming circular bead cross-section with diameter = BEAD_RADIUS_MM * 2
        bead_cross_area = math.pi * BEAD_RADIUS_MM ** 2
        
        # Bead area should be much smaller than feedstock area
        area_ratio = bead_cross_area / FEEDSTOCK_AREA_MM2
        assert area_ratio < 0.05  # Less than 5% of feedstock area (reasonable for 1mm radius vs 161mm² feedstock)


class TestConfigurationValidation:
    """Test configuration-related constants."""
    
    def test_default_feedstock_type(self):
        """Test that default feedstock type is valid."""
        assert DEFAULT_FEEDSTOCK_TYPE in FEEDSTOCK_TYPES
        assert DEFAULT_FEEDSTOCK_TYPE == 'square'  # MELD uses square rod
    
    def test_feedstock_type_completeness(self):
        """Test that all feedstock types have required fields."""
        required_fields = {
            'square': ['dimension_mm', 'area_mm2', 'description'],
            'circular': ['diameter_mm', 'area_mm2', 'description']
        }
        
        for feedstock_type, fields in required_fields.items():
            assert feedstock_type in FEEDSTOCK_TYPES
            config = FEEDSTOCK_TYPES[feedstock_type]
            for field in fields:
                assert field in config
                assert config[field] is not None
    
    def test_feedstock_descriptions(self):
        """Test that feedstock descriptions are informative."""
        for feedstock_type, config in FEEDSTOCK_TYPES.items():
            description = config['description']
            assert isinstance(description, str)
            assert len(description) > 10  # Meaningful description
            assert '0.5"' in description  # Should mention dimension


class TestNumericalStability:
    """Test numerical stability and edge cases."""
    
    def test_floating_point_precision(self):
        """Test that calculations maintain floating point precision."""
        # Test that repeated calculations give same result
        calc1 = (0.5 * 25.4) ** 2
        calc2 = 0.5 ** 2 * 25.4 ** 2
        calc3 = (0.5 * 25.4) * (0.5 * 25.4)
        
        assert calc1 == pytest.approx(calc2, abs=1e-15)
        assert calc1 == pytest.approx(calc3, abs=1e-15)
        assert all(c == pytest.approx(FEEDSTOCK_AREA_MM2, abs=1e-10) for c in [calc1, calc2, calc3])
    
    def test_zero_division_safety(self):
        """Test that constants prevent zero division scenarios."""
        # All dimensional constants should be positive
        assert FEEDSTOCK_DIMENSION_MM > 0
        assert FEEDSTOCK_AREA_MM2 > 0
        assert BEAD_LENGTH_MM > 0
        assert BEAD_RADIUS_MM > 0
        
        # Area calculations should never be zero
        for config in FEEDSTOCK_TYPES.values():
            assert config['area_mm2'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])