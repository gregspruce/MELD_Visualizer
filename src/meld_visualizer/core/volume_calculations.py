"""
Volume calculations module for MELD Visualizer.

This module handles all volume-related calculations for the MELD process,
including bead geometry, feedstock parameters, and volume conservation.
Separated from mesh generation for easier tuning and development.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, Union
from dataclasses import dataclass
import logging

# Import constants from centralized location
from ..constants import INCH_TO_MM, MM_TO_INCH

logger = logging.getLogger(__name__)


@dataclass
class FeedstockParameters:
    """
    Parameters defining the feedstock material geometry.
    
    MELD uses square rod feedstock, not circular wire.
    Default values represent 0.5" × 0.5" square rod.
    """
    dimension_inches: float = 0.5  # Square rod dimension in inches
    shape: str = 'square'  # 'square' or 'circular' for future flexibility
    
    @property
    def dimension_mm(self) -> float:
        """Get feedstock dimension in millimeters."""
        return self.dimension_inches * INCH_TO_MM
    
    @property
    def cross_sectional_area_mm2(self) -> float:
        """Calculate cross-sectional area in mm²."""
        if self.shape == 'square':
            return self.dimension_mm ** 2
        elif self.shape == 'circular':
            # For circular wire: π * (d/2)²
            return np.pi * (self.dimension_mm / 2) ** 2
        else:
            raise ValueError(f"Unknown feedstock shape: {self.shape}")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            'dimension_inches': self.dimension_inches,
            'dimension_mm': self.dimension_mm,
            'area_mm2': self.cross_sectional_area_mm2,
            'shape': self.shape
        }


@dataclass
class BeadGeometry:
    """
    Parameters defining the extruded bead geometry.
    
    The bead is modeled as a capsule shape:
    - Rectangular center section with length L
    - Semi-circular ends with radius R
    """
    length_mm: float = 2.0  # Length of rectangular section
    radius_mm: float = 1.0  # Radius of semi-circular ends (typically L/2)
    max_thickness_mm: float = 25.4  # Maximum allowed thickness (1 inch)
    
    @property
    def min_area_mm2(self) -> float:
        """Minimum bead area when thickness is zero (just the circular ends)."""
        return np.pi * self.radius_mm ** 2
    
    def calculate_thickness(self, bead_area_mm2: float) -> float:
        """
        Calculate bead thickness from total cross-sectional area.
        
        Args:
            bead_area_mm2: Total bead cross-sectional area in mm²
            
        Returns:
            Thickness T in mm (clamped to max_thickness_mm)
        """
        # For capsule shape: Area = π*R² + L*T
        # Therefore: T = (Area - π*R²) / L
        thickness = (bead_area_mm2 - self.min_area_mm2) / self.length_mm
        return np.clip(thickness, 0.0, self.max_thickness_mm)
    
    def calculate_area(self, thickness_mm: float) -> float:
        """
        Calculate total bead area from thickness.
        
        Args:
            thickness_mm: Bead thickness in mm
            
        Returns:
            Total cross-sectional area in mm²
        """
        return self.min_area_mm2 + self.length_mm * thickness_mm
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            'length_mm': self.length_mm,
            'radius_mm': self.radius_mm,
            'max_thickness_mm': self.max_thickness_mm,
            'min_area_mm2': self.min_area_mm2
        }


class VolumeCalculator:
    """
    Handles volume calculations for MELD process visualization.
    
    This class encapsulates all volume-related calculations, making it
    easier to tune parameters and validate against physical print results.
    """
    
    def __init__(self, 
                 feedstock: Optional[FeedstockParameters] = None,
                 bead_geometry: Optional[BeadGeometry] = None):
        """
        Initialize volume calculator with material parameters.
        
        Args:
            feedstock: Feedstock material parameters
            bead_geometry: Extruded bead geometry parameters
        """
        self.feedstock = feedstock or FeedstockParameters()
        self.bead_geometry = bead_geometry or BeadGeometry()
        
        # Calibration factors for tuning
        self.volume_correction_factor = 1.0  # Multiplicative correction
        self.area_offset = 0.0  # Additive correction in mm²
        self.width_multiplier = 1.0  # Width spreading factor for bead overlap
        
        logger.info(f"VolumeCalculator initialized with feedstock area: "
                   f"{self.feedstock.cross_sectional_area_mm2:.2f} mm²")
    
    def calculate_bead_area(self, 
                           feed_velocity: Union[float, np.ndarray], 
                           path_velocity: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate bead cross-sectional area from velocities.
        
        Uses conservation of mass principle:
        Volume_in = Volume_out
        Feed_vel × Feedstock_area = Path_vel × Bead_area
        
        Args:
            feed_velocity: Material feed velocity in mm/min
            path_velocity: Tool path velocity in mm/min
            
        Returns:
            Bead cross-sectional area in mm²
        """
        # Avoid division by zero
        path_vel_safe = np.maximum(path_velocity, 1e-6)
        
        # Basic conservation of mass calculation
        bead_area = (feed_velocity * self.feedstock.cross_sectional_area_mm2) / path_vel_safe
        
        # Apply calibration corrections
        bead_area = bead_area * self.volume_correction_factor + self.area_offset
        
        return np.maximum(bead_area, 0.0)  # Ensure non-negative
    
    def calculate_bead_thickness(self,
                                 feed_velocity: Union[float, np.ndarray],
                                 path_velocity: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate bead thickness from velocities.
        
        Args:
            feed_velocity: Material feed velocity in mm/min
            path_velocity: Tool path velocity in mm/min
            
        Returns:
            Bead thickness in mm
        """
        bead_area = self.calculate_bead_area(feed_velocity, path_velocity)
        
        if isinstance(bead_area, np.ndarray):
            return np.array([self.bead_geometry.calculate_thickness(a) for a in bead_area])
        else:
            return self.bead_geometry.calculate_thickness(bead_area)
    
    def calculate_effective_bead_width(self, thickness: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate effective bead width including spreading.
        
        The physical bead spreads wider than the theoretical capsule shape
        due to material flow and pressure during deposition.
        
        Args:
            thickness: Bead thickness in mm
            
        Returns:
            Effective bead width in mm
        """
        # Theoretical capsule width
        theoretical_width = thickness + 2 * self.bead_geometry.radius_mm
        
        # Apply width multiplier to account for spreading
        effective_width = theoretical_width * self.width_multiplier
        
        return effective_width
    
    def process_dataframe(self, df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
        """
        Add volume calculation columns to a DataFrame.
        
        Args:
            df: DataFrame with FeedVel and PathVel columns
            inplace: Whether to modify the DataFrame in place
            
        Returns:
            DataFrame with added volume calculation columns
        """
        if not inplace:
            df = df.copy()
        
        # Validate required columns
        required_cols = ['FeedVel', 'PathVel']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Calculate bead geometry
        df['Bead_Area_mm2'] = self.calculate_bead_area(
            df['FeedVel'].values, 
            df['PathVel'].values
        )
        
        df['Bead_Thickness_mm'] = self.calculate_bead_thickness(
            df['FeedVel'].values,
            df['PathVel'].values
        )
        
        # Calculate effective width with spreading
        df['Bead_Width_mm'] = self.calculate_effective_bead_width(df['Bead_Thickness_mm'].values)
        
        # Add reference columns for analysis
        df['Feedstock_Area_mm2'] = self.feedstock.cross_sectional_area_mm2
        df['Volume_Rate_mm3_per_min'] = df['FeedVel'] * self.feedstock.cross_sectional_area_mm2
        
        # Calculate actual deposited volume per segment (needs segment length)
        if 'XPos' in df.columns and 'YPos' in df.columns and 'ZPos' in df.columns:
            # Calculate segment lengths
            positions = df[['XPos', 'YPos', 'ZPos']].values
            segment_lengths = np.zeros(len(df))
            segment_lengths[1:] = np.linalg.norm(np.diff(positions, axis=0), axis=1)
            df['Segment_Length_mm'] = segment_lengths
            
            # Calculate time per segment (assuming constant velocity)
            time_per_segment = np.zeros(len(df))
            mask = df['PathVel'] > 1e-6
            time_per_segment[mask] = segment_lengths[mask] / df.loc[mask, 'PathVel']
            df['Segment_Time_min'] = time_per_segment
            
            # Calculate volume per segment
            df['Segment_Volume_mm3'] = df['Bead_Area_mm2'] * df['Segment_Length_mm']
        
        logger.info(f"Processed {len(df)} rows with volume calculations")
        logger.info(f"Bead area range: {df['Bead_Area_mm2'].min():.2f} - {df['Bead_Area_mm2'].max():.2f} mm²")
        logger.info(f"Thickness range: {df['Bead_Thickness_mm'].min():.2f} - {df['Bead_Thickness_mm'].max():.2f} mm")
        
        return df
    
    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Calculate volume statistics from a processed DataFrame.
        
        Args:
            df: DataFrame with volume calculation columns
            
        Returns:
            Dictionary of statistics
        """
        stats = {}
        
        # Only calculate stats for active extrusion
        active_mask = (df['FeedVel'] > 0) & (df['PathVel'] > 0)
        df_active = df[active_mask]
        
        if not df_active.empty:
            stats['bead_area'] = {
                'min': float(df_active['Bead_Area_mm2'].min()),
                'max': float(df_active['Bead_Area_mm2'].max()),
                'mean': float(df_active['Bead_Area_mm2'].mean()),
                'std': float(df_active['Bead_Area_mm2'].std())
            }
            
            stats['thickness'] = {
                'min': float(df_active['Bead_Thickness_mm'].min()),
                'max': float(df_active['Bead_Thickness_mm'].max()),
                'mean': float(df_active['Bead_Thickness_mm'].mean()),
                'std': float(df_active['Bead_Thickness_mm'].std())
            }
            
            if 'Segment_Volume_mm3' in df_active.columns:
                total_volume = df_active['Segment_Volume_mm3'].sum()
                stats['total_volume'] = {
                    'mm3': float(total_volume),
                    'cm3': float(total_volume / 1000),
                    'in3': float(total_volume / (INCH_TO_MM ** 3))
                }
            
            stats['process'] = {
                'feed_vel_mean': float(df_active['FeedVel'].mean()),
                'path_vel_mean': float(df_active['PathVel'].mean()),
                'active_points': int(len(df_active)),
                'total_points': int(len(df))
            }
        
        return stats
    
    def set_calibration(self, 
                        correction_factor: float = 1.0,
                        area_offset: float = 0.0,
                        width_multiplier: float = 1.0) -> None:
        """
        Set calibration factors for volume calculations.
        
        These factors can be tuned to match physical print results.
        
        Args:
            correction_factor: Multiplicative correction for volume (default 1.0)
            area_offset: Additive correction in mm² (default 0.0)
            width_multiplier: Width spreading factor for overlap (default 1.0)
        """
        self.volume_correction_factor = correction_factor
        self.area_offset = area_offset
        self.width_multiplier = width_multiplier
        logger.info(f"Calibration set: factor={correction_factor}, offset={area_offset}, width_mult={width_multiplier}")
    
    def export_parameters(self) -> Dict[str, any]:
        """
        Export all parameters for documentation or persistence.
        
        Returns:
            Dictionary containing all calculator parameters
        """
        return {
            'feedstock': self.feedstock.to_dict(),
            'bead_geometry': self.bead_geometry.to_dict(),
            'calibration': {
                'correction_factor': self.volume_correction_factor,
                'area_offset': self.area_offset
            }
        }
    
    @classmethod
    def from_parameters(cls, params: Dict[str, any]) -> 'VolumeCalculator':
        """
        Create calculator from exported parameters.
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            New VolumeCalculator instance
        """
        feedstock = FeedstockParameters(
            dimension_inches=params['feedstock']['dimension_inches'],
            shape=params['feedstock']['shape']
        )
        
        bead = BeadGeometry(
            length_mm=params['bead_geometry']['length_mm'],
            radius_mm=params['bead_geometry']['radius_mm'],
            max_thickness_mm=params['bead_geometry']['max_thickness_mm']
        )
        
        calc = cls(feedstock=feedstock, bead_geometry=bead)
        calc.set_calibration(
            correction_factor=params['calibration']['correction_factor'],
            area_offset=params['calibration']['area_offset']
        )
        
        return calc


# Convenience function for backward compatibility
def calculate_volume_data(df: pd.DataFrame, 
                          feedstock_params: Optional[Dict] = None,
                          bead_params: Optional[Dict] = None) -> pd.DataFrame:
    """
    Calculate volume data for a DataFrame (backward compatible interface).
    
    Args:
        df: Input DataFrame with velocity columns
        feedstock_params: Optional feedstock parameters
        bead_params: Optional bead geometry parameters
        
    Returns:
        DataFrame with added volume columns
    """
    calc = VolumeCalculator()
    
    if feedstock_params:
        calc.feedstock = FeedstockParameters(**feedstock_params)
    if bead_params:
        calc.bead_geometry = BeadGeometry(**bead_params)
    
    return calc.process_dataframe(df)