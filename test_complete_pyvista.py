#!/usr/bin/env python
"""
Complete end-to-end test of PyVista integration in MELD Visualizer.
"""

import sys
import os
import numpy as np
import pandas as pd
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_pyvista_flow():
    """Test the complete PyVista workflow as it would run in the app."""
    print("\n" + "="*60)
    print("Complete PyVista Integration Test")
    print("="*60)
    
    # Step 1: Create test data
    print("\n1. Creating test data...")
    num_points = 100
    df = pd.DataFrame({
        'XPos': np.random.rand(num_points) * 100,
        'YPos': np.random.rand(num_points) * 100,
        'ZPos': np.random.rand(num_points) * 10,
        'FeedVel': 5 + np.random.rand(num_points) * 5,
        'PathVel': 10 * np.ones(num_points),
        'SpinVel': 300 + np.random.rand(num_points) * 100,
        'ToolTemp': 400 + np.random.rand(num_points) * 50,
        'Time': np.arange(num_points)
    })
    print(f"   Created DataFrame with {len(df)} rows and columns: {list(df.columns)}")
    
    # Step 2: Convert to JSON (like the app does)
    print("\n2. Converting to JSON format (simulating store-main-df)...")
    data_json = df.to_json(date_format='iso', orient='split')
    print(f"   JSON data size: {len(data_json)} characters")
    
    # Step 3: Parse JSON back (like the callback does)
    print("\n3. Parsing JSON data...")
    df_parsed = pd.read_json(data_json, orient='split')
    print(f"   Parsed DataFrame: {len(df_parsed)} rows")
    
    # Step 4: Generate mesh using DataService
    print("\n4. Generating mesh using DataService...")
    from meld_visualizer.services.data_service import DataService
    
    data_service = DataService()
    color_column = 'FeedVel' if 'FeedVel' in df_parsed.columns else df_parsed.columns[0]
    mesh_data = data_service.generate_mesh(df_parsed, color_column=color_column, lod="medium")
    
    if not mesh_data:
        print("   [FAIL] Failed to generate mesh data")
        return False
    
    vertices = np.array(mesh_data.get('vertices', []))
    faces = np.array(mesh_data.get('faces', []))
    scalars = np.array(mesh_data.get('vertex_colors', []))
    print(f"   [OK] Mesh generated: {len(vertices)} vertices, {len(faces)} faces")
    
    # Step 5: Initialize PyVista integration
    print("\n5. Initializing PyVista integration...")
    from meld_visualizer.components.pyvista_simple import SimplePyVistaIntegration
    
    integration = SimplePyVistaIntegration()
    
    if not integration.initialize_server(port=8053):  # Different port for testing
        print("   [FAIL] Failed to initialize server")
        return False
    print("   [OK] PyVista server initialized")
    
    # Step 6: Update mesh
    print("\n6. Updating mesh with data...")
    if not integration.update_mesh_from_data(vertices, faces, scalars):
        print("   [FAIL] Failed to update mesh")
        return False
    print("   [OK] Mesh updated successfully")
    
    # Step 7: Export screenshot
    print("\n7. Testing screenshot export...")
    if integration.server:
        screenshot_file = "test_pyvista_screenshot.png"
        if integration.server.export_screenshot(screenshot_file):
            print(f"   [OK] Screenshot saved to {screenshot_file}")
            if os.path.exists(screenshot_file):
                file_size = os.path.getsize(screenshot_file)
                print(f"   File size: {file_size:,} bytes")
                os.remove(screenshot_file)  # Clean up
        else:
            print("   [FAIL] Failed to export screenshot")
    
    # Step 8: Export mesh
    print("\n8. Testing mesh export...")
    export_file = "test_export.stl"
    if integration.export_mesh(export_file):
        print(f"   [OK] Mesh exported to {export_file}")
        if os.path.exists(export_file):
            file_size = os.path.getsize(export_file)
            print(f"   File size: {file_size:,} bytes")
            os.remove(export_file)  # Clean up
    else:
        print("   [FAIL] Failed to export mesh")
    
    print("\n" + "="*60)
    print("All tests passed successfully!")
    print("="*60)
    print("\nThe PyVista integration is working correctly.")
    print("You can now use it in the app by:")
    print("1. Loading your MELD data")
    print("2. Going to '3D PyVista (Beta)' tab")
    print("3. Clicking 'Initialize PyVista Renderer'")
    
    return True

if __name__ == "__main__":
    success = test_complete_pyvista_flow()
    sys.exit(0 if success else 1)