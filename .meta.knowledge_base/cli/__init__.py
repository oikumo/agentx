#!/usr/bin/env python3
"""
CLI interface for Knowledge Base.
"""

import argparse
import json
from core import (
    init_db, hybrid_search, add_entry, correct_entry, 
    run_evolution, get_stats
)


def search_command(query: str, top_k: int = 5, category: str = None):
    """Search entries."""
    conn = init_db()
    results = hybrid_search(conn, query, category, top_k)
    conn.close()
    
    if not results:
        print("No results found.")
        return
    
    print(f"\n📚 Found {len(results)} results for '{query}':\n")
    for i, entry in enumerate(results, 1):
        print(f"{i}. [{entry['id']}] {entry['title']}")
        print(f"   Type: {entry['type']} | Category: {entry['category']}")
        print(f"   Confidence: {entry['confidence']:.2f}")
        if entry.get('finding'):
            finding_text = entry['finding'][:100] + "..." if len(entry['finding']) > 100 else entry['finding']
            print(f"   Finding: {finding_text}")
        if entry.get('solution'):
            solution_text = entry['solution'][:100] + "..." if len(entry['solution']) > 100 else entry['solution']
            print(f"   Solution: {solution_text}")
        print()


def add_command(args):
    """Add entry CLI."""
    result = add_entry(
        args.type, args.category, args.title,
        args.finding, args.solution, args.context,
        args.example, args.confidence
    )
    if result['success']:
        print(f"✓ Added {args.type.upper()} entry: {result['entry_id']}")
        print(f"  Title: {args.title}")
        print(f"  Category: {args.category}")
        print(f"  Confidence: {args.confidence:.2f}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")


def correct_command(entry_id: str, reason: str, new_finding: str):
    """Correct entry CLI."""
    result = correct_entry(entry_id, reason, new_finding)
    if result['success']:
        print(f"✓ Added correction to {entry_id}")
        print(f"  Reason: {reason}")
        print(f"  New finding: {new_finding}")
        print(f"  Confidence adjusted: {result['old_confidence']:.2f} → {result['new_confidence']:.2f}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")


def stats_command():
    """Show statistics."""
    result = get_stats()
    if result['success']:
        print("\n📊 Knowledge Base Statistics\n")
        print("Entries by Type (active only):")
        for type_name, data in result['by_type'].items():
            print(f"  {type_name.capitalize():12} {data['count']:3} entries (avg confidence: {data['avg_confidence']:.2f})")
        
        print("\nEntries by Category:")
        for cat, count in result['by_category'].items():
            print(f"  {cat.capitalize():12} {count:3} entries")
        
        dist = result['confidence_distribution']
        print(f"\nConfidence Distribution:")
        print(f"  High (≥0.9):    {dist['high']}")
        print(f"  Medium (0.6-0.9): {dist['medium']}")
        print(f"  Low (<0.6):     {dist['low']}")
        
        print(f"\nPending corrections: {result['pending_corrections']}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")


def evolve_command():
    """Run evolution."""
    result = run_evolution()
    if result['success']:
        print("🔄 Evolution complete:")
        print(f"  - Entries decayed: {result['decayed']}")
        print(f"  - Entries archived: {result['archived']}")
        print(f"  - Pending corrections: {result['pending_corrections']}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(description='Knowledge Base CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new entry')
    add_parser.add_argument('--type', required=True, choices=['pattern', 'finding', 'correction', 'decision'])
    add_parser.add_argument('--category', required=True, choices=['workflow', 'code', 'test', 'docs', 'tool', 'architecture'])
    add_parser.add_argument('--title', required=True)
    add_parser.add_argument('--finding', required=True)
    add_parser.add_argument('--solution', required=True)
    add_parser.add_argument('--context', default='')
    add_parser.add_argument('--example', default='')
    add_parser.add_argument('--confidence', type=float, default=0.5)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search entries')
    search_parser.add_argument('query')
    search_parser.add_argument('--top-k', type=int, default=5)
    search_parser.add_argument('--category')
    
    # Correct command
    correct_parser = subparsers.add_parser('correct', help='Add correction')
    correct_parser.add_argument('--entry', required=True)
    correct_parser.add_argument('--reason', required=True)
    correct_parser.add_argument('--new-finding', required=True)
    
    # Other commands
    subparsers.add_parser('evolve', help='Run evolution cycle')
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_command(args)
    elif args.command == 'search':
        search_command(args.query, args.top_k, args.category)
    elif args.command == 'correct':
        correct_command(args.entry, args.reason, args.new_finding)
    elif args.command == 'evolve':
        evolve_command()
    elif args.command == 'stats':
        stats_command()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
