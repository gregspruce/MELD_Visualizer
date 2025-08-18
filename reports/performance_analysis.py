"""
Performance Analysis Tool for MELD Visualizer
Analyzes bottlenecks, memory usage, and optimization opportunities
"""

import time
import tracemalloc
import psutil
import io
import base64
import pandas as pd
import numpy as np
from memory_profiler import profile
import cProfile
import pstats
from functools import wraps

# Import modules to test
from data_processing import (
    parse_contents, 
    parse_gcode_file, 
    generate_volume_mesh,
    get_cross_section_vertices
)

# Performance measurement decorator
def measure_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # CPU usage before
        process = psutil.Process()
        cpu_before = process.cpu_percent(interval=0.1)
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Time measurement
        start_time = time.perf_counter()
        
        # Memory tracking
        tracemalloc.start()
        
        result = func(*args, **kwargs)
        
        # Get memory peak
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Time and CPU after
        end_time = time.perf_counter()
        cpu_after = process.cpu_percent(interval=0.1)
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"\n{'='*60}")
        print(f"Performance Analysis: {func.__name__}")
        print(f"{'='*60}")
        print(f"Execution Time: {end_time - start_time:.4f} seconds")
        print(f"Memory Used: {(mem_after - mem_before):.2f} MB")
        print(f"Peak Memory: {peak / 1024 / 1024:.2f} MB")
        print(f"CPU Usage: {cpu_after:.1f}%")
        
        return result
    return wrapper

class PerformanceAnalyzer:
    def __init__(self):
        self.results = {}
        
    def load_test_data(self, filepath):
        """Load test CSV data"""
        with open(filepath, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            return f"data:text/csv;base64,{content}"
    
    def load_gcode_data(self, filepath):
        """Load test G-code data"""
        with open(filepath, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            return f"data:text/plain;base64,{content}"
    
    @measure_performance
    def test_csv_parsing(self, contents, filename):
        """Test CSV parsing performance"""
        df, error, converted = parse_contents(contents, filename)
        if df is not None:
            print(f"Parsed DataFrame shape: {df.shape}")
            print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        return df
    
    @measure_performance
    def test_gcode_parsing(self, contents, filename):
        """Test G-code parsing performance"""
        df, message, _ = parse_gcode_file(contents, filename)
        if df is not None:
            print(f"Parsed DataFrame shape: {df.shape}")
            print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        return df
    
    @measure_performance
    def test_mesh_generation(self, df):
        """Test mesh generation performance"""
        if df is None:
            return None
            
        df_active = df[(df['FeedVel'] > 0) & (df['PathVel'] > 1e-6)].copy()
        if df_active.empty:
            print("No active data for mesh generation")
            return None
            
        color_col = 'ToolTemp' if 'ToolTemp' in df_active.columns else df_active.select_dtypes(include=np.number).columns[0]
        
        mesh_data = generate_volume_mesh(df_active, color_col)
        
        if mesh_data:
            print(f"Vertices: {mesh_data['vertices'].shape}")
            print(f"Faces: {mesh_data['faces'].shape}")
            print(f"Vertex colors: {mesh_data['vertex_colors'].shape}")
            
            # Calculate memory usage
            mem_usage = (
                mesh_data['vertices'].nbytes + 
                mesh_data['faces'].nbytes + 
                mesh_data['vertex_colors'].nbytes
            ) / 1024 / 1024
            print(f"Mesh memory usage: {mem_usage:.2f} MB")
        
        return mesh_data
    
    def profile_mesh_generation_detailed(self, df):
        """Detailed profiling of mesh generation with cProfile"""
        if df is None:
            return
            
        df_active = df[(df['FeedVel'] > 0) & (df['PathVel'] > 1e-6)].copy()
        if df_active.empty:
            print("No active data for mesh generation")
            return
            
        color_col = 'ToolTemp' if 'ToolTemp' in df_active.columns else df_active.select_dtypes(include=np.number).columns[0]
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        mesh_data = generate_volume_mesh(df_active, color_col)
        
        profiler.disable()
        
        print("\n" + "="*60)
        print("Detailed Profile: Mesh Generation")
        print("="*60)
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        return mesh_data
    
    def analyze_dataframe_operations(self, df):
        """Analyze DataFrame operation performance"""
        if df is None:
            return
            
        print("\n" + "="*60)
        print("DataFrame Operation Analysis")
        print("="*60)
        
        # Test filtering performance
        start = time.perf_counter()
        filtered = df[(df['ZPos'] >= df['ZPos'].min()) & (df['ZPos'] <= df['ZPos'].max())]
        filter_time = time.perf_counter() - start
        print(f"Filter operation time: {filter_time*1000:.2f} ms")
        
        # Test copy performance
        start = time.perf_counter()
        df_copy = df.copy()
        copy_time = time.perf_counter() - start
        print(f"Copy operation time: {copy_time*1000:.2f} ms")
        
        # Test calculation performance
        start = time.perf_counter()
        if 'FeedVel' in df.columns and 'PathVel' in df.columns:
            df['TestCalc'] = df['FeedVel'] * 25.4 / df['PathVel'].clip(lower=1e-6)
        calc_time = time.perf_counter() - start
        print(f"Calculation operation time: {calc_time*1000:.2f} ms")
        
        # Test JSON serialization (used for dcc.Store)
        start = time.perf_counter()
        json_str = df.to_json(date_format='iso', orient='split')
        json_time = time.perf_counter() - start
        print(f"JSON serialization time: {json_time*1000:.2f} ms")
        print(f"JSON size: {len(json_str) / 1024 / 1024:.2f} MB")
        
        # Test JSON deserialization
        start = time.perf_counter()
        df_restored = pd.read_json(io.StringIO(json_str), orient='split')
        dejson_time = time.perf_counter() - start
        print(f"JSON deserialization time: {dejson_time*1000:.2f} ms")
    
    def generate_optimization_report(self):
        """Generate comprehensive optimization recommendations"""
        print("\n" + "="*60)
        print("PERFORMANCE OPTIMIZATION RECOMMENDATIONS")
        print("="*60)
        
        recommendations = [
            {
                "area": "Data Processing",
                "bottleneck": "DataFrame operations and JSON serialization",
                "impact": "HIGH",
                "recommendations": [
                    "1. Use dtype optimization: specify dtypes when reading CSV to reduce memory",
                    "2. Consider using Parquet format for data storage instead of JSON",
                    "3. Implement chunked processing for large files",
                    "4. Use numba or cython for compute-intensive loops in mesh generation"
                ]
            },
            {
                "area": "Mesh Generation",
                "bottleneck": "Nested loops and numpy operations",
                "impact": "HIGH",
                "recommendations": [
                    "1. Vectorize get_cross_section_vertices calculations",
                    "2. Pre-allocate arrays instead of using extend()",
                    "3. Use numpy broadcasting to eliminate loops where possible",
                    "4. Consider LOD (Level of Detail) for mesh - reduce POINTS_PER_SECTION for preview"
                ]
            },
            {
                "area": "3D Visualization",
                "bottleneck": "Large mesh rendering in Plotly",
                "impact": "MEDIUM",
                "recommendations": [
                    "1. Implement mesh decimation for large datasets",
                    "2. Add progressive loading - render low-res first, then high-res",
                    "3. Consider WebGL-based rendering with deck.gl for large datasets",
                    "4. Implement viewport culling to render only visible portions"
                ]
            },
            {
                "area": "Callback Performance",
                "bottleneck": "Multiple DataFrame JSON serialization/deserialization",
                "impact": "HIGH",
                "recommendations": [
                    "1. Cache parsed DataFrames in server-side session store",
                    "2. Use Redis or similar for DataFrame caching between callbacks",
                    "3. Implement incremental updates instead of full re-renders",
                    "4. Use Dash's prevent_initial_call more effectively"
                ]
            },
            {
                "area": "Memory Management",
                "bottleneck": "Multiple DataFrame copies in memory",
                "impact": "MEDIUM",
                "recommendations": [
                    "1. Use views instead of copies where possible (df.loc instead of df.copy)",
                    "2. Implement garbage collection hints after large operations",
                    "3. Stream large CSV files instead of loading entirely into memory",
                    "4. Use memory mapping for very large files"
                ]
            },
            {
                "area": "File Upload",
                "bottleneck": "Base64 encoding/decoding overhead",
                "impact": "LOW",
                "recommendations": [
                    "1. Implement chunked upload for large files",
                    "2. Add progress indicator for file processing",
                    "3. Consider server-side file upload endpoint",
                    "4. Compress data before base64 encoding"
                ]
            }
        ]
        
        for rec in recommendations:
            print(f"\n{rec['area']} (Impact: {rec['impact']})")
            print(f"Bottleneck: {rec['bottleneck']}")
            print("Recommendations:")
            for r in rec['recommendations']:
                print(f"  {r}")
        
        return recommendations

def main():
    """Run comprehensive performance analysis"""
    analyzer = PerformanceAnalyzer()
    
    print("MELD Visualizer Performance Analysis")
    print("="*60)
    
    # Test with sample CSV file
    csv_file = "CSV/20250722163434.csv"
    print(f"\n1. Testing CSV Parsing with {csv_file}")
    contents = analyzer.load_test_data(csv_file)
    df = analyzer.test_csv_parsing(contents, csv_file)
    
    # Analyze DataFrame operations
    print("\n2. Analyzing DataFrame Operations")
    analyzer.analyze_dataframe_operations(df)
    
    # Test mesh generation
    print("\n3. Testing Mesh Generation")
    mesh = analyzer.test_mesh_generation(df)
    
    # Detailed profiling of mesh generation
    print("\n4. Detailed Profiling of Mesh Generation")
    analyzer.profile_mesh_generation_detailed(df)
    
    # Test with G-code if available
    try:
        gcode_file = "NC/ZigZag Compensation.Toolpath.nc"
        print(f"\n5. Testing G-code Parsing with {gcode_file}")
        gcode_contents = analyzer.load_gcode_data(gcode_file)
        gcode_df = analyzer.test_gcode_parsing(gcode_contents, gcode_file)
    except FileNotFoundError:
        print("\n5. G-code file not found, skipping G-code parsing test")
    
    # Generate optimization report
    print("\n6. Generating Optimization Report")
    analyzer.generate_optimization_report()

if __name__ == "__main__":
    main()