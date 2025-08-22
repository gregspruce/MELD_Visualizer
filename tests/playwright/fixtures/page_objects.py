"""
Page Object Model for MELD Visualizer Dash Application
Provides reusable methods for interacting with UI elements during testing.
"""

class MeldVisualizerPage:
    """Main page object for the MELD Visualizer application"""
    
    def __init__(self, page):
        """
        Initialize with Playwright page object
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.base_url = "http://localhost:8050"
    
    # Navigation and Setup
    async def navigate(self):
        """Navigate to the main application page"""
        await self.page.goto(self.base_url)
        await self.page.wait_for_load_state('networkidle')
    
    async def wait_for_app_ready(self, timeout=30000):
        """Wait for the application to be fully loaded and ready"""
        # Wait for main content to appear
        await self.page.wait_for_selector('.dash-app-content', timeout=timeout)
        
        # Wait for any loading spinners to disappear
        loading_selectors = [
            '.dash-spinner',
            '[data-loading="true"]',
            '.loading-spinner'
        ]
        for selector in loading_selectors:
            try:
                await self.page.wait_for_selector(selector, state='detached', timeout=5000)
            except:
                pass  # Selector might not exist, which is fine
    
    # File Upload Operations
    async def upload_csv_file(self, file_path):
        """
        Upload a CSV file using the file upload component
        
        Args:
            file_path (str): Path to the CSV file to upload
        """
        upload_selector = '#upload-data input[type="file"]'
        await self.page.set_input_files(upload_selector, file_path)
    
    async def get_output_filename(self):
        """Get the displayed output filename text"""
        return await self.page.text_content('#output-filename')
    
    async def get_config_warning(self):
        """Get any configuration warning message"""
        warning_element = self.page.locator('#config-warning-alert')
        if await warning_element.is_visible():
            return await warning_element.text_content()
        return None
    
    # Graph and Visualization
    async def wait_for_graph_render(self, graph_id='main-graph', timeout=15000):
        """
        Wait for a specific graph to render completely
        
        Args:
            graph_id (str): ID of the graph element
            timeout (int): Timeout in milliseconds
        """
        # Wait for the graph container
        graph_selector = f'#{graph_id}'
        await self.page.wait_for_selector(graph_selector, timeout=timeout)
        
        # Wait for Plotly to render (look for the plotly graph div)
        plotly_selector = f'{graph_selector} .plotly-graph-div'
        await self.page.wait_for_selector(plotly_selector, timeout=timeout)
        
        # Wait a bit more for any animations to complete
        await self.page.wait_for_timeout(2000)
    
    async def take_graph_screenshot(self, graph_id='main-graph', filename='graph_screenshot.png'):
        """
        Take a screenshot of a specific graph
        
        Args:
            graph_id (str): ID of the graph element
            filename (str): Output filename for the screenshot
        """
        graph_element = self.page.locator(f'#{graph_id}')
        await graph_element.screenshot(path=f'../reports/{filename}')
    
    # Tab Navigation
    async def click_tab(self, tab_index=0):
        """
        Click on a specific tab
        
        Args:
            tab_index (int): Index of the tab to click (0-based)
        """
        tab_selector = f'.nav-tabs .nav-link:nth-child({tab_index + 1})'
        await self.page.click(tab_selector)
        await self.page.wait_for_timeout(1000)  # Wait for tab content to load
    
    async def get_active_tab_title(self):
        """Get the title of the currently active tab"""
        active_tab = self.page.locator('.nav-tabs .nav-link.active')
        return await active_tab.text_content()
    
    # Filter Controls
    async def set_range_slider(self, control_prefix, min_value, max_value):
        """
        Set values for a range slider control
        
        Args:
            control_prefix (str): The control ID prefix
            min_value (float): Minimum value for the range
            max_value (float): Maximum value for the range
        """
        # Set lower bound
        lower_input = f'#\{{"type":"lower-bound-input","index":"{control_prefix}"\}}'
        await self.page.fill(lower_input, str(min_value))
        
        # Set upper bound
        upper_input = f'#\{{"type":"upper-bound-input","index":"{control_prefix}"\}}'
        await self.page.fill(upper_input, str(max_value))
        
        # Trigger change event
        await self.page.press(upper_input, 'Enter')
    
    async def set_color_range(self, control_prefix, min_color, max_color):
        """
        Set color range values
        
        Args:
            control_prefix (str): The control ID prefix
            min_color (str): Minimum color value
            max_color (str): Maximum color value
        """
        min_input = f'#\{{"type":"color-min-input","index":"{control_prefix}"\}}'
        max_input = f'#\{{"type":"color-max-input","index":"{control_prefix}"\}}'
        
        await self.page.fill(min_input, str(min_color))
        await self.page.fill(max_input, str(max_color))
    
    async def select_radio_option(self, radio_group_id, option_value):
        """
        Select a radio button option
        
        Args:
            radio_group_id (str): ID of the radio button group
            option_value (str): Value of the option to select
        """
        radio_selector = f'#{radio_group_id} input[value="{option_value}"]'
        await self.page.click(radio_selector)
    
    # Data Table Operations
    async def get_table_data(self, table_id='data-table'):
        """
        Get data from a Dash data table
        
        Args:
            table_id (str): ID of the data table
            
        Returns:
            list: Table data as list of dictionaries
        """
        # Wait for table to load
        table_selector = f'#{table_id}'
        await self.page.wait_for_selector(table_selector)
        
        # Extract table data using JavaScript
        table_data = await self.page.evaluate(f'''
            () => {{
                const table = document.querySelector('#{table_id}');
                if (!table) return [];
                
                const rows = table.querySelectorAll('tbody tr');
                const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
                
                return Array.from(rows).map(row => {{
                    const cells = row.querySelectorAll('td');
                    const rowData = {{}};
                    cells.forEach((cell, index) => {{
                        if (headers[index]) {{
                            rowData[headers[index]] = cell.textContent.trim();
                        }}
                    }});
                    return rowData;
                }});
            }}
        ''')
        
        return table_data
    
    async def sort_table_column(self, table_id, column_name):
        """
        Click on a table column header to sort
        
        Args:
            table_id (str): ID of the data table
            column_name (str): Name of the column to sort
        """
        column_header = f'#{table_id} th:has-text("{column_name}")'
        await self.page.click(column_header)
    
    # Export Operations
    async def export_data(self, format='csv'):
        """
        Trigger data export
        
        Args:
            format (str): Export format ('csv', 'json', etc.)
        """
        export_button = f'button[data-export-format="{format}"]'
        
        # Start waiting for download before clicking
        async with self.page.expect_download() as download_info:
            await self.page.click(export_button)
        
        download = await download_info.value
        return download
    
    # Theme and UI Controls
    async def change_theme(self, theme_name):
        """
        Change the application theme
        
        Args:
            theme_name (str): Name of the theme to apply
        """
        theme_selector = f'select#theme-selector'
        await self.page.select_option(theme_selector, theme_name)
    
    # Utility Methods
    async def get_console_errors(self):
        """Get any console errors from the page"""
        return await self.page.evaluate('window.console_errors || []')
    
    async def wait_for_no_loading_spinners(self, timeout=10000):
        """Wait for all loading spinners to disappear"""
        loading_selectors = [
            '.dash-spinner',
            '.loading',
            '[data-loading="true"]'
        ]
        
        for selector in loading_selectors:
            try:
                await self.page.wait_for_selector(selector, state='detached', timeout=timeout)
            except:
                pass  # Element might not exist
    
    async def get_viewport_size(self):
        """Get current viewport dimensions"""
        return await self.page.evaluate('({width: window.innerWidth, height: window.innerHeight})')
    
    async def set_viewport_size(self, width, height):
        """Set viewport size for responsive testing"""
        await self.page.set_viewport_size({'width': width, 'height': height})


class PerformancePage(MeldVisualizerPage):
    """Extended page object for performance testing"""
    
    async def measure_page_load_time(self):
        """Measure page load time from navigation start"""
        return await self.page.evaluate('''
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return navigation.loadEventEnd - navigation.navigationStart;
            }
        ''')
    
    async def measure_csv_upload_time(self, file_path):
        """
        Measure time taken to upload and process CSV file
        
        Args:
            file_path (str): Path to CSV file
            
        Returns:
            float: Upload and processing time in milliseconds
        """
        start_time = await self.page.evaluate('Date.now()')
        
        await self.upload_csv_file(file_path)
        await self.wait_for_graph_render()
        
        end_time = await self.page.evaluate('Date.now()')
        return end_time - start_time
    
    async def get_memory_usage(self):
        """Get current memory usage if available"""
        return await self.page.evaluate('''
            () => {
                if (performance.memory) {
                    return {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }
        ''')


class AccessibilityPage(MeldVisualizerPage):
    """Extended page object for accessibility testing"""
    
    async def check_keyboard_navigation(self):
        """Test keyboard navigation through interactive elements"""
        # Get all focusable elements
        focusable_elements = await self.page.locator('button, input, select, textarea, [tabindex]:not([tabindex="-1"])').all()
        
        results = []
        for i, element in enumerate(focusable_elements):
            await element.focus()
            is_focused = await element.evaluate('el => document.activeElement === el')
            results.append({
                'index': i,
                'focused': is_focused,
                'tag': await element.evaluate('el => el.tagName'),
                'id': await element.get_attribute('id'),
                'class': await element.get_attribute('class')
            })
        
        return results
    
    async def check_color_contrast(self):
        """Basic color contrast check for text elements"""
        return await self.page.evaluate('''
            () => {
                const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div, button, label');
                const results = [];
                
                textElements.forEach((el, index) => {
                    const styles = window.getComputedStyle(el);
                    const color = styles.color;
                    const backgroundColor = styles.backgroundColor;
                    
                    if (color && backgroundColor && el.textContent.trim()) {
                        results.push({
                            index,
                            element: el.tagName,
                            color,
                            backgroundColor,
                            text: el.textContent.trim().substring(0, 50)
                        });
                    }
                });
                
                return results;
            }
        ''')