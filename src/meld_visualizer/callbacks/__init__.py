"""
Callbacks module for MELD Visualizer.
Organizes Dash callbacks by functional domain.
"""

# Import all callback registration functions
from .data_callbacks import register_data_callbacks
from .graph_callbacks import register_graph_callbacks
from .config_callbacks import register_config_callbacks
from .visualization_callbacks import register_visualization_callbacks
from .filter_callbacks import register_filter_callbacks
from .enhanced_ui_callbacks import register_enhanced_ui_callbacks
# from .pyvista_callbacks import register_pyvista_callbacks  # Full version - disabled
from .standalone_pyvista_callbacks import register_standalone_pyvista_callbacks

def register_all_callbacks(app=None):
    """
    Register all callbacks with the Dash app.
    
    Args:
        app: Dash app instance (optional if using @callback decorator)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Register callbacks from each module in dependency order
    try:
        logger.info("Registering data callbacks...")
        register_data_callbacks(app)
        
        logger.info("Registering config callbacks...")
        register_config_callbacks(app)
        
        logger.info("Registering filter callbacks...")
        register_filter_callbacks(app)
        
        logger.info("Registering graph callbacks...")
        register_graph_callbacks(app)
        
        logger.info("Registering visualization callbacks...")
        register_visualization_callbacks(app)
        
        logger.info("Registering standalone PyVista callbacks...")
        register_standalone_pyvista_callbacks(app)
        
        # Temporarily disabled - callbacks reference non-existent components
        # logger.info("Registering enhanced UI callbacks...")
        # register_enhanced_ui_callbacks(app)
        
        logger.info("All core callbacks registered successfully")
    except Exception as e:
        logger.error(f"Error registering callbacks: {e}")
        raise

# For backward compatibility
register_callbacks = register_all_callbacks

__all__ = [
    'register_all_callbacks',
    'register_callbacks',
    'register_data_callbacks',
    'register_graph_callbacks',
    'register_config_callbacks',
    'register_visualization_callbacks',
    'register_filter_callbacks',
    'register_enhanced_ui_callbacks',
    'register_standalone_pyvista_callbacks'
]