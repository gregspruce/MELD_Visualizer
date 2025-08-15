"""
Data service for processing and managing MELD visualization data.
Integrates caching and optimized processing functions.
"""

import logging
from typing import Optional, Tuple, Dict, Any
import pandas as pd
import numpy as np

from constants import (
    IMPERIAL_VELOCITY_THRESHOLD, MIN_PATH_VELOCITY, MIN_FEED_VELOCITY,
    POSITION_COLUMNS, VELOCITY_COLUMNS, CHUNK_SIZE
)
from security_utils import FileValidator, InputValidator
from .cache_service import get_cache, cached
from .file_service import FileService

# Try to import optimized functions, fallback to standard
try:
    from data_processing_optimized import (
        parse_contents_optimized as parse_contents_impl,
        generate_volume_mesh_optimized as generate_mesh_impl,
        generate_volume_mesh_lod
    )
    OPTIMIZED_AVAILABLE = True
except ImportError:
    from data_processing import (
        parse_contents as parse_contents_impl,
        generate_volume_mesh as generate_mesh_impl
    )
    OPTIMIZED_AVAILABLE = False
    generate_volume_mesh_lod = None

logger = logging.getLogger(__name__)


class DataService:
    """
    Service for data processing operations with caching and optimization.
    """
    
    def __init__(self):
        """Initialize data service."""
        self.cache = get_cache()
        self.file_service = FileService()
        self.current_df_id = None
        logger.info(f"DataService initialized (optimized: {OPTIMIZED_AVAILABLE})")
    
    def parse_file(self, contents: str, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str], bool]:
        """
        Parse uploaded file with caching and validation.
        
        Args:
            contents: Base64 encoded file contents
            filename: Name of the uploaded file
            
        Returns:
            Tuple of (DataFrame, error_message, units_converted)
        """
        # Check cache first
        cache_key = self.cache._generate_key("parse", filename, contents[:100])
        cached_result = self.cache.get(cache_key)
        
        if cached_result is not None:
            logger.info(f"Using cached parse result for {filename}")
            return cached_result
        
        # Validate file
        is_valid, error_msg = FileValidator.validate_file_upload(contents, filename)
        if not is_valid:
            return None, error_msg, False
        
        # Parse file
        df, error_msg, converted = parse_contents_impl(contents, filename)
        
        if df is not None:
            # Cache the successful result
            result = (df, error_msg, converted)
            self.cache.set(cache_key, result)
            
            # Also cache the DataFrame separately for quick access
            self.current_df_id = filename
            self.cache.cache_dataframe(df, filename)
            
            logger.info(f"Successfully parsed {filename} ({len(df)} rows)")
        
        return df, error_msg, converted
    
    def get_current_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the currently loaded DataFrame from cache."""
        if self.current_df_id:
            return self.cache.get_dataframe(self.current_df_id)
        return None
    
    def filter_active_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter DataFrame to only active printing data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Filtered DataFrame
        """
        cache_key = self.cache._generate_key("filter_active", len(df))
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        # Apply filters
        df_active = df[
            (df['FeedVel'] > MIN_FEED_VELOCITY) & 
            (df['PathVel'] > MIN_PATH_VELOCITY)
        ].copy()
        
        self.cache.set(cache_key, df_active)
        return df_active
    
    def filter_by_range(self, df: pd.DataFrame, column: str, 
                       min_val: float, max_val: float) -> pd.DataFrame:
        """
        Filter DataFrame by column range with validation.
        
        Args:
            df: Input DataFrame
            column: Column name to filter
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            Filtered DataFrame
        """
        # Validate column
        if column not in df.columns:
            logger.warning(f"Column {column} not found in DataFrame")
            return df
        
        # Sanitize inputs
        min_val = InputValidator.sanitize_numeric_input(min_val)
        max_val = InputValidator.sanitize_numeric_input(max_val)
        
        # Use vectorized operation for performance
        mask = (df[column] >= min_val) & (df[column] <= max_val)
        return df[mask]
    
    def generate_mesh(self, df: pd.DataFrame, color_column: str, 
                     lod: str = 'high') -> Optional[Dict[str, Any]]:
        """
        Generate 3D mesh with LOD support.
        
        Args:
            df: Input DataFrame
            color_column: Column for mesh coloring
            lod: Level of detail ('high', 'medium', 'low')
            
        Returns:
            Mesh data dictionary or None
        """
        # Validate inputs
        if color_column not in df.columns:
            logger.error(f"Color column {color_column} not found")
            return None
        
        # Check cache
        cache_key = self.cache._generate_key("mesh", len(df), color_column, lod)
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            logger.info(f"Using cached mesh (LOD: {lod})")
            return cached
        
        # Generate mesh
        if OPTIMIZED_AVAILABLE and generate_volume_mesh_lod is not None:
            mesh_data = generate_volume_mesh_lod(df, color_column, lod)
        else:
            mesh_data = generate_mesh_impl(df, color_column)
        
        if mesh_data is not None:
            self.cache.set(cache_key, mesh_data)
            logger.info(f"Generated mesh with {len(mesh_data['vertices'])} vertices")
        
        return mesh_data
    
    def process_in_chunks(self, df: pd.DataFrame, 
                         operation: callable, 
                         chunk_size: int = CHUNK_SIZE) -> pd.DataFrame:
        """
        Process large DataFrame in chunks for memory efficiency.
        
        Args:
            df: Input DataFrame
            operation: Function to apply to each chunk
            chunk_size: Size of each chunk
            
        Returns:
            Processed DataFrame
        """
        if len(df) <= chunk_size:
            return operation(df)
        
        chunks = []
        for start in range(0, len(df), chunk_size):
            end = min(start + chunk_size, len(df))
            chunk = df.iloc[start:end]
            processed = operation(chunk)
            chunks.append(processed)
        
        return pd.concat(chunks, ignore_index=True)
    
    def get_column_statistics(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all numeric columns with caching.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary of column statistics
        """
        cache_key = self.cache._generate_key("stats", len(df), list(df.columns))
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        numeric_cols = df.select_dtypes(include=np.number).columns
        stats = {}
        
        for col in numeric_cols:
            stats[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'count': int(df[col].count())
            }
        
        self.cache.set(cache_key, stats)
        return stats
    
    def validate_columns(self, df: pd.DataFrame, 
                        required_columns: list) -> Tuple[bool, list]:
        """
        Validate that DataFrame contains required columns.
        
        Args:
            df: Input DataFrame
            required_columns: List of required column names
            
        Returns:
            Tuple of (all_present, missing_columns)
        """
        df_columns = set(df.columns)
        required = set(required_columns)
        missing = list(required - df_columns)
        
        return len(missing) == 0, missing
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.current_df_id = None
        logger.info("Data service cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


# Global service instance
_data_service_instance = None


def get_data_service() -> DataService:
    """Get or create the global data service instance."""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataService()
    return _data_service_instance