"""
Filter synchronization callbacks.
Handles range sliders and filter controls across the application.
"""

import logging
from dash import Input, Output, State, callback, no_update, ctx, MATCH
from dash.exceptions import PreventUpdate

from security_utils import InputValidator

logger = logging.getLogger(__name__)


def register_filter_callbacks(app=None):
    """Register filter-related callbacks."""
    
    @callback(
        Output({'type': 'range-slider', 'index': MATCH}, 'min'),
        Output({'type': 'range-slider', 'index': MATCH}, 'max'),
        Output({'type': 'range-slider', 'index': MATCH}, 'value'),
        Output({'type': 'lower-bound-input', 'index': MATCH}, 'value'),
        Output({'type': 'upper-bound-input', 'index': MATCH}, 'value'),
        Output({'type': 'slider-min-input', 'index': MATCH}, 'value'),
        Output({'type': 'slider-max-input', 'index': MATCH}, 'value'),
        Input({'type': 'range-slider', 'index': MATCH}, 'value'),
        Input({'type': 'lower-bound-input', 'index': MATCH}, 'value'),
        Input({'type': 'upper-bound-input', 'index': MATCH}, 'value'),
        Input({'type': 'slider-min-input', 'index': MATCH}, 'value'),
        Input({'type': 'slider-max-input', 'index': MATCH}, 'value'),
        Input('store-column-ranges', 'data'),
        State('custom-dropdown-filter', 'value'),
        prevent_initial_call=True
    )
    def sync_filter_controls(slider_val, lower_in, upper_in, s_min_in, s_max_in,
                            column_ranges, custom_filter_col):
        """
        Synchronize all filter components (slider and input boxes).
        Uses pattern-matching callback to handle multiple filter controls.
        """
        if not column_ranges:
            raise PreventUpdate

        # Identify which component triggered the callback
        triggered_id = ctx.triggered_id if isinstance(ctx.triggered_id, dict) else {
            'index': 'init', 'type': 'store'
        }
        triggered_prop_str = ctx.triggered[0]['prop_id']
        index = triggered_id.get('index')

        # Determine which data column to filter
        if index.startswith('zpos'):
            col_name = 'ZPos'
        elif index == 'time-2d':
            col_name = 'TimeInSeconds'
        elif index == 'custom':
            col_name = custom_filter_col
        else:
            col_name = 'ZPos'  # Fallback

        if not col_name:
            return no_update

        # Get absolute min/max for the column
        abs_min, abs_max = column_ranges.get(col_name, [0, 1])

        # Sanitize all inputs
        abs_min = InputValidator.sanitize_numeric_input(abs_min)
        abs_max = InputValidator.sanitize_numeric_input(abs_max)
        
        # Initialize output values
        out_s_min = InputValidator.sanitize_numeric_input(
            s_min_in, min_val=abs_min, max_val=abs_max, default=abs_min
        )
        out_s_max = InputValidator.sanitize_numeric_input(
            s_max_in, min_val=abs_min, max_val=abs_max, default=abs_max
        )
        
        if slider_val:
            out_l_bound, out_u_bound = slider_val
        else:
            out_l_bound, out_u_bound = abs_min, abs_max

        # Handle different trigger sources
        if triggered_prop_str.startswith('store-column-ranges'):
            # New file loaded - reset to full range
            out_s_min = abs_min
            out_s_max = abs_max
            out_l_bound = abs_min
            out_u_bound = abs_max
            
        elif 'range-slider' in triggered_prop_str:
            # Slider moved
            out_l_bound, out_u_bound = slider_val
            
        elif 'lower-bound-input' in triggered_prop_str and lower_in is not None:
            # Lower bound input changed
            out_l_bound = InputValidator.sanitize_numeric_input(
                lower_in, min_val=abs_min, max_val=out_u_bound, default=abs_min
            )
            out_s_min = min(out_l_bound, out_s_min)
            
        elif 'upper-bound-input' in triggered_prop_str and upper_in is not None:
            # Upper bound input changed
            out_u_bound = InputValidator.sanitize_numeric_input(
                upper_in, min_val=out_l_bound, max_val=abs_max, default=abs_max
            )
            out_s_max = max(out_u_bound, out_s_max)
            
        elif 'slider-min-input' in triggered_prop_str and s_min_in is not None:
            # Slider min input changed
            out_s_min = InputValidator.sanitize_numeric_input(
                s_min_in, min_val=abs_min, max_val=out_s_max, default=abs_min
            )
            
        elif 'slider-max-input' in triggered_prop_str and s_max_in is not None:
            # Slider max input changed
            out_s_max = InputValidator.sanitize_numeric_input(
                s_max_in, min_val=out_s_min, max_val=abs_max, default=abs_max
            )

        # Final validation
        if out_s_min > out_s_max:
            out_s_min = out_s_max
            
        out_l_bound = max(out_l_bound, out_s_min)
        out_u_bound = min(out_u_bound, out_s_max)
        
        if out_l_bound > out_u_bound:
            out_l_bound = out_u_bound

        logger.debug(f"Filter sync for {col_name}: [{out_l_bound:.2f}, {out_u_bound:.2f}]")

        return (out_s_min, out_s_max, [out_l_bound, out_u_bound],
                out_l_bound, out_u_bound, out_s_min, out_s_max)