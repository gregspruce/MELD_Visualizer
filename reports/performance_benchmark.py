"""
Performance Benchmark: Original vs Optimized Implementation
Compares execution time and memory usage between implementations
"""

import time
import tracemalloc
import pandas as pd
import numpy as np
import base64
import io
import tabulate

# Import original functions
from data_processing import (
    parse_contents as parse_contents_original,
    generate_volume_mesh as generate_volume_mesh_original
)

# Import optimized functions
from data_processing_optimized import (
    parse_contents_optimized,
    generate_volume_mesh_optimized,
    generate_volume_mesh_lod,
    optimize_dataframe_for_json,
    df_cache
)

class PerformanceBenchmark:
    def __init__(self):
        self.results = []
        
    def load_test_data(self, filepath):
        """Load test CSV data"""
        with open(filepath, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            return f"data:text/csv;base64,{content}"
    
    def benchmark_function(self, func, *args, **kwargs):
        """Benchmark a single function execution"""
        # Memory tracking
        tracemalloc.start()
        
        # Time measurement
        start_time = time.perf_counter()
        
        result = func(*args, **kwargs)
        
        # Get memory peak
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        end_time = time.perf_counter()
        
        return {
            'time': end_time - start_time,
            'memory_peak': peak / 1024 / 1024,  # MB
            'result': result
        }
    
    def compare_csv_parsing(self, test_file):
        """Compare CSV parsing performance"""
        contents = self.load_test_data(test_file)
        
        print(f"\nBenchmarking CSV Parsing: {test_file}")
        print("-" * 60)
        
        # Original implementation
        original = self.benchmark_function(parse_contents_original, contents, test_file)
        df_original = original['result'][0]
        
        # Optimized implementation
        optimized = self.benchmark_function(parse_contents_optimized, contents, test_file)
        df_optimized = optimized['result'][0]
        
        # Calculate improvements
        time_improvement = (original['time'] - optimized['time']) / original['time'] * 100
        memory_improvement = (original['memory_peak'] - optimized['memory_peak']) / original['memory_peak'] * 100
        
        # Original DataFrame memory usage
        orig_mem = df_original.memory_usage(deep=True).sum() / 1024 / 1024 if df_original is not None else 0
        opt_mem = df_optimized.memory_usage(deep=True).sum() / 1024 / 1024 if df_optimized is not None else 0
        
        results = [
            ['Metric', 'Original', 'Optimized', 'Improvement'],
            ['Execution Time (s)', f"{original['time']:.4f}", f"{optimized['time']:.4f}", f"{time_improvement:.1f}%"],
            ['Peak Memory (MB)', f"{original['memory_peak']:.2f}", f"{optimized['memory_peak']:.2f}", f"{memory_improvement:.1f}%"],
            ['DataFrame Size (MB)', f"{orig_mem:.2f}", f"{opt_mem:.2f}", f"{(orig_mem - opt_mem) / orig_mem * 100:.1f}%"]
        ]
        
        print(tabulate.tabulate(results, headers='firstrow', tablefmt='grid'))
        
        return df_original, df_optimized
    
    def compare_mesh_generation(self, df):
        """Compare mesh generation performance"""
        if df is None:
            return
            
        df_active = df[(df['FeedVel'] > 0) & (df['PathVel'] > 1e-6)].copy()
        if df_active.empty:
            print("No active data for mesh generation")
            return
            
        color_col = 'ToolTemp' if 'ToolTemp' in df_active.columns else df_active.select_dtypes(include=np.number).columns[0]
        
        print(f"\nBenchmarking Mesh Generation")
        print(f"Active data points: {len(df_active)}")
        print("-" * 60)
        
        # Original implementation
        original = self.benchmark_function(generate_volume_mesh_original, df_active, color_col)
        mesh_original = original['result']
        
        # Optimized implementation
        optimized = self.benchmark_function(generate_volume_mesh_optimized, df_active, color_col)
        mesh_optimized = optimized['result']
        
        # LOD versions
        lod_low = self.benchmark_function(generate_volume_mesh_lod, df_active, color_col, 'low')
        lod_medium = self.benchmark_function(generate_volume_mesh_lod, df_active, color_col, 'medium')
        lod_high = self.benchmark_function(generate_volume_mesh_lod, df_active, color_col, 'high')
        
        results = [
            ['Implementation', 'Time (s)', 'Memory (MB)', 'Vertices', 'Faces'],
            ['Original', f"{original['time']:.4f}", f"{original['memory_peak']:.2f}", 
             mesh_original['vertices'].shape[0] if mesh_original else 0,
             mesh_original['faces'].shape[0] if mesh_original else 0],
            ['Optimized', f"{optimized['time']:.4f}", f"{optimized['memory_peak']:.2f}",
             mesh_optimized['vertices'].shape[0] if mesh_optimized else 0,
             mesh_optimized['faces'].shape[0] if mesh_optimized else 0],
            ['LOD Low', f"{lod_low['time']:.4f}", f"{lod_low['memory_peak']:.2f}",
             lod_low['result']['vertices'].shape[0] if lod_low['result'] else 0,
             lod_low['result']['faces'].shape[0] if lod_low['result'] else 0],
            ['LOD Medium', f"{lod_medium['time']:.4f}", f"{lod_medium['memory_peak']:.2f}",
             lod_medium['result']['vertices'].shape[0] if lod_medium['result'] else 0,
             lod_medium['result']['faces'].shape[0] if lod_medium['result'] else 0],
            ['LOD High', f"{lod_high['time']:.4f}", f"{lod_high['memory_peak']:.2f}",
             lod_high['result']['vertices'].shape[0] if lod_high['result'] else 0,
             lod_high['result']['faces'].shape[0] if lod_high['result'] else 0]
        ]
        
        print(tabulate.tabulate(results, headers='firstrow', tablefmt='grid'))
        
        # Calculate speedup
        speedup = original['time'] / optimized['time']
        print(f"\nSpeedup: {speedup:.2f}x faster")
        
    def compare_json_serialization(self, df):
        """Compare JSON serialization performance"""
        if df is None:
            return
            
        print(f"\nBenchmarking JSON Serialization")
        print(f"DataFrame shape: {df.shape}")
        print("-" * 60)
        
        # Original DataFrame
        start = time.perf_counter()
        json_original = df.to_json(date_format='iso', orient='split')
        time_original = time.perf_counter() - start
        size_original = len(json_original) / 1024 / 1024
        
        # Optimized DataFrame
        df_opt = optimize_dataframe_for_json(df)
        start = time.perf_counter()
        json_optimized = df_opt.to_json(date_format='iso', orient='split')
        time_optimized = time.perf_counter() - start
        size_optimized = len(json_optimized) / 1024 / 1024
        
        # Test caching
        cache_key = 'test_df'
        
        # First access (cache miss)
        start = time.perf_counter()
        df_cache.set(cache_key, df)
        cached_df = df_cache.get(cache_key)
        time_cache_miss = time.perf_counter() - start
        
        # Second access (cache hit)
        start = time.perf_counter()
        cached_df = df_cache.get(cache_key)
        time_cache_hit = time.perf_counter() - start
        
        results = [
            ['Operation', 'Time (ms)', 'Size (MB)'],
            ['Original JSON', f"{time_original*1000:.2f}", f"{size_original:.2f}"],
            ['Optimized JSON', f"{time_optimized*1000:.2f}", f"{size_optimized:.2f}"],
            ['Cache Miss', f"{time_cache_miss*1000:.2f}", '-'],
            ['Cache Hit', f"{time_cache_hit*1000:.2f}", '-']
        ]
        
        print(tabulate.tabulate(results, headers='firstrow', tablefmt='grid'))
        
        print(f"\nJSON size reduction: {(size_original - size_optimized) / size_original * 100:.1f}%")
        print(f"Cache speedup: {time_cache_miss / time_cache_hit:.0f}x faster")
    
    def run_stress_test(self):
        """Run stress test with large synthetic dataset"""
        print(f"\nStress Test: Large Dataset Performance")
        print("-" * 60)
        
        # Generate large synthetic dataset
        n_points = 10000
        print(f"Generating synthetic dataset with {n_points} points...")
        
        # Create spiral pattern
        t = np.linspace(0, 20*np.pi, n_points)
        x = t * np.cos(t)
        y = t * np.sin(t)
        z = t / 10
        
        df_large = pd.DataFrame({
            'Date': '2025-01-01',
            'Time': pd.date_range('2025-01-01', periods=n_points, freq='100ms').strftime('%H:%M:%S.%f'),
            'XPos': x.astype(np.float32),
            'YPos': y.astype(np.float32),
            'ZPos': z.astype(np.float32),
            'FeedVel': np.random.uniform(100, 500, n_points).astype(np.float32),
            'PathVel': np.random.uniform(500, 1000, n_points).astype(np.float32),
            'ToolTemp': np.random.uniform(20, 200, n_points).astype(np.float32),
            'SpinVel': np.zeros(n_points, dtype=np.float32),
            'SpinTrq': np.zeros(n_points, dtype=np.float32),
            'FRO': np.ones(n_points, dtype=np.float32) * 100
        })
        
        df_large['Time'] = pd.to_datetime(df_large['Date'] + ' ' + df_large['Time'])
        df_large['TimeInSeconds'] = (df_large['Time'] - df_large['Time'].min()).dt.total_seconds()
        
        print(f"Dataset created: {df_large.shape}")
        print(f"Memory usage: {df_large.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Test mesh generation with large dataset
        df_active = df_large[(df_large['FeedVel'] > 0)].copy()
        color_col = 'ToolTemp'
        
        print("\nMesh generation performance:")
        
        # Test different implementations
        for impl_name, impl_func, impl_args in [
            ('Original', generate_volume_mesh_original, (df_active, color_col)),
            ('Optimized', generate_volume_mesh_optimized, (df_active, color_col)),
            ('LOD Low', generate_volume_mesh_lod, (df_active, color_col, 'low'))
        ]:
            start = time.perf_counter()
            try:
                mesh = impl_func(*impl_args)
                elapsed = time.perf_counter() - start
                if mesh:
                    print(f"{impl_name:12} - Time: {elapsed:.2f}s, Vertices: {mesh['vertices'].shape[0]:,}")
                else:
                    print(f"{impl_name:12} - Failed to generate mesh")
            except Exception as e:
                print(f"{impl_name:12} - Error: {str(e)}")

def main():
    """Run comprehensive performance benchmarks"""
    benchmark = PerformanceBenchmark()
    
    print("=" * 60)
    print("MELD Visualizer Performance Benchmark")
    print("Comparing Original vs Optimized Implementations")
    print("=" * 60)
    
    # Test with sample files
    test_files = [
        "CSV/20250722163434.csv",  # Largest file
        "CSV/20250708104310.csv"   # Smallest file
    ]
    
    for test_file in test_files:
        try:
            # Compare CSV parsing
            df_original, df_optimized = benchmark.compare_csv_parsing(test_file)
            
            # Compare mesh generation
            benchmark.compare_mesh_generation(df_original)
            
            # Compare JSON serialization
            benchmark.compare_json_serialization(df_original)
            
        except FileNotFoundError:
            print(f"Test file {test_file} not found, skipping...")
    
    # Run stress test
    benchmark.run_stress_test()
    
    print("\n" + "=" * 60)
    print("Benchmark Complete")
    print("=" * 60)

if __name__ == "__main__":
    # tabulate module already imported at top
    
    main()