#!/usr/bin/env python
"""
Test Trame server with proper threading to diagnose issues.
"""

import sys
import os
import time
import threading
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_trame_server():
    """Test the Trame server initialization."""
    print("\n" + "="*60)
    print("Trame Server Threading Test")
    print("="*60)
    
    # Set environment
    os.environ['PYVISTA_OFF_SCREEN'] = 'false'
    
    import pyvista as pv
    from trame.app import get_server
    from trame.widgets import vtk
    from trame.ui.vuetify import SinglePageLayout
    
    print("\n1. Testing threaded Trame server...")
    
    server_ready = threading.Event()
    server_error = threading.Event()
    error_msg = []
    
    def start_server():
        """Start server in its own thread."""
        try:
            print("   [Thread] Creating event loop...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            print("   [Thread] Creating PyVista plotter...")
            plotter = pv.Plotter(
                off_screen=False,
                notebook=False,
                window_size=[800, 600]
            )
            
            print("   [Thread] Adding test mesh...")
            sphere = pv.Sphere()
            plotter.add_mesh(sphere, color='red')
            
            print("   [Thread] Creating Trame server...")
            server = get_server("test_server")
            server.client_type = "vue2"
            
            print("   [Thread] Building UI...")
            with SinglePageLayout(server) as layout:
                layout.title.set_text("Test PyVista Viewer")
                with layout.content:
                    view = vtk.VtkLocalView(plotter.ren_win)
            
            print("   [Thread] Server ready!")
            server_ready.set()
            
            print("   [Thread] Starting server on port 8051...")
            server.start(
                port=8051,
                show=False,
                open_browser=False,
                exec_mode='task'
            )
            
        except Exception as e:
            print(f"   [Thread] ERROR: {e}")
            import traceback
            error_msg.append(traceback.format_exc())
            server_error.set()
    
    # Start the server thread
    print("2. Starting server thread...")
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    
    print("3. Waiting for server to be ready...")
    if server_ready.wait(timeout=10):
        print("   SUCCESS: Server is ready!")
        
        print("\n4. Server is running on http://localhost:8051")
        print("   Open this URL in your browser to see if it works")
        print("   Press Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n5. Shutting down...")
            
    elif server_error.is_set():
        print("   ERROR: Server failed to start")
        if error_msg:
            print("\nError details:")
            print(error_msg[0])
    else:
        print("   TIMEOUT: Server didn't respond in time")
    
    print("\n" + "="*60)
    print("Test complete")
    print("="*60)

if __name__ == "__main__":
    test_trame_server()