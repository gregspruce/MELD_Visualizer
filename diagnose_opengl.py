#!/usr/bin/env python
"""
Diagnose OpenGL and PyVista rendering capabilities.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def diagnose_system():
    """Run comprehensive diagnostics."""
    print("\n" + "="*60)
    print("OpenGL and PyVista Diagnostics")
    print("="*60)
    
    # 1. Check PyVista backend
    print("\n1. Checking PyVista configuration...")
    try:
        import pyvista as pv
        print(f"   PyVista version: {pv.__version__}")
        print(f"   VTK version: {pv.vtk_version_info}")
        
        # Check plotting backend
        print(f"   Current backend: {pv.global_theme.jupyter_backend}")
        print(f"   Off screen: {pv.OFF_SCREEN}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 2. Test creating a plotter
    print("\n2. Testing PyVista plotter creation...")
    try:
        # Try without off_screen first
        plotter = pv.Plotter(off_screen=False, notebook=False)
        print("   SUCCESS: Created interactive plotter")
        
        # Check render window
        ren_win = plotter.ren_win
        print(f"   Render window class: {ren_win.__class__.__name__}")
        
        # Try to get OpenGL info
        plotter.add_mesh(pv.Sphere())
        plotter.show(auto_close=False, interactive=False)
        
        # Get renderer information
        renderer = plotter.renderer
        print(f"   Renderer: {renderer}")
        
        plotter.close()
        print("   Plotter closed successfully")
        
    except Exception as e:
        print(f"   FAILED: {e}")
        print("   Trying off-screen mode...")
        try:
            plotter = pv.Plotter(off_screen=True)
            print("   SUCCESS: Created off-screen plotter")
            plotter.close()
        except Exception as e2:
            print(f"   FAILED off-screen too: {e2}")
    
    # 3. Check VTK render window directly
    print("\n3. Testing VTK render window...")
    try:
        import vtk
        render_window = vtk.vtkRenderWindow()
        render_window.SetSize(300, 300)
        render_window.Render()
        print("   SUCCESS: VTK render window created and rendered")
        
        # Get OpenGL information
        render_window.MakeCurrent()
        info = render_window.ReportCapabilities()
        if info:
            print("   OpenGL Capabilities:")
            for line in info.split('\n')[:10]:  # First 10 lines
                if line.strip():
                    print(f"      {line.strip()}")
        
        render_window.Finalize()
        del render_window
        
    except Exception as e:
        print(f"   FAILED: {e}")
    
    # 4. Check environment variables
    print("\n4. Checking environment variables...")
    important_vars = [
        'PYVISTA_OFF_SCREEN',
        'PYVISTA_USE_PANEL', 
        'PYVISTA_PLOT_THEME',
        'DISPLAY',
        'VTK_GRAPHICS_BACKEND',
        'MESA_GL_VERSION_OVERRIDE'
    ]
    for var in important_vars:
        value = os.environ.get(var, "Not set")
        print(f"   {var}: {value}")
    
    # 5. Test Trame server initialization
    print("\n5. Testing Trame server...")
    try:
        from trame.app import get_server
        server = get_server("test_server")
        print(f"   SUCCESS: Created Trame server")
        print(f"   Server type: {server.__class__.__name__}")
        print(f"   Client type: {server.client_type}")
        
        # Don't actually start it, just test creation
        
    except Exception as e:
        print(f"   FAILED: {e}")
    
    # 6. Check if we're in a remote/virtual environment
    print("\n6. Checking system environment...")
    print(f"   Platform: {sys.platform}")
    print(f"   Python: {sys.version}")
    
    # Check for WSL
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                print("   WARNING: Running in WSL - may have limited OpenGL support")
    except:
        pass
    
    # Check for RDP
    if os.environ.get('SESSIONNAME', '').startswith('RDP'):
        print("   WARNING: Running over RDP - may have limited OpenGL support")
    
    # 7. Try a simple Trame + PyVista combination
    print("\n7. Testing Trame + PyVista integration...")
    try:
        from trame.app import get_server
        from trame.widgets import vtk
        from trame.ui.vuetify import SinglePageLayout
        import pyvista as pv
        
        # Create plotter with specific settings for Windows
        plotter = pv.Plotter(
            window_size=[800, 600],
            notebook=False,
            off_screen=False  # Try interactive first
        )
        
        # Add a simple mesh
        sphere = pv.Sphere()
        plotter.add_mesh(sphere, color='red')
        
        # Create server
        server = get_server("test_pyvista_server")
        server.client_type = "vue2"
        
        # Create minimal UI
        with SinglePageLayout(server) as layout:
            with layout.content:
                view = vtk.VtkLocalView(plotter.ren_win)
        
        print("   SUCCESS: Trame + PyVista integration created")
        print("   Server ready to start on a port")
        
        # Clean up
        plotter.close()
        
    except Exception as e:
        print(f"   FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Diagnostics complete")
    print("="*60)
    
    print("\nRECOMMENDATIONS:")
    print("1. If VTK render window works but Trame doesn't, it's a server issue")
    print("2. If VTK fails, try updating graphics drivers")
    print("3. Consider setting PYVISTA_OFF_SCREEN=false explicitly")
    print("4. On Windows, ensure you're not running over RDP for best results")

if __name__ == "__main__":
    diagnose_system()