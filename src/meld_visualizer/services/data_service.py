"""
Data service for processing and managing MELD visualization data.
Integrates caching and optimized processing functions.
"""

# Standard library imports
import logging
import os
import sys
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

# Third-party imports
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from typing_extensions import Literal, TypeAlias, TypedDict

from ..constants import CHUNK_SIZE, MIN_FEED_VELOCITY, MIN_PATH_VELOCITY
from ..utils.security_utils import FileValidator, InputValidator

# Local imports
from .cache_service import CacheService, get_cache
from .file_service import FileService

# Volume components - imported with TYPE_CHECKING for mypy compatibility
if TYPE_CHECKING:
    from ..core.volume_calculations import VolumeCalculator
    from ..core.volume_mesh import MeshGenerator, VolumePlotter
else:
    from ..core.volume_calculations import VolumeCalculator
    from ..core.volume_mesh import MeshGenerator, VolumePlotter

# Try to import optimized functions, fallback to standard
try:
    # Import from reports directory at project root
    reports_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "reports"
    )
    sys.path.insert(0, reports_path)
    from data_processing_optimized import generate_volume_mesh_lod as generate_mesh_lod_legacy
    from data_processing_optimized import parse_contents_optimized as parse_contents_impl

    OPTIMIZED_AVAILABLE = True
except ImportError:
    from ..core.data_processing import parse_contents as parse_contents_impl

    OPTIMIZED_AVAILABLE = False
    generate_mesh_lod_legacy = None

logger = logging.getLogger(__name__)


# Type aliases for service layer patterns
NumericValue: TypeAlias = Union[int, float]
LODLevel: TypeAlias = Literal["high", "medium", "low"]
ParseResult: TypeAlias = Tuple[Optional[pd.DataFrame], Optional[str], bool]
ValidationResult: TypeAlias = Tuple[bool, List[str]]
FilterOperation: TypeAlias = Callable[[pd.DataFrame], pd.DataFrame]


# TypedDict structures for complex return types
class MeshData(TypedDict):
    """3D mesh data structure for volume visualization."""

    vertices: NDArray[np.float64]
    faces: NDArray[np.int32]
    colors: NDArray[np.float64]
    metadata: Dict[str, Any]


class ColumnStatistics(TypedDict):
    """Statistical data for numeric columns."""

    min: float
    max: float
    mean: float
    std: float
    count: int


class CacheStats(TypedDict):
    """Cache performance statistics."""

    hits: int
    misses: int
    hit_rate: float
    size_bytes: int
    max_size_bytes: int
    entry_count: int


class DataService:
    """
    Service for data processing operations with caching and optimization.
    """

    def __init__(self) -> None:
        """Initialize data service."""
        self.cache: CacheService = get_cache()
        self.file_service: FileService = FileService()
        self.current_df_id: Optional[str] = None

        # Initialize volume components
        self.volume_calculator: VolumeCalculator = VolumeCalculator()
        self.mesh_generator: MeshGenerator = MeshGenerator()
        self.volume_plotter: VolumePlotter = VolumePlotter()

        # Load calibration if available
        self._load_calibration()

        logger.info(f"DataService initialized (optimized: {OPTIMIZED_AVAILABLE})")

    def _load_calibration(self) -> None:
        """Load calibration from config file if available."""
        import json
        import os

        config_path = "config/volume_calibration.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)

                # Apply calibration
                if "calibration" in config:
                    cal = config["calibration"]
                    width_mult = cal.get("width_multiplier", 1.0)
                    self.volume_calculator.set_calibration(
                        correction_factor=cal.get("correction_factor", 1.0),
                        area_offset=cal.get("area_offset", 0.0),
                        width_multiplier=width_mult,
                    )
                    self.volume_plotter.calculator.set_calibration(
                        correction_factor=cal.get("correction_factor", 1.0),
                        area_offset=cal.get("area_offset", 0.0),
                        width_multiplier=width_mult,
                    )
                    logger.info(f"Loaded calibration: width_multiplier={width_mult:.3f}")
            except Exception as e:
                logger.warning(f"Failed to load calibration: {e}")

    def parse_file(self, contents: str, filename: str) -> ParseResult:
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
            # Ensure cached result matches expected type
            if isinstance(cached_result, tuple) and len(cached_result) == 3:
                return cached_result
            else:
                logger.warning("Cached result has unexpected format, re-parsing")

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
            (df["FeedVel"] > MIN_FEED_VELOCITY) & (df["PathVel"] > MIN_PATH_VELOCITY)
        ].copy()

        self.cache.set(cache_key, df_active)
        return df_active

    def filter_by_range(
        self, df: pd.DataFrame, column: str, min_val: NumericValue, max_val: NumericValue
    ) -> pd.DataFrame:
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
        return df[mask].copy()

    def generate_mesh(
        self, df: pd.DataFrame, color_column: str, lod: LODLevel = "high"
    ) -> Optional[MeshData]:
        """
        Generate 3D mesh with LOD support using new modular system.

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
            # Validate cached mesh data structure
            if isinstance(cached, dict) and all(
                k in cached for k in ["vertices", "faces", "colors", "metadata"]
            ):
                return cached  # type: ignore[return-value]
            else:
                logger.warning("Cached mesh data has unexpected format, regenerating")

        try:
            # Prepare data with volume calculations if needed
            if "Bead_Thickness_mm" not in df.columns:
                df = self.volume_calculator.process_dataframe(df)

            # Validate that volume calculations were successful
            if "Bead_Thickness_mm" not in df.columns:
                logger.error("Volume calculations failed - Bead_Thickness_mm column not created")
                return None

            # Check for valid thickness values
            thickness_values = df["Bead_Thickness_mm"]
            if thickness_values.isna().all() or (thickness_values <= 0).all():
                logger.error("No valid bead thickness values found after volume calculations")
                return None

            # Generate mesh using new modular system with width multiplier
            raw_mesh_data = self.mesh_generator.generate_mesh_lod(
                df,
                color_column,
                lod,
                self.volume_calculator.bead_geometry.length_mm,
                self.volume_calculator.bead_geometry.radius_mm,
                width_multiplier=self.volume_calculator.width_multiplier,
            )

        except Exception as e:
            logger.error(f"Error in mesh generation pipeline: {str(e)}", exc_info=True)
            return None

        # Convert raw mesh data to typed structure
        if raw_mesh_data is not None and isinstance(raw_mesh_data, dict):
            mesh_data: Optional[MeshData] = {
                "vertices": raw_mesh_data.get("vertices", np.array([])),
                "faces": raw_mesh_data.get("faces", np.array([])),
                "colors": raw_mesh_data.get("colors", np.array([])),
                "metadata": raw_mesh_data.get("metadata", {}),
            }
        else:
            mesh_data = None

        if mesh_data is not None:
            self.cache.set(cache_key, mesh_data)
            logger.info(f"Generated mesh with {len(mesh_data['vertices'])} vertices")

        return mesh_data

    def calculate_volume_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume calculations to DataFrame.

        Args:
            df: Input DataFrame with velocity columns

        Returns:
            DataFrame with added volume columns
        """
        return self.volume_calculator.process_dataframe(df)

    def set_volume_calibration(
        self, correction_factor: float = 1.0, area_offset: float = 0.0
    ) -> None:
        """
        Set calibration factors for volume calculations.

        Args:
            correction_factor: Multiplicative correction
            area_offset: Additive correction in mm²
        """
        self.volume_calculator.set_calibration(correction_factor, area_offset)
        self.volume_plotter.set_calibration(correction_factor, area_offset)
        logger.info(f"Volume calibration updated: factor={correction_factor}, offset={area_offset}")

    def process_in_chunks(
        self, df: pd.DataFrame, operation: FilterOperation, chunk_size: int = CHUNK_SIZE
    ) -> pd.DataFrame:
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

    def get_column_statistics(self, df: pd.DataFrame) -> Dict[str, ColumnStatistics]:
        """
        Get statistics for all numeric columns with caching.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary of column statistics
        """
        cache_key = self.cache._generate_key("stats", len(df), list(df.columns))
        cached = self.cache.get(cache_key)

        if cached is not None and isinstance(cached, dict):
            # Validate cached statistics structure
            try:
                validated_stats: Dict[str, ColumnStatistics] = {}
                for col, stats in cached.items():
                    if isinstance(stats, dict) and all(
                        k in stats for k in ["min", "max", "mean", "std", "count"]
                    ):
                        validated_stats[col] = ColumnStatistics(
                            min=float(stats["min"]),
                            max=float(stats["max"]),
                            mean=float(stats["mean"]),
                            std=float(stats["std"]),
                            count=int(stats["count"]),
                        )
                return validated_stats
            except (KeyError, TypeError, ValueError):
                logger.warning("Cached statistics have unexpected format, recalculating")
                # Fall through to recalculate

        numeric_cols = df.select_dtypes(include=np.number).columns
        stats = {}

        for col in numeric_cols:
            stats[col] = ColumnStatistics(
                min=float(df[col].min()),
                max=float(df[col].max()),
                mean=float(df[col].mean()),
                std=float(df[col].std()),
                count=int(df[col].count()),
            )

        self.cache.set(cache_key, stats)
        return stats

    def validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> ValidationResult:
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

    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics."""
        raw_stats = self.cache.get_stats()

        # Convert raw stats to typed structure
        if isinstance(raw_stats, dict):
            return CacheStats(
                hits=raw_stats.get("hits", 0),
                misses=raw_stats.get("misses", 0),
                hit_rate=raw_stats.get("hit_rate", 0.0),
                size_bytes=raw_stats.get("size_bytes", 0),
                max_size_bytes=raw_stats.get("max_size_bytes", 0),
                entry_count=raw_stats.get("entry_count", 0),
            )
        else:
            # Fallback for unexpected format
            return CacheStats(
                hits=0, misses=0, hit_rate=0.0, size_bytes=0, max_size_bytes=0, entry_count=0
            )


# Global service instance
_data_service_instance: Optional[DataService] = None


def get_data_service() -> DataService:
    """Get or create the global data service instance."""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataService()
    return _data_service_instance
