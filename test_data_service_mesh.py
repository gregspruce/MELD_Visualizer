#!/usr/bin/env python
"""
Test DataService mesh generation to verify parameters.
"""

import sys
import os
import numpy as np
import pandas as pd

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_service_mesh():
    """Test the DataService mesh generation."""
    print("Testing DataService mesh generation...")
    
    from meld_visualizer.services.data_service import DataService
    
    # Create test data similar to MELD data
    num_points = 50
    df = pd.DataFrame({
        'XPos': np.random.rand(num_points) * 100,
        'YPos': np.random.rand(num_points) * 100,
        'ZPos': np.random.rand(num_points) * 10,
        'FeedVel': 5 + np.random.rand(num_points) * 5,
        'PathVel': 10 * np.ones(num_points),
        'Time': np.arange(num_points)
    })
    
    print(f"Created test DataFrame with {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    
    # Create data service
    data_service = DataService()
    
    # Test mesh generation with correct parameters
    try:
        mesh_data = data_service.generate_mesh(
            df, 
            color_column='FeedVel',
            lod='medium'
        )
        
        if mesh_data:
            vertices = mesh_data.get('vertices', [])
            faces = mesh_data.get('faces', [])
            colors = mesh_data.get('vertex_colors', [])
            
            print(f"[OK] Mesh generated successfully:")
            print(f"  - Vertices: {len(vertices)}")
            print(f"  - Faces: {len(faces)}")
            print(f"  - Colors: {len(colors)}")
            return True
        else:
            print("[FAIL] Failed to generate mesh data")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_service_mesh()
    sys.exit(0 if success else 1)