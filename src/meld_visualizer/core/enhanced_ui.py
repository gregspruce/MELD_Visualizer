"""
Enhanced UI components for desktop-optimized MELD Visualizer interface.
Provides improved tab navigation, control panels, loading states, and user feedback.
"""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from typing import List, Dict, Any, Optional
import uuid


class EnhancedUIComponents:
    """Factory class for creating enhanced UI components."""
    
    @staticmethod
    def create_enhanced_tabs(tabs_config: List[Dict[str, Any]], 
                           active_tab: Optional[str] = None) -> html.Div:
        """
        Create an enhanced tab navigation system with desktop-optimized overflow handling.
        
        Args:
            tabs_config: List of tab configurations with 'id', 'label', and 'content'
            active_tab: ID of the initially active tab
            
        Returns:
            html.Div: Enhanced tabs container with scroll buttons
        """
        tab_items = []
        for i, tab_config in enumerate(tabs_config):
            is_active = (tab_config['id'] == active_tab) or (active_tab is None and i == 0)
            
            tab_items.append(
                dbc.Tab(
                    label=tab_config['label'],
                    tab_id=tab_config['id'],
                    className="enhanced-tab-item",
                    active_tab_class_name="active",
                    children=tab_config.get('content', [])
                )
            )
        
        return html.Div([
            # Enhanced tabs container with scroll functionality
            html.Div([
                # Left scroll button
                html.Button([
                    html.I(className="fas fa-chevron-left")
                ], 
                id="tab-scroll-left", 
                className="tab-scroll-button left",
                disabled=True
                ),
                
                # Scrollable tabs container
                html.Div([
                    dbc.Tabs(
                        tab_items,
                        id="enhanced-tabs",
                        className="enhanced-tabs",
                        active_tab=active_tab or tabs_config[0]['id'] if tabs_config else None
                    )
                ], className="enhanced-tabs-scroll-container"),
                
                # Right scroll button
                html.Button([
                    html.I(className="fas fa-chevron-right")
                ], 
                id="tab-scroll-right", 
                className="tab-scroll-button right"
                ),
                
            ], className="enhanced-tabs-wrapper"),
            
            # Tab content area
            html.Div(id="tab-content", className="mt-4")
            
        ], className="enhanced-tabs-container")
    
    @staticmethod
    def create_control_panel(title: str, 
                           controls: List[html.Div], 
                           panel_id: Optional[str] = None,
                           collapsible: bool = True,
                           initial_collapsed: bool = False) -> html.Div:
        """
        Create a desktop-optimized control panel with visual grouping.
        
        Args:
            title: Panel title
            controls: List of control components
            panel_id: Unique ID for the panel
            collapsible: Whether panel can be collapsed
            initial_collapsed: Initial collapsed state
            
        Returns:
            html.Div: Enhanced control panel
        """
        if panel_id is None:
            panel_id = f"control-panel-{uuid.uuid4().hex[:8]}"
            
        header_class = "control-panel-header"
        if initial_collapsed:
            header_class += " collapsed"
            
        header_children = [title]
        if collapsible:
            header_children.append(
                html.I(className="fas fa-chevron-down collapse-icon")
            )
        
        return html.Div([
            # Panel header
            html.H5(
                header_children,
                className=header_class,
                id=f"{panel_id}-header",
                **({'data-bs-toggle': 'collapse', 
                    'data-bs-target': f'#{panel_id}-body'} if collapsible else {})
            ),
            
            # Panel body
            dbc.Collapse(
                html.Div(controls, className="control-panel-body"),
                id=f"{panel_id}-body",
                is_open=not initial_collapsed
            )
            
        ], className="enhanced-control-panel", id=panel_id)
    
    @staticmethod
    def create_control_group(title: str, 
                           controls: List[html.Div],
                           group_id: Optional[str] = None) -> html.Div:
        """
        Create a visually grouped set of related controls.
        
        Args:
            title: Group title
            controls: List of control components
            group_id: Unique ID for the group
            
        Returns:
            html.Div: Control group with visual styling
        """
        if group_id is None:
            group_id = f"control-group-{uuid.uuid4().hex[:8]}"
            
        return html.Fieldset([
            html.Legend(title, className="control-group-title"),
            *controls
        ], className="control-group", id=group_id)
    
    @staticmethod
    def create_enhanced_input_group(label: str, 
                                  input_component: html.Div,
                                  help_text: Optional[str] = None) -> html.Div:
        """
        Create an enhanced input group with consistent styling.
        
        Args:
            label: Input label text
            input_component: The input component (Input, Dropdown, etc.)
            help_text: Optional help text
            
        Returns:
            html.Div: Enhanced input group
        """
        components = [
            dbc.InputGroup([
                dbc.InputGroupText(label),
                input_component
            ], className="enhanced-input-group")
        ]
        
        if help_text:
            components.append(
                html.Small(help_text, className="text-muted form-text")
            )
        
        return html.Div(components, className="mb-3")
    
    @staticmethod
    def create_loading_overlay(message: str = "Processing...", 
                             overlay_id: str = "loading-overlay") -> html.Div:
        """
        Create a loading overlay for user feedback.
        
        Args:
            message: Loading message
            overlay_id: Unique ID for the overlay
            
        Returns:
            html.Div: Loading overlay component
        """
        return html.Div([
            html.Div([
                html.Div(className="loading-spinner"),
                html.P(message, className="loading-message")
            ], className="loading-content")
        ], id=overlay_id, className="loading-overlay")
    
    @staticmethod
    def create_progress_indicator(title: str,
                                progress_id: str,
                                initial_value: int = 0,
                                max_value: int = 100) -> html.Div:
        """
        Create a progress indicator with title.
        
        Args:
            title: Progress title
            progress_id: Unique ID for progress component
            initial_value: Initial progress value
            max_value: Maximum progress value
            
        Returns:
            html.Div: Progress indicator component
        """
        percentage = int((initial_value / max_value) * 100) if max_value > 0 else 0
        
        return html.Div([
            html.H6(title, className="progress-title"),
            html.Div([
                html.Div([
                    html.Span(f"{percentage}%", className="progress-text")
                ], 
                id=f"{progress_id}-bar",
                className="enhanced-progress-bar",
                style={'width': f'{percentage}%'})
            ], className="enhanced-progress"),
            
            # Hidden stores for progress tracking
            dcc.Store(id=f"{progress_id}-value", data=initial_value),
            dcc.Store(id=f"{progress_id}-max", data=max_value)
        ], className="progress-container", id=progress_id)
    
    @staticmethod
    def create_toast_container() -> html.Div:
        """
        Create a toast notification container.
        
        Returns:
            html.Div: Toast container positioned for desktop
        """
        return html.Div(
            id="toast-container",
            className="toast-container",
            children=[]
        )
    
    @staticmethod
    def create_enhanced_upload_area(upload_id: str,
                                  message: str = "Drag and Drop or Select a CSV File",
                                  accepted_types: str = ".csv,.nc,.gcode") -> dcc.Upload:
        """
        Create an enhanced upload area with better visual feedback.
        
        Args:
            upload_id: Unique ID for upload component
            message: Upload message
            accepted_types: Accepted file types
            
        Returns:
            dcc.Upload: Enhanced upload component
        """
        return dcc.Upload([
            html.Div([
                html.I(className="fas fa-cloud-upload-alt upload-icon"),
                html.Div(message, className="upload-text"),
                html.Div(f"Supported formats: {accepted_types}", className="upload-hint")
            ])
        ],
        id=upload_id,
        className="enhanced-upload-area",
        accept=accepted_types,
        multiple=False
        )


class UserFeedbackManager:
    """Manager for user feedback operations (toasts, loading states, etc.)."""
    
    @staticmethod
    def create_toast_component(toast_type: str = "info",
                             title: str = "Notification",
                             message: str = "",
                             duration: int = 5000,
                             toast_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a toast notification configuration.
        
        Args:
            toast_type: Type of toast (success, error, warning, info)
            title: Toast title
            message: Toast message
            duration: Auto-dismiss duration in milliseconds
            toast_id: Unique ID for the toast
            
        Returns:
            Dict: Toast configuration for client-side rendering
        """
        if toast_id is None:
            toast_id = f"toast-{uuid.uuid4().hex[:8]}"
            
        icon_map = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-triangle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        }
        
        return {
            'id': toast_id,
            'type': toast_type,
            'title': title,
            'message': message,
            'duration': duration,
            'icon': icon_map.get(toast_type, icon_map['info']),
            'timestamp': None  # Will be set client-side
        }


class ResponsiveLayoutManager:
    """Manager for responsive layout adjustments on desktop."""
    
    @staticmethod
    def get_desktop_breakpoint_class(viewport_width: int) -> str:
        """
        Get CSS class for desktop breakpoint.
        
        Args:
            viewport_width: Viewport width in pixels
            
        Returns:
            str: CSS class for the current breakpoint
        """
        if viewport_width >= 1920:
            return "desktop-large"
        elif viewport_width >= 1440:
            return "desktop-medium"
        elif viewport_width >= 1280:
            return "desktop-small"
        else:
            return "desktop-compact"
    
    @staticmethod
    def get_layout_config(viewport_width: int) -> Dict[str, Any]:
        """
        Get layout configuration for current viewport.
        
        Args:
            viewport_width: Viewport width in pixels
            
        Returns:
            Dict: Layout configuration
        """
        configs = {
            "desktop-large": {
                "columns_per_row": 2,
                "control_panel_width": 4,
                "plot_width": 8,
                "sidebar_collapsed": False
            },
            "desktop-medium": {
                "columns_per_row": 2,
                "control_panel_width": 5,
                "plot_width": 7,
                "sidebar_collapsed": False
            },
            "desktop-small": {
                "columns_per_row": 1,
                "control_panel_width": 6,
                "plot_width": 6,
                "sidebar_collapsed": True
            },
            "desktop-compact": {
                "columns_per_row": 1,
                "control_panel_width": 12,
                "plot_width": 12,
                "sidebar_collapsed": True
            }
        }
        
        breakpoint = ResponsiveLayoutManager.get_desktop_breakpoint_class(viewport_width)
        return configs.get(breakpoint, configs["desktop-compact"])