#!/usr/bin/env python3
"""
Knowledge Base Test Runner
===========================
Main entry point for running all KB tests.

Usage:
    python run_tests.py [--verbose] [--json]
    
Options:
    --verbose   Show detailed output
    --json      Output results in JSON format
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Test modules
TEST_MODULES = [
    'test_kb_functionality',
    'test_kb_performance',
    'test_kb_edge_cases',
    'test_kb_integration',
    'test_kb_populate',
    'test_opencode_integration',
    'test_opencode_commands'
]


def run_test_module(module_name: str, verbose: bool = False) -> Dict[str, Any]:
    """Run a single test module."""
    try:
        # Import the module
        module = __import__(module_name)
        
        # Run its main function
        if hasattr(module, 'run_all_tests'):
            start_time = datetime.now()
            success = module.run_all_tests()
            end_time = datetime.now()
            
            return {
                'name': module_name,
                'success': success,
                'duration': (end_time - start_time).total_seconds(),
                'error': None
            }
        else:
            return {
                'name': module_name,
                'success': False,
                'error': 'No run_all_tests function'
            }
    except Exception as e:
        if verbose:
            print(f"  Error running {module_name}: {e}")
        return {
            'name': module_name,
            'success': False,
            'error': str(e)
        }


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='Run KB tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()
    
    # Change to test directory
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    print("\n" + "="*70)
    print("Knowledge Base Comprehensive Test Suite")
    print("="*70 + "\n")
    
    # Run each test module
    for module_name in TEST_MODULES:
        if args.verbose:
            print(f"Running {module_name}...")
        
        result = run_test_module(module_name, args.verbose)
        results['tests'].append(result)
        results['total'] += 1
        
        if result['success']:
            results['passed'] += 1
            status = "✓ PASS"
        else:
            results['failed'] += 1
            status = "✗ FAIL"
        
        print(f"  {status} - {module_name}")
        if result.get('error') and args.verbose:
            print(f"    Error: {result['error']}")
        if result.get('duration'):
            print(f"    Duration: {result['duration']:.2f}s")
    
    # Summary
    success_rate = 0
    if results['total'] > 0:
        success_rate = int(results['passed'] * 100 / results['total'])
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"Total:  {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {success_rate}%")
    
    # Save results
    results_file = script_dir / 'test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    if args.json:
        print("\n" + "="*70)
        print("JSON Results:")
        print("="*70)
        print(json.dumps(results, indent=2))
    
    # Exit code
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
