"""Core modules for MELD Visualizer.

Contains the core functionality for:
- Layout and UI components
- Data processing and mesh generation
"""

# Optional imports - only import if dependencies are available
__all__ = []

try:
    from .layout import get_layout

    __all__.append("get_layout")
except ImportError:
    pass

try:
    from .data_processing import (
        generate_volume_mesh,
        get_cross_section_vertices,
        parse_contents,
        parse_gcode_file,
    )

    __all__.extend(
        ["parse_contents", "parse_gcode_file", "get_cross_section_vertices", "generate_volume_mesh"]
    )
except ImportError:
    pass
