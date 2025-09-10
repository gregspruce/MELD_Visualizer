#!/usr/bin/env python3
"""Analyze test coverage to identify high-impact modules for testing improvement."""

import json
import os

def analyze_coverage():
    # Load coverage data
    with open('tests/reports/coverage.json', 'r') as f:
        coverage_data = json.load(f)

    # Extract file coverage info
    file_coverage = []
    for file_path, data in coverage_data['files'].items():
        if 'src' in file_path and 'meld_visualizer' in file_path:
            # Clean up the path for display
            clean_path = file_path
            # Handle both forward and backslashes
            clean_path = clean_path.replace('src\\meld_visualizer\\', '')
            clean_path = clean_path.replace('src/meld_visualizer/', '') 
            clean_path = clean_path.replace('\\\\', '/')
            clean_path = clean_path.replace('\\', '/')
            
            covered = data['summary']['covered_lines']
            total = data['summary']['num_statements'] 
            percent = (covered / total * 100) if total > 0 else 0
            
            file_coverage.append({
                'file': clean_path,
                'covered': covered,
                'total': total,
                'percent': round(percent, 2),
                'missing': total - covered
            })

    # Sort by missing lines (highest impact potential)
    file_coverage.sort(key=lambda x: x['missing'], reverse=True)

    print('Top modules by potential impact (most missing lines):')
    print('-' * 80)
    for i, module in enumerate(file_coverage[:10], 1):
        print(f'{i:2d}. {module["file"]:50s} {module["percent"]:6.1f}% ({module["missing"]:3d} missing)')
    
    print('\n' + '-' * 80)
    print('Current overall coverage: {:.2f}%'.format(coverage_data['totals']['percent_covered']))
    
    # Also show modules with 0% coverage (completely untested)
    untested = [m for m in file_coverage if m['percent'] == 0]
    if untested:
        print(f'\nModules with 0% coverage ({len(untested)} total):')
        for module in untested:
            print(f'  - {module["file"]:50s} ({module["total"]:3d} statements)')

if __name__ == '__main__':
    analyze_coverage()