"""
Enhanced UI callbacks for desktop-optimized MELD Visualizer interface.
Handles tab navigation, user feedback, loading states, and progress indicators.
"""

import logging
from typing import Dict, Any, List, Optional
import json
import time

from dash import Input, Output, State, callback, clientside_callback, ClientsideFunction, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from ..core.enhanced_ui import UserFeedbackManager

logger = logging.getLogger(__name__)


def register_enhanced_ui_callbacks(app):
    """Register all enhanced UI callbacks."""
    
    register_tab_navigation_callbacks(app)
    register_loading_state_callbacks(app)
    register_toast_notification_callbacks(app)
    register_progress_indicator_callbacks(app)
    register_control_panel_callbacks(app)


def register_tab_navigation_callbacks(app):
    """Register callbacks for enhanced tab navigation."""
    
    # Tab scrolling functionality (client-side)
    clientside_callback(
        """
        function(left_clicks, right_clicks) {
            const scrollContainer = document.querySelector('.enhanced-tabs-scroll-container');
            if (!scrollContainer) return [false, false];
            
            // Calculate scroll amount based on container width
            const scrollAmount = Math.min(200, scrollContainer.clientWidth * 0.3);
            
            // Handle left scroll
            if (left_clicks && left_clicks > 0) {
                scrollContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            }
            
            // Handle right scroll
            if (right_clicks && right_clicks > 0) {
                scrollContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            }
            
            // Update button states after scroll
            setTimeout(() => {
                const isAtStart = scrollContainer.scrollLeft <= 0;
                const isAtEnd = scrollContainer.scrollLeft >= 
                    scrollContainer.scrollWidth - scrollContainer.clientWidth - 1;
                
                const leftBtn = document.getElementById('tab-scroll-left');
                const rightBtn = document.getElementById('tab-scroll-right');
                
                if (leftBtn) leftBtn.disabled = isAtStart;
                if (rightBtn) rightBtn.disabled = isAtEnd;
            }, 300);
            
            return [false, false];
        }
        """,
        [Output('tab-scroll-left', 'disabled', allow_duplicate=True),
         Output('tab-scroll-right', 'disabled', allow_duplicate=True)],
        [Input('tab-scroll-left', 'n_clicks'),
         Input('tab-scroll-right', 'n_clicks')],
        prevent_initial_call=True
    )
    
    # Tab content switching
    @callback(
        Output('tab-content', 'children'),
        Input('enhanced-tabs', 'active_tab')
    )
    def update_tab_content(active_tab):
        """Update tab content based on active tab."""
        try:
            # This will be handled by the Dash Bootstrap Components Tabs
            # The content is already defined in the tab structure
            return []
        except Exception as e:
            logger.error(f"Error updating tab content: {e}")
            return []


def register_loading_state_callbacks(app):
    """Register callbacks for loading state management."""
    
    # Global loading state management (client-side)
    clientside_callback(
        """
        function(loading_state) {
            if (!loading_state) return window.dash_clientside.no_update;
            
            if (window.dashUtils && loading_state.show !== undefined) {
                if (loading_state.show) {
                    window.dashUtils.showLoading(loading_state.message || 'Processing...');
                } else {
                    window.dashUtils.hideLoading();
                }
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('loading-overlay', 'className'),
        Input('loading-state-store', 'data'),
        prevent_initial_call=True
    )
    
    # Show loading for file uploads
    @callback(
        Output('loading-state-store', 'data', allow_duplicate=True),
        [Input('upload-data', 'contents'),
         Input('upload-gcode', 'contents')],
        prevent_initial_call=True
    )
    def show_loading_on_upload(csv_contents, gcode_contents):
        """Show loading overlay when files are uploaded."""
        try:
            if csv_contents or gcode_contents:
                return {'show': True, 'message': 'Processing uploaded file...'}
            return {'show': False, 'message': ''}
        except Exception as e:
            logger.error(f"Error in upload loading callback: {e}")
            return {'show': False, 'message': ''}
    
    # Hide loading after data processing
    @callback(
        Output('loading-state-store', 'data', allow_duplicate=True),
        [Input('store-main-df', 'data'),
         Input('store-gcode-df', 'data')],
        prevent_initial_call=True
    )
    def hide_loading_after_processing(main_data, gcode_data):
        """Hide loading overlay after data is processed."""
        try:
            # Hide loading if data is available
            if main_data or gcode_data:
                return {'show': False, 'message': ''}
            return {'show': False, 'message': ''}
        except Exception as e:
            logger.error(f"Error in processing loading callback: {e}")
            return {'show': False, 'message': ''}


def register_toast_notification_callbacks(app):
    """Register callbacks for toast notifications."""
    
    # Toast notification display (client-side)
    clientside_callback(
        """
        function(toast_trigger, ui_state) {
            if (!toast_trigger || toast_trigger === 0) {
                return window.dash_clientside.no_update;
            }
            
            if (window.dashUtils && ui_state && ui_state.last_toast) {
                window.dashUtils.showToast(ui_state.last_toast);
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('toast-container', 'className'),
        [Input('toast-trigger-store', 'data'),
         State('ui-state-store', 'data')],
        prevent_initial_call=True
    )
    
    # Success toast for file uploads
    @callback(
        [Output('toast-trigger-store', 'data', allow_duplicate=True),
         Output('ui-state-store', 'data', allow_duplicate=True)],
        [Input('output-filename', 'children'),
         Input('gcode-filename-alert', 'is_open')],
        [State('toast-trigger-store', 'data'),
         State('ui-state-store', 'data')],
        prevent_initial_call=True
    )
    def show_upload_success_toast(filename, gcode_alert, current_trigger, ui_state):
        """Show success toast when files are successfully uploaded."""
        try:
            if not ui_state:
                ui_state = {}
            
            # Check if a file was successfully loaded
            if isinstance(filename, str) and "Please upload" not in filename:
                toast_config = UserFeedbackManager.create_toast_component(
                    toast_type="success",
                    title="File Loaded",
                    message=f"Successfully loaded: {filename}",
                    duration=4000
                )
                ui_state['last_toast'] = toast_config
                return current_trigger + 1, ui_state
            
            # Check for G-code file upload
            if gcode_alert:
                toast_config = UserFeedbackManager.create_toast_component(
                    toast_type="success",
                    title="G-code Loaded",
                    message="G-code file successfully loaded and ready for visualization",
                    duration=4000
                )
                ui_state['last_toast'] = toast_config
                return current_trigger + 1, ui_state
            
            return current_trigger, ui_state
            
        except Exception as e:
            logger.error(f"Error in upload success toast: {e}")
            return current_trigger, ui_state
    
    # Error toast for configuration warnings
    @callback(
        [Output('toast-trigger-store', 'data', allow_duplicate=True),
         Output('ui-state-store', 'data', allow_duplicate=True)],
        Input('config-warning-alert', 'is_open'),
        [State('config-warning-alert', 'children'),
         State('toast-trigger-store', 'data'),
         State('ui-state-store', 'data')],
        prevent_initial_call=True
    )
    def show_warning_toast(is_open, alert_children, current_trigger, ui_state):
        """Show warning toast for configuration issues."""
        try:
            if not ui_state:
                ui_state = {}
            
            if is_open and alert_children:
                # Extract warning message
                warning_text = str(alert_children) if alert_children else "Configuration warning"
                
                toast_config = UserFeedbackManager.create_toast_component(
                    toast_type="warning",
                    title="Configuration Warning",
                    message=warning_text,
                    duration=6000
                )
                ui_state['last_toast'] = toast_config
                return current_trigger + 1, ui_state
            
            return current_trigger, ui_state
            
        except Exception as e:
            logger.error(f"Error in warning toast: {e}")
            return current_trigger, ui_state
    
    # Success toast for configuration saves
    @callback(
        [Output('toast-trigger-store', 'data', allow_duplicate=True),
         Output('ui-state-store', 'data', allow_duplicate=True)],
        Input('save-config-alert', 'is_open'),
        [State('toast-trigger-store', 'data'),
         State('ui-state-store', 'data')],
        prevent_initial_call=True
    )
    def show_config_save_toast(is_open, current_trigger, ui_state):
        """Show success toast when configuration is saved."""
        try:
            if not ui_state:
                ui_state = {}
            
            if is_open:
                toast_config = UserFeedbackManager.create_toast_component(
                    toast_type="success",
                    title="Settings Saved",
                    message="Configuration has been saved successfully!",
                    duration=3000
                )
                ui_state['last_toast'] = toast_config
                return current_trigger + 1, ui_state
            
            return current_trigger, ui_state
            
        except Exception as e:
            logger.error(f"Error in config save toast: {e}")
            return current_trigger, ui_state


def register_progress_indicator_callbacks(app):
    """Register callbacks for progress indicators."""
    
    # Progress update system (client-side)
    clientside_callback(
        """
        function(progress_data) {
            if (!progress_data || !window.dashUtils) {
                return window.dash_clientside.no_update;
            }
            
            if (progress_data.id && progress_data.value !== undefined) {
                window.dashUtils.updateProgress(
                    progress_data.id, 
                    progress_data.value, 
                    progress_data.max || 100
                );
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('ui-state-store', 'modified_timestamp'),
        Input('ui-state-store', 'data'),
        prevent_initial_call=True
    )


def register_control_panel_callbacks(app):
    """Register callbacks for enhanced control panels."""
    
    # Control panel collapse/expand state management (client-side)
    clientside_callback(
        """
        function(ui_state) {
            if (!ui_state || !ui_state.panel_states) {
                return window.dash_clientside.no_update;
            }
            
            // Update panel collapse states
            Object.keys(ui_state.panel_states).forEach(panelId => {
                const header = document.querySelector(`#${panelId}-header`);
                const body = document.querySelector(`#${panelId}-body`);
                
                if (header && body) {
                    const isCollapsed = ui_state.panel_states[panelId].collapsed;
                    if (isCollapsed) {
                        header.classList.add('collapsed');
                        body.classList.remove('show');
                    } else {
                        header.classList.remove('collapsed');
                        body.classList.add('show');
                    }
                }
            });
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('ui-state-store', 'modified_timestamp', allow_duplicate=True),
        Input('ui-state-store', 'data'),
        prevent_initial_call=True
    )
    
    # Responsive layout adjustments based on viewport
    @callback(
        Output('ui-state-store', 'data', allow_duplicate=True),
        Input('viewport-dimensions', 'data'),
        State('ui-state-store', 'data'),
        prevent_initial_call=True
    )
    def update_responsive_layout(viewport_data, ui_state):
        """Update UI state based on viewport dimensions for responsive layout."""
        try:
            if not ui_state:
                ui_state = {}
            
            if not viewport_data:
                return ui_state
            
            from ..core.enhanced_ui import ResponsiveLayoutManager
            
            viewport_width = viewport_data.get('width', 1920)
            layout_config = ResponsiveLayoutManager.get_layout_config(viewport_width)
            breakpoint_class = ResponsiveLayoutManager.get_desktop_breakpoint_class(viewport_width)
            
            ui_state.update({
                'viewport_width': viewport_width,
                'viewport_height': viewport_data.get('height', 1080),
                'layout_config': layout_config,
                'breakpoint_class': breakpoint_class,
                'responsive_updated': time.time()
            })
            
            return ui_state
            
        except Exception as e:
            logger.error(f"Error updating responsive layout: {e}")
            return ui_state or {}


def register_keyboard_navigation_callbacks(app):
    """Register callbacks for keyboard navigation enhancements."""
    
    # Keyboard navigation (client-side)
    clientside_callback(
        """
        function() {
            // This is handled entirely by the enhanced-ui.js file
            // Just ensuring the callback is registered
            return window.dash_clientside.no_update;
        }
        """,
        Output('ui-state-store', 'modified_timestamp', allow_duplicate=True),
        Input('enhanced-tabs', 'active_tab'),
        prevent_initial_call=True
    )


def register_accessibility_callbacks(app):
    """Register callbacks for accessibility enhancements."""
    
    # ARIA labels and states (client-side)
    clientside_callback(
        """
        function(active_tab) {
            if (!active_tab) return window.dash_clientside.no_update;
            
            // Update ARIA labels for active tab
            const tabs = document.querySelectorAll('.enhanced-tabs .nav-link');
            tabs.forEach(tab => {
                tab.setAttribute('aria-selected', 'false');
                tab.removeAttribute('aria-current');
            });
            
            const activeTab = document.querySelector(`[data-value="${active_tab}"]`);
            if (activeTab) {
                activeTab.setAttribute('aria-selected', 'true');
                activeTab.setAttribute('aria-current', 'page');
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('enhanced-tabs', 'className'),
        Input('enhanced-tabs', 'active_tab'),
        prevent_initial_call=True
    )


def register_performance_callbacks(app):
    """Register callbacks for performance monitoring and optimization."""
    
    @callback(
        Output('ui-state-store', 'data', allow_duplicate=True),
        [Input('store-main-df', 'data'),
         Input('store-gcode-df', 'data')],
        [State('ui-state-store', 'data')],
        prevent_initial_call=True
    )
    def track_data_processing_performance(main_data, gcode_data, ui_state):
        """Track performance metrics for data processing operations."""
        try:
            if not ui_state:
                ui_state = {}
            
            # Track data processing time
            current_time = time.time()
            
            if main_data and 'data_load_start' in ui_state:
                processing_time = current_time - ui_state['data_load_start']
                ui_state['last_processing_time'] = processing_time
                
                # Show performance toast if processing took a while
                if processing_time > 2.0:  # More than 2 seconds
                    ui_state['performance_warning'] = True
            
            if gcode_data and 'gcode_load_start' in ui_state:
                processing_time = current_time - ui_state['gcode_load_start']
                ui_state['last_gcode_processing_time'] = processing_time
            
            return ui_state
            
        except Exception as e:
            logger.error(f"Error tracking performance: {e}")
            return ui_state or {}