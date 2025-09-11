# --- data_processing.py ---

# Standard library imports
import base64
import io
import logging
import re
from typing import Dict, List, Optional, Tuple, Union

# Third-party imports
import numpy as np
import pandas as pd
from numpy.typing import NDArray

# Local imports
from ..constants import (
    BEAD_LENGTH_MM,
    BEAD_RADIUS_MM,
    FEEDSTOCK_AREA_MM2,
    INCH_TO_MM,
    MAX_BEAD_THICKNESS_MM,
    MELD_FEED_VELOCITY_SCALE_FACTOR,
    MESH_VERTICES_PER_CROSS_SECTION,
    SECONDS_PER_MINUTE,
)
from ..utils.error_handling import (
    DataProcessingError,
    ErrorCode,
    ErrorContext,
    ErrorLogger,
    ValidationError,
    handle_errors,
)


@handle_errors(
    error_type=DataProcessingError,
    error_code=ErrorCode.DATA_PARSING_ERROR,
    user_message="Unable to process the CSV file. Please check the format and try again.",
)
def parse_contents(
    contents: str, filename: str
) -> Tuple[Optional[pd.DataFrame], Optional[str], bool]:
    """
    Parses the contents of an uploaded CSV file with standardized error handling.

    Args:
        contents (str): The base64 encoded string of the file content.
        filename (str): The name of the uploaded file.

    Returns:
        tuple: A tuple containing (DataFrame, error_message, unit_conversion_flag).
               The DataFrame is None if an error occurs.

    Raises:
        DataProcessingError: For file parsing and validation errors
        ValidationError: For data validation errors
    """
    logger: logging.Logger = logging.getLogger(__name__)

    if not contents:
        raise ValidationError(
            "No file content provided",
            error_code=ErrorCode.INVALID_INPUT,
            context={"filename": filename},
        )

    # Import security utilities for file validation
    from ..utils.security_utils import FileValidator

    # Validate file upload for security
    is_valid: bool
    error_msg: Optional[str]
    is_valid, error_msg = FileValidator.validate_file_upload(contents, filename)
    if not is_valid:
        raise DataProcessingError(
            f"File validation failed: {error_msg}",
            error_code=ErrorCode.FILE_VALIDATION_ERROR,
            context={"filename": filename, "validation_error": error_msg},
        )

    with ErrorContext("CSV parsing", logger, error_code=ErrorCode.DATA_PARSING_ERROR):
        _, content_string = contents.split(",")
        decoded: bytes = base64.b64decode(content_string)

        if "csv" not in filename.lower():
            raise ValidationError(
                f"Invalid file type: {filename}. Only CSV files are supported.",
                error_code=ErrorCode.FILE_FORMAT_ERROR,
                context={"filename": filename, "expected_type": "csv"},
            )

        df: pd.DataFrame = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

        if df.empty:
            raise ValidationError(
                "CSV file is empty or contains no valid data",
                error_code=ErrorCode.DATA_VALIDATION_ERROR,
                context={"filename": filename, "rows": 0},
            )

        ErrorLogger.log_info(
            logger, f"Successfully parsed CSV with {len(df)} rows", {"filename": filename}
        )

        # Handle Time column - check if Date column exists
        if "Date" in df.columns and "Time" in df.columns:
            try:
                df["Time"] = pd.to_datetime(df["Date"] + " " + df["Time"])
            except Exception as e:
                ErrorLogger.log_warning(
                    logger,
                    f"Failed to parse Date/Time columns, creating synthetic timestamps: {e}",
                    {"filename": filename},
                )
                df["Time"] = pd.date_range(start="2024-01-01", periods=len(df), freq="s")
        elif "Time" in df.columns:
            try:
                df["Time"] = pd.to_datetime(df["Time"])
            except Exception as e:
                ErrorLogger.log_warning(
                    logger,
                    f"Failed to parse Time column, creating synthetic timestamps: {e}",
                    {"filename": filename},
                )
                df["Time"] = pd.date_range(start="2024-01-01", periods=len(df), freq="s")
        else:
            # Create synthetic timestamps if no Time column exists
            df["Time"] = pd.date_range(start="2024-01-01", periods=len(df), freq="s")
            ErrorLogger.log_info(logger, "No Time column found, created synthetic timestamps")

        df["TimeInSeconds"] = (df["Time"] - df["Time"].min()).dt.total_seconds()

        converted_units: bool = False
        # Check for imperial units (inches/sec) and convert to metric (mm/sec)
        if "FeedVel" in df.columns:
            df_active_check: pd.DataFrame = df[df["FeedVel"] > 0]
            if not df_active_check.empty and df_active_check["FeedVel"].max() <= 100:
                converted_units = True
                cols_to_convert: List[str] = [
                    "XPos",
                    "YPos",
                    "ZPos",
                    "FeedVel",
                    "PathVel",
                    "XVel",
                    "YVel",
                    "ZVel",
                ]
                for col in [c for c in cols_to_convert if c in df.columns]:
                    df[col] *= INCH_TO_MM
                ErrorLogger.log_info(
                    logger,
                    f"Converted imperial units to metric for {len([c for c in cols_to_convert if c in df.columns])} columns",
                )

        return df, None, converted_units


@handle_errors(
    error_type=DataProcessingError,
    error_code=ErrorCode.GCODE_PARSING_ERROR,
    user_message="Unable to process the G-code file. Please check the format and try again.",
)
def parse_gcode_file(
    contents: str, filename: str
) -> Tuple[Optional[pd.DataFrame], Optional[str], bool]:
    """
    Parses the contents of an uploaded G-code (.nc) file and simulates the toolpath.
    This creates a DataFrame compatible with the existing plotting functions.

    Args:
        contents (str): The base64 encoded string of the file content.
        filename (str): The name of the uploaded file.

    Returns:
        tuple: A tuple containing (DataFrame, error_message, unit_conversion_flag).
               The DataFrame is None if an error occurs.

    Raises:
        DataProcessingError: For G-code parsing and simulation errors
        ValidationError: For data validation errors
    """
    logger: logging.Logger = logging.getLogger(__name__)

    if not contents:
        raise ValidationError(
            "No G-code file content provided",
            error_code=ErrorCode.INVALID_INPUT,
            context={"filename": filename},
        )

    # Import security utilities for file validation
    from ..utils.security_utils import FileValidator

    # Validate file upload for security
    is_valid: bool
    error_msg: Optional[str]
    is_valid, error_msg = FileValidator.validate_file_upload(contents, filename)
    if not is_valid:
        raise DataProcessingError(
            f"G-code file validation failed: {error_msg}",
            error_code=ErrorCode.FILE_VALIDATION_ERROR,
            context={"filename": filename, "validation_error": error_msg},
        )

    with ErrorContext("G-code decoding", logger, error_code=ErrorCode.GCODE_PARSING_ERROR):
        _, content_string = contents.split(",")
        decoded: bytes = base64.b64decode(content_string)
        gcode_text: str = decoded.decode("utf-8")
        lines: List[str] = io.StringIO(gcode_text).readlines()

        ErrorLogger.log_info(
            logger, f"Successfully decoded G-code with {len(lines)} lines", {"filename": filename}
        )

    # Import security utilities for safe G-code parsing
    from ..utils.security_utils import secure_parse_gcode

    # First sanitize the content to prevent ReDoS
    sanitized_result, error = secure_parse_gcode(decoded.decode("utf-8", errors="ignore"))
    if error or sanitized_result is None:
        return None, error or "Failed to parse G-code content", False

    # Convert to List[str] with proper type checking
    sanitized_lines: List[str] = [str(line) for line in sanitized_result]

    # Safe regex pattern with bounded repetition
    gcode_word_re: re.Pattern[str] = re.compile(r"([A-Z])([-+]?\d{0,10}\.?\d{0,6})")

    # Machine state
    state: Dict[str, Union[Dict[str, float], float, bool, int]] = {
        "current_pos": {"X": 0.0, "Y": 0.0, "Z": 0.0},
        "feed_vel": 0.0,  # Material feed velocity (from M34 S...)
        "path_vel": 0.0,  # Tool head velocity (from G1 F...)
        "extrusion_on": False,
        "time_counter": 0.0,
        "gcode_mode": 0,  # 0 for G0 (rapid), 1 for G1 (linear feed)
    }
    path_points: List[Dict[str, float]] = []

    # Add an initial point at the origin to start the path
    current_pos: Dict[str, float] = state["current_pos"]  # type: ignore
    initial_point: Dict[str, float] = {
        "XPos": current_pos["X"],
        "YPos": current_pos["Y"],
        "ZPos": current_pos["Z"],
        "FeedVel": 0,
        "PathVel": 0,
        "TimeInSeconds": 0,
    }
    path_points.append(initial_point)

    with ErrorContext("G-code simulation", logger, error_code=ErrorCode.GCODE_PARSING_ERROR):
        # Use sanitized lines instead of raw lines
        for line_num, line in enumerate(sanitized_lines, 1):
            # Line is already sanitized and uppercased
            if not line:
                continue

            words: Dict[str, str] = dict(gcode_word_re.findall(line))

            # Handle state-changing M-Codes and G-Codes
            if "M" in words:
                m_code: int = int(float(words["M"]))
                if m_code == 34:
                    state["extrusion_on"] = True
                    if "S" in words:
                        # Per documentation: S value is mm/min x 10
                        state["feed_vel"] = float(words["S"]) / MELD_FEED_VELOCITY_SCALE_FACTOR
                elif m_code == 35:
                    state["extrusion_on"] = False

            if "G" in words:
                g_code: int = int(float(words["G"]))
                if g_code in [0, 1]:
                    state["gcode_mode"] = g_code

                    # This is a movement command, so we generate a new point in the path
                    current_pos_dict: Dict[str, float] = state["current_pos"]  # type: ignore
                    target_pos: Dict[str, float] = current_pos_dict.copy()

                    # Update target position based on modal X, Y, Z, and F values
                    if "X" in words:
                        target_pos["X"] = float(words["X"])
                    if "Y" in words:
                        target_pos["Y"] = float(words["Y"])
                    if "Z" in words:
                        target_pos["Z"] = float(words["Z"])
                    if "F" in words:
                        state["path_vel"] = float(words["F"])

                    current_pos_dict = state["current_pos"]  # type: ignore
                    p1: NDArray[np.float64] = np.array(list(current_pos_dict.values()))
                    p2: NDArray[np.float64] = np.array(list(target_pos.values()))
                    distance: float = float(np.linalg.norm(p2 - p1))

                    time_segment_seconds: float = 0
                    path_vel: float = state["path_vel"]  # type: ignore
                    if distance > 1e-9 and path_vel > 1e-9:
                        # F is in mm/min, so we convert segment time to seconds
                        time_segment_seconds = (distance / path_vel) * SECONDS_PER_MINUTE
                    time_counter: float = float(state["time_counter"])  # type: ignore
                    state["time_counter"] = time_counter + time_segment_seconds

                    # Extrusion only occurs during G1 moves
                    extrusion_on: bool = state["extrusion_on"]  # type: ignore
                    gcode_mode: int = state["gcode_mode"]  # type: ignore
                    feed_vel: float = state["feed_vel"]  # type: ignore
                    current_feed: float = feed_vel if extrusion_on and gcode_mode == 1 else 0

                    # Create the new data point for our DataFrame
                    new_point: Dict[str, float] = {
                        "XPos": target_pos["X"],
                        "YPos": target_pos["Y"],
                        "ZPos": target_pos["Z"],
                        "FeedVel": current_feed,
                        "PathVel": path_vel,
                        "TimeInSeconds": float(state["time_counter"]),  # type: ignore
                    }
                    path_points.append(new_point)

                    # Update the machine's current position for the next iteration
                    state["current_pos"] = target_pos

    if len(path_points) <= 1:
        raise ValidationError(
            "No valid G-code movement commands (G0/G1) were found in file",
            error_code=ErrorCode.GCODE_PARSING_ERROR,
            context={
                "filename": filename,
                "total_lines": len(sanitized_lines),
                "path_points": len(path_points),
            },
        )

    df: pd.DataFrame = pd.DataFrame(path_points)

    # Add synthetic Date/Time columns for compatibility with the 2D time plotter
    start_time: pd.Timestamp = pd.to_datetime("2025-01-01T00:00:00")
    df["Time"] = df["TimeInSeconds"].apply(lambda s: start_time + pd.to_timedelta(s, unit="s"))
    df["Date"] = df["Time"].dt.strftime("%Y-%m-%d")

    # Add placeholder columns that exist in the CSV but not G-code, for compatibility
    placeholder_columns: List[str] = ["SpinVel", "ToolTemp", "SpinTrq", "SpinPwr", "FeedTrq", "FRO"]
    for col in placeholder_columns:
        if col not in df.columns:
            df[col] = 0

    ErrorLogger.log_info(
        logger,
        f"Successfully parsed G-code file with {len(path_points)} movement commands",
        {"filename": filename, "lines_processed": len(sanitized_lines)},
    )

    return df, f"Successfully parsed G-code file: {filename}", False


def get_cross_section_vertices(
    p: NDArray[np.float64],
    v_dir: NDArray[np.float64],
    T: float,
    L: float,
    R: float,
    N: int = MESH_VERTICES_PER_CROSS_SECTION,
) -> NDArray[np.float64]:
    """
    Calculates the vertices of a single cross-section for the mesh.
    This defines the shape of the extruded bead at a single point.
    """
    if np.linalg.norm(v_dir) > 1e-9:
        v_dir = v_dir / np.linalg.norm(v_dir)
    else:
        # Default to a vertical direction if the direction vector is zero
        v_dir = np.array([0, 1, 0], dtype=np.float64)

    z_axis: NDArray[np.float64] = np.array([0, 0, 1], dtype=np.float64)
    h_vec: NDArray[np.float64] = np.cross(v_dir, z_axis)
    if np.linalg.norm(h_vec) < 1e-6:
        h_vec = np.array([1, 0, 0], dtype=np.float64)  # Fallback for vertical toolpaths
    h_vec = h_vec / np.linalg.norm(h_vec)
    u_vec: NDArray[np.float64] = np.cross(h_vec, v_dir)

    vertices: List[NDArray[np.float64]] = []
    half_N: int = N // 2
    # First semi-circle
    center_s1: NDArray[np.float64] = p - h_vec * T / 2.0
    for i in range(half_N):
        angle: float = np.pi / 2 + (np.pi * i) / (half_N - 1)
        vertex: NDArray[np.float64] = center_s1 + R * (
            np.cos(angle) * h_vec + np.sin(angle) * u_vec
        )
        vertices.append(vertex)
    # Second semi-circle
    center_s2: NDArray[np.float64] = p + h_vec * T / 2.0
    for i in range(half_N):
        angle = -np.pi / 2 + (np.pi * i) / (half_N - 1)
        vertex = center_s2 + R * (np.cos(angle) * h_vec + np.sin(angle) * u_vec)
        vertices.append(vertex)

    return np.array(vertices)


def generate_volume_mesh(
    df_active: pd.DataFrame, color_col: str
) -> Optional[Dict[str, Union[NDArray[np.float64], NDArray[np.int32]]]]:
    """
    Generates the vertices, faces, and color data for a 3D mesh plot.

    Args:
        df_active (pd.DataFrame): DataFrame containing only active extrusion data.
        color_col (str): The name of the column to use for the mesh's color intensity.

    Returns:
        dict: A dictionary containing 'vertices', 'faces', and 'vertex_colors'.
              Returns None if the data is insufficient for mesh generation.
    """
    if df_active.empty:
        return None

    # Check for required columns for geometry calculation
    required_cols: set[str] = {"XPos", "YPos", "ZPos", "FeedVel", "PathVel"}
    if not required_cols.issubset(df_active.columns):
        missing_cols: set[str] = required_cols - set(df_active.columns)
        print(f"Error: Missing required columns for mesh generation: {', '.join(missing_cols)}")
        return None

    # --- Bead Geometry Constants ---
    # These values define the physical properties of the extrusion material.
    # Using constants from centralized location (constants.py)

    # Feedstock geometry - using constants from centralized location
    # MELD uses 0.5" × 0.5" square rod feedstock (defined in constants.py)

    # Legacy variable for backward compatibility (now represents square rod area)
    WIRE_AREA: float = FEEDSTOCK_AREA_MM2  # Corrected: actual square rod area, not diameter squared

    MAX_BEAD_THICKNESS: float = MAX_BEAD_THICKNESS_MM  # Safety clip for bead thickness (mm)
    POINTS_PER_SECTION: int = (
        MESH_VERTICES_PER_CROSS_SECTION  # Number of vertices in each cross-section circle
    )

    # --- Bead Geometry Calculation ---
    # This section calculates the cross-sectional geometry of the bead at each point
    # based on the principle of conservation of mass (volume in = volume out).
    # Bead Area = (Feed Velocity * Wire Area) / Path Velocity
    df_active = df_active.copy()
    df_active["Bead_Area"] = (df_active["FeedVel"] * WIRE_AREA) / df_active["PathVel"]
    # The thickness T is derived from the area of the idealized bead shape (rectangle + circle)
    df_active["T"] = (df_active["Bead_Area"] - (np.pi * BEAD_RADIUS_MM**2)) / BEAD_LENGTH_MM
    df_active["T_clipped"] = df_active["T"].clip(0.0, MAX_BEAD_THICKNESS)

    # --- Vertex and Face Generation ---
    points: NDArray[np.float64] = df_active[["XPos", "YPos", "ZPos"]].values
    geometries: NDArray[np.float64] = (
        df_active[["T_clipped"]].rename(columns={"T_clipped": "T"}).values
    )
    color_data: NDArray[np.float64] = df_active[color_col].values

    all_vertices: List[NDArray[np.float64]] = []
    all_faces: List[List[int]] = []
    vertex_colors: List[float] = []
    vertex_offset: int = 0
    N_points_per_section: int = (
        MESH_VERTICES_PER_CROSS_SECTION  # Number of vertices in each cross-section circle
    )

    for i in range(len(points) - 1):
        p1: NDArray[np.float64] = points[i]
        p2: NDArray[np.float64] = points[i + 1]
        g1: NDArray[np.float64] = geometries[i]
        g2: NDArray[np.float64] = geometries[i + 1]
        v_direction: NDArray[np.float64] = p2 - p1

        # Skip if points are identical (no direction)
        if np.linalg.norm(v_direction) < 1e-6:
            continue

        # Generate the vertices for the cross-sections at the start and end of the segment
        verts1: NDArray[np.float64] = get_cross_section_vertices(
            p1, v_direction, g1[0], BEAD_LENGTH_MM, BEAD_RADIUS_MM, N=POINTS_PER_SECTION
        )
        verts2: NDArray[np.float64] = get_cross_section_vertices(
            p2, v_direction, g2[0], BEAD_LENGTH_MM, BEAD_RADIUS_MM, N=POINTS_PER_SECTION
        )

        all_vertices.extend(verts1)
        all_vertices.extend(verts2)

        # Assign color data to the vertices
        vertex_colors.extend([color_data[i]] * N_points_per_section)
        vertex_colors.extend([color_data[i + 1]] * N_points_per_section)

        # Create faces connecting the two cross-sections
        for j in range(N_points_per_section):
            v1: int = vertex_offset + j
            v2: int = vertex_offset + (j + 1) % N_points_per_section
            v3: int = vertex_offset + N_points_per_section + j
            v4: int = vertex_offset + N_points_per_section + (j + 1) % N_points_per_section
            # Create two triangles for each quad
            all_faces.append([v1, v3, v4])
            all_faces.append([v1, v4, v2])
        vertex_offset += 2 * N_points_per_section

    if not all_vertices:
        return None

    return {
        "vertices": np.array(all_vertices),
        "faces": np.array(all_faces),
        "vertex_colors": np.array(vertex_colors),
    }
