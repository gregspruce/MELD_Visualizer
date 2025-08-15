"""
Performance benchmark tests for MELD Visualizer.
Measures and compares performance of critical operations.
"""

import pytest
import pandas as pd
import numpy as np
import time
import base64
import statistics
from typing import List, Callable
from contextlib import contextmanager

from data_processing import parse_contents, generate_volume_mesh
from services import get_data_service, get_cache
from logging_config import performance_logger


@contextmanager
def timer():
    """Context manager for timing operations."""
    start = time.perf_counter()
    yield lambda: (time.perf_counter() - start) * 1000  # Return ms


def benchmark(func: Callable, iterations: int = 10, warmup: int = 2) -> dict:
    """
    Benchmark a function over multiple iterations.
    
    Args:
        func: Function to benchmark
        iterations: Number of test iterations
        warmup: Number of warmup iterations
        
    Returns:
        Dictionary with timing statistics
    """
    # Warmup runs
    for _ in range(warmup):
        func()
    
    # Benchmark runs
    times = []
    for _ in range(iterations):
        with timer() as t:
            func()
        times.append(t())
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
        'iterations': iterations
    }


class TestDataProcessingPerformance:
    """Benchmark data processing operations."""
    
    @pytest.fixture
    def small_csv(self):
        """Create small CSV data (100 rows)."""
        df = pd.DataFrame({
            'XPos': np.random.randn(100),
            'YPos': np.random.randn(100),
            'ZPos': np.random.randn(100),
            'FeedVel': np.random.rand(100) * 200,
            'PathVel': np.random.rand(100) * 100,
            'ToolTemp': np.random.rand(100) * 300,
            'Time': pd.date_range('2024-01-01', periods=100, freq='S')
        })
        csv_string = df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        return f"data:text/csv;base64,{encoded}"
    
    @pytest.fixture
    def medium_csv(self):
        """Create medium CSV data (1000 rows)."""
        df = pd.DataFrame({
            'XPos': np.random.randn(1000),
            'YPos': np.random.randn(1000),
            'ZPos': np.random.randn(1000),
            'FeedVel': np.random.rand(1000) * 200,
            'PathVel': np.random.rand(1000) * 100,
            'ToolTemp': np.random.rand(1000) * 300,
            'Time': pd.date_range('2024-01-01', periods=1000, freq='S')
        })
        csv_string = df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        return f"data:text/csv;base64,{encoded}"
    
    @pytest.fixture
    def large_csv(self):
        """Create large CSV data (10000 rows)."""
        df = pd.DataFrame({
            'XPos': np.random.randn(10000),
            'YPos': np.random.randn(10000),
            'ZPos': np.random.randn(10000),
            'FeedVel': np.random.rand(10000) * 200,
            'PathVel': np.random.rand(10000) * 100,
            'ToolTemp': np.random.rand(10000) * 300,
            'Time': pd.date_range('2024-01-01', periods=10000, freq='S')
        })
        csv_string = df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        return f"data:text/csv;base64,{encoded}"
    
    def test_csv_parsing_performance(self, small_csv, medium_csv, large_csv):
        """Benchmark CSV parsing performance."""
        results = {}
        
        # Small file
        def parse_small():
            parse_contents(small_csv, "small.csv")
        
        results['small'] = benchmark(parse_small, iterations=20)
        
        # Medium file
        def parse_medium():
            parse_contents(medium_csv, "medium.csv")
        
        results['medium'] = benchmark(parse_medium, iterations=10)
        
        # Large file
        def parse_large():
            parse_contents(large_csv, "large.csv")
        
        results['large'] = benchmark(parse_large, iterations=5)
        
        # Log results
        for size, stats in results.items():
            performance_logger.log_operation(
                f"CSV parsing ({size})",
                stats['mean'],
                {'median': stats['median'], 'stdev': stats['stdev']}
            )
        
        # Performance assertions (adjust based on hardware)
        assert results['small']['mean'] < 50  # Should parse in < 50ms
        assert results['medium']['mean'] < 200  # Should parse in < 200ms
        assert results['large']['mean'] < 2000  # Should parse in < 2s
    
    def test_mesh_generation_performance(self):
        """Benchmark mesh generation performance."""
        # Create test data
        df_small = pd.DataFrame({
            'XPos': np.linspace(0, 100, 100),
            'YPos': np.linspace(0, 100, 100),
            'ZPos': np.repeat(np.arange(10), 10),
            'ToolTemp': np.random.rand(100) * 300,
            'FeedVel': np.ones(100) * 50,
            'PathVel': np.ones(100) * 25
        })
        
        df_large = pd.DataFrame({
            'XPos': np.linspace(0, 100, 1000),
            'YPos': np.linspace(0, 100, 1000),
            'ZPos': np.repeat(np.arange(100), 10),
            'ToolTemp': np.random.rand(1000) * 300,
            'FeedVel': np.ones(1000) * 50,
            'PathVel': np.ones(1000) * 25
        })
        
        # Benchmark small mesh
        def gen_small():
            generate_volume_mesh(df_small, 'ToolTemp')
        
        small_stats = benchmark(gen_small, iterations=10)
        
        # Benchmark large mesh
        def gen_large():
            generate_volume_mesh(df_large, 'ToolTemp')
        
        large_stats = benchmark(gen_large, iterations=5)
        
        # Log results
        performance_logger.log_operation(
            "Mesh generation (100 points)", small_stats['mean']
        )
        performance_logger.log_operation(
            "Mesh generation (1000 points)", large_stats['mean']
        )
        
        # Performance assertions
        assert small_stats['mean'] < 500  # < 500ms for small mesh
        assert large_stats['mean'] < 5000  # < 5s for large mesh


class TestCachePerformance:
    """Benchmark caching performance."""
    
    def test_cache_hit_vs_miss(self):
        """Compare cache hit vs miss performance."""
        cache = get_cache()
        cache.clear()
        
        # Create test data
        df = pd.DataFrame({
            'A': np.random.randn(1000),
            'B': np.random.randn(1000)
        })
        
        # Benchmark cache miss (first access)
        miss_times = []
        for i in range(10):
            cache.clear()
            with timer() as t:
                cache.cache_dataframe(df, f"test_{i}")
                cache.get_dataframe(f"test_{i}")
            miss_times.append(t())
        
        # Benchmark cache hit (subsequent access)
        cache.cache_dataframe(df, "test_hit")
        hit_times = []
        for _ in range(100):
            with timer() as t:
                cache.get_dataframe("test_hit")
            hit_times.append(t())
        
        miss_avg = statistics.mean(miss_times)
        hit_avg = statistics.mean(hit_times)
        
        # Log results
        performance_logger.log_operation("Cache miss", miss_avg)
        performance_logger.log_operation("Cache hit", hit_avg)
        performance_logger.log_cache_hit("DataFrame cache", hit_avg / miss_avg)
        
        # Cache hits should be much faster
        assert hit_avg < miss_avg / 5  # At least 5x faster
    
    def test_cache_eviction_performance(self):
        """Test cache eviction performance."""
        cache = get_cache()
        cache.clear()
        
        # Fill cache with data
        with timer() as t:
            for i in range(1000):
                cache.set(f"key_{i}", f"value_{i}" * 100)
        
        fill_time = t()
        
        # Access with eviction
        with timer() as t:
            for i in range(1000, 2000):
                cache.set(f"key_{i}", f"value_{i}" * 100)
        
        evict_time = t()
        
        # Log results
        performance_logger.log_operation("Cache fill (1000 entries)", fill_time)
        performance_logger.log_operation("Cache with eviction", evict_time)
        
        # Eviction shouldn't add significant overhead
        assert evict_time < fill_time * 2


class TestServiceLayerPerformance:
    """Benchmark service layer performance."""
    
    def test_data_service_caching(self):
        """Test data service with caching enabled."""
        data_service = get_data_service()
        data_service.clear_cache()
        
        # Create test data
        df = pd.DataFrame({
            'XPos': np.random.randn(1000),
            'YPos': np.random.randn(1000),
            'ZPos': np.random.randn(1000),
            'FeedVel': np.random.rand(1000) * 100,
            'PathVel': np.random.rand(1000) * 50
        })
        
        # First call - no cache
        with timer() as t1:
            stats1 = data_service.get_column_statistics(df)
        first_time = t1()
        
        # Second call - cached
        with timer() as t2:
            stats2 = data_service.get_column_statistics(df)
        cached_time = t2()
        
        # Verify same results
        assert stats1 == stats2
        
        # Log performance
        performance_logger.log_operation("Statistics (uncached)", first_time)
        performance_logger.log_operation("Statistics (cached)", cached_time)
        
        # Cached should be faster
        assert cached_time < first_time / 2
    
    def test_filter_performance(self):
        """Test filtering performance."""
        data_service = get_data_service()
        
        # Create large dataset
        df = pd.DataFrame({
            'Value': np.random.randn(100000),
            'Category': np.random.choice(['A', 'B', 'C'], 100000)
        })
        
        # Benchmark range filtering
        def filter_range():
            data_service.filter_by_range(df, 'Value', -1, 1)
        
        range_stats = benchmark(filter_range, iterations=20)
        
        # Log results
        performance_logger.log_operation(
            "Range filter (100k rows)", range_stats['mean']
        )
        
        # Should be fast even for large data
        assert range_stats['mean'] < 10  # < 10ms


class TestOptimizedVsStandard:
    """Compare optimized vs standard implementations."""
    
    def test_parsing_optimization(self):
        """Compare optimized vs standard parsing."""
        try:
            from data_processing_optimized import parse_contents_optimized
            optimized_available = True
        except ImportError:
            optimized_available = False
            pytest.skip("Optimized module not available")
        
        from data_processing import parse_contents as parse_standard
        
        # Create test data
        df = pd.DataFrame({
            'XPos': np.random.randn(5000),
            'YPos': np.random.randn(5000),
            'ZPos': np.random.randn(5000),
            'FeedVel': np.random.rand(5000) * 200,
            'PathVel': np.random.rand(5000) * 100,
            'ToolTemp': np.random.rand(5000) * 300,
            'Time': pd.date_range('2024-01-01', periods=5000, freq='S')
        })
        csv_string = df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        # Benchmark standard
        def parse_std():
            parse_standard(contents, "test.csv")
        
        std_stats = benchmark(parse_std, iterations=10)
        
        # Benchmark optimized
        def parse_opt():
            parse_contents_optimized(contents, "test.csv")
        
        opt_stats = benchmark(parse_opt, iterations=10)
        
        # Calculate improvement
        improvement = std_stats['mean'] / opt_stats['mean']
        
        # Log results
        performance_logger.log_operation("Standard parsing", std_stats['mean'])
        performance_logger.log_operation("Optimized parsing", opt_stats['mean'])
        performance_logger.log_operation(
            "Optimization speedup", improvement, {'type': 'ratio'}
        )
        
        # Optimized should be faster
        assert opt_stats['mean'] < std_stats['mean']
        assert improvement > 1.2  # At least 20% faster


class TestMemoryUsage:
    """Test memory usage of operations."""
    
    def test_dataframe_memory(self):
        """Test DataFrame memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Create large DataFrame
        df = pd.DataFrame({
            f'col_{i}': np.random.randn(10000)
            for i in range(50)  # 50 columns
        })
        
        # Memory after creation
        after_create = process.memory_info().rss / (1024 * 1024)
        
        # Cache DataFrame
        cache = get_cache()
        cache.cache_dataframe(df, "large_df")
        
        # Memory after caching
        after_cache = process.memory_info().rss / (1024 * 1024)
        
        # Calculate usage
        df_memory = after_create - baseline
        cache_overhead = after_cache - after_create
        
        # Log memory usage
        performance_logger.log_memory("DataFrame creation", df_memory)
        performance_logger.log_memory("Cache overhead", cache_overhead)
        
        # Cache overhead should be reasonable
        assert cache_overhead < df_memory * 0.5  # Less than 50% overhead


class TestScalability:
    """Test scalability with increasing data sizes."""
    
    def test_linear_scalability(self):
        """Test that performance scales linearly with data size."""
        sizes = [100, 500, 1000, 5000]
        times = []
        
        for size in sizes:
            df = pd.DataFrame({
                'X': np.random.randn(size),
                'Y': np.random.randn(size)
            })
            
            with timer() as t:
                # Simple operation that should scale linearly
                df['Z'] = df['X'] + df['Y']
                _ = df['Z'].mean()
            
            times.append(t())
        
        # Calculate scaling factor
        scaling_factors = []
        for i in range(1, len(sizes)):
            size_ratio = sizes[i] / sizes[0]
            time_ratio = times[i] / times[0]
            scaling_factors.append(time_ratio / size_ratio)
        
        avg_scaling = statistics.mean(scaling_factors)
        
        # Log results
        for size, time_ms in zip(sizes, times):
            performance_logger.log_operation(f"Linear op ({size} rows)", time_ms)
        
        # Should scale approximately linearly (allow some overhead)
        assert 0.8 < avg_scaling < 2.0  # Within 2x of linear


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])