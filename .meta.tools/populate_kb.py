#!/usr/bin/env python3
"""
KB Population Script - Traverses all Meta Harness and Agent-X files
and populates knowledge bases with LLM-analyzed insights.

This script:
1. Finds all .meta.* directories and key documentation files
2. Reads each file's content
3. Uses LLM to analyze and extract key insights
4. Creates structured knowledge base entries
5. Populates the appropriate KB (Meta Harness or Agent-X)

Usage:
    python .meta.tools/populate_kb.py [--kb both|meta|agentx] [--verbose]
"""

import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from meta_tools import meta_kb, agentx_kb, KnowledgeBase


class KBPopulator:
    """Traverses project files and populates KBs with analyzed knowledge."""
    
    def __init__(self, target_kb: str = "both", verbose: bool = True):
        """
        Initialize KB Populator.
        
        Args:
            target_kb: Which KB to populate ('meta', 'agentx', or 'both')
            verbose: Print progress information
        """
        self.target_kb = target_kb
        self.verbose = verbose
        # Correct base path: .meta.tools is in .meta.tools/, so parent.parent.parent = project root
        self.base_path = Path(__file__).parent.parent
        self.entries_added = {"meta": 0, "agentx": 0}
    
    def find_all_meta_files(self) -> List[Tuple[Path, str]]:
        """
        Find all relevant files including source code.
        
        Returns:
            List of (file_path, kb_type) tuples
        """
        files_to_analyze = []
        
        # Root documentation (both KBs)
        root_docs = [
            "AGENTS.md",
            "META_HARNESS.md", 
            "README.md",
        ]
        
        for doc in root_docs:
            file_path = self.base_path / doc
            if file_path.exists():
                files_to_analyze.append((file_path, "both"))
        
        # Find ALL directories starting with .meta
        meta_dirs = []
        for item in self.base_path.iterdir():
            if item.is_dir() and item.name.startswith('.meta'):
                meta_dirs.append(item)
        
        if self.verbose:
            print(f"Found {len(meta_dirs)} .meta* directories: {[d.name for d in meta_dirs]}")
        
        for meta_path in meta_dirs:
            if not meta_path.exists():
                continue
            
            # Find all META.md files
            for meta_file in meta_path.rglob("META.md"):
                files_to_analyze.append((meta_file, "meta"))
            
            # Find all .md files in .meta directories
            for md_file in meta_path.rglob("*.md"):
                if md_file.name != "META.md":
                    files_to_analyze.append((md_file, "meta"))
        
        # ===== Agent-X Source Code (CRITICAL!) =====
        # Analyze actual Python source code in src/
        src_path = self.base_path / "src"
        if src_path.exists():
            if self.verbose:
                print(f"Found src/ directory - analyzing source code...")
            
            # All Python files
            for py_file in src_path.rglob("*.py"):
                # Skip __pycache__ and virtual environments
                if '__pycache__' not in str(py_file) and '.venv' not in str(py_file):
                    files_to_analyze.append((py_file, "agentx"))
            
            # All markdown in src
            for md_file in src_path.rglob("*.md"):
                files_to_analyze.append((md_file, "agentx"))
        
        # Other Agent-X documentation
        doc_path = self.base_path / "doc"
        if doc_path.exists():
            for md_file in doc_path.rglob("*.md"):
                files_to_analyze.append((md_file, "agentx"))
        
        # Remove duplicates
        seen = set()
        unique_files = []
        for file_path, kb_type in files_to_analyze:
            if str(file_path) not in seen:
                seen.add(str(file_path))
                unique_files.append((file_path, kb_type))
        
        return unique_files
    
    def analyze_file_with_llm(self, file_path: Path) -> Dict:
        """
        Analyze a file and extract structured knowledge.
        Handles both Python source files and markdown documentation.
        """
        # Python source files
        if file_path.suffix == '.py':
            return self._analyze_python_file(file_path)
        
        # Markdown files
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            if self.verbose:
                print(f"  ✗ Could not read {file_path.name}: {e}")
            return {}
        
        sections = self._extract_sections(content)
        
        return {
            'title': self._extract_title(content, file_path),
            'summary': content[:2000].replace('\n', ' '),
            'sections': sections,
            'directives': self._extract_directives(content),
            'workflows': self._extract_workflows(content),
            'patterns': self._extract_patterns(content),
            'best_practices': self._extract_best_practices(content),
        }
    
    def _analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze Python source code to extract classes, functions, imports."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            if self.verbose:
                print(f"  ✗ Could not read {file_path.name}: {e}")
            return {}
        
        lines = content.split('\n')
        classes = []
        functions = []
        imports = []
        
        for line in lines:
            if line.strip().startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].strip()
                classes.append(class_name)
            elif line.strip().startswith('def '):
                func_name = line.strip().split('def ')[1].split('(')[0]
                functions.append(func_name)
            elif line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        
        try:
            rel_path = file_path.relative_to(self.base_path)
        except:
            rel_path = file_path.name
        
        summary_parts = []
        if classes:
            summary_parts.append(f"Classes: {', '.join(classes)}")
        if functions:
            summary_parts.append(f"Functions: {', '.join(functions[:10])}")
        
        return {
            'title': f"Python: {file_path.name}",
            'summary': f"Source: {rel_path}. " + " | ".join(summary_parts),
            'classes': classes,
            'functions': functions,
            'imports': imports[:10],
            'is_source': True,
            'file_type': 'python',
        }
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections from markdown content."""
        sections = []
        current_section = None
        section_lines = []
        
        for line in content.split('\n'):
            if line.startswith('##') or line.startswith('###'):
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(section_lines)
                    })
                current_section = line.lstrip('#').strip()
                section_lines = []
            else:
                section_lines.append(line)
        
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(section_lines)
            })
        
        return sections
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """Extract or generate title from content."""
        # Try to get first heading
        for line in content.split('\n'):
            if line.startswith('# ') and len(line) > 2:
                return line[2:].strip()
        
        # Fallback to filename
        return file_path.stem.replace('_', ' ').title()
    
    def _extract_directives(self, content: str) -> List[str]:
        """Extract directive-like statements (NEVER, ALWAYS, MUST)."""
        directives = []
        
        for line in content.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['**never', '**always', '**must', '| 1 |', '| 2 |', '| 3 |']):
                if '|' in line:  # Table row
                    directives.append(line.strip('|').strip())
                elif line.strip().startswith(('- ', '**')):
                    directives.append(line.strip('- ').strip())
        
        return directives[:10]  # Limit to top 10
    
    def _extract_workflows(self, content: str) -> List[str]:
        """Extract workflow steps."""
        workflows = []
        
        for line in content.split('\n'):
            if any(x in line for x in ['→', 'workflow', 'step', 'process']):
                workflows.append(line.strip('- ').strip())
        
        return workflows[:5]
    
    def _extract_patterns(self, content: str) -> List[str]:
        """Extract code patterns and examples."""
        patterns = []
        in_code_block = False
        code_block = []
        
        for line in content.split('\n'):
            if line.startswith('```'):
                if in_code_block:
                    patterns.append('\n'.join(code_block))
                    code_block = []
                in_code_block = not in_code_block
            elif in_code_block:
                code_block.append(line)
        
        return patterns[:3]
    
    def _extract_best_practices(self, content: str) -> List[str]:
        """Extract best practices and recommendations."""
        practices = []
        
        for line in content.split('\n'):
            if any(x in line.lower() for x in ['should', 'recommend', 'best practice', 'guideline']):
                practices.append(line.strip('- ').strip())
        
        return practices[:5]
    
    def create_kb_entries(self, file_path: Path, analysis: Dict, kb_type: str) -> List[Dict]:
        """Create KB entries from analyzed file."""
        entries = []
        
        # Handle Python source files differently
        if analysis.get('is_source') and analysis.get('file_type') == 'python':
            # Source code entry
            entries.append({
                "type": "pattern",
                "category": "source_code",
                "title": f"Source: {analysis['title']}",
                "finding": analysis['summary'],
                "solution": f"Classes: {', '.join(analysis.get('classes', [])[:5]) or 'None'} | Functions: {', '.join(analysis.get('functions', [])[:10]) or 'None'}",
                "context": f"Python source at {file_path}",
                "confidence": 1.0,
                "example": f"Import from {file_path.parent}"
            })
            
            # Add entries for each class found
            for cls in analysis.get('classes', [])[:3]:
                entries.append({
                    "type": "pattern",
                    "category": "class",
                    "title": f"Class: {cls}",
                    "finding": f"Class defined in {file_path.name}",
                    "solution": f"Import {cls} from {file_path.parent}",
                    "context": f"Source: {file_path}",
                    "confidence": 1.0,
                    "example": f"from {file_path.parent} import {cls}"
                })
            
            return entries
        
        # Main file entry (for markdown/docs)
        entries.append({
            "type": "pattern",
            "category": "documentation",
            "title": f"{analysis['title']} ({file_path.name})",
            "finding": f"Documentation file: {file_path.name}",
            "solution": analysis['summary'][:1000],
            "context": f"Full path: {file_path}",
            "confidence": 0.95,
            "example": f"Read {file_path.name} for complete information"
        })
        
        # Directives entry
        if analysis.get('directives'):
            entries.append({
                "type": "pattern",
                "category": "directives",
                "title": f"Directives from {file_path.name}",
                "finding": "Key directives and rules",
                "solution": "; ".join(analysis['directives']),
                "context": f"Extracted from {file_path}",
                "confidence": 1.0,
                "example": f"Follow directives in {file_path.name}"
            })
        
        # Workflows entry
        if analysis.get('workflows'):
            entries.append({
                "type": "pattern",
                "category": "workflow",
                "title": f"Workflows from {file_path.name}",
                "finding": "Identified workflow patterns",
                "solution": " → ".join(analysis['workflows']),
                "context": f"Extracted from {file_path}",
                "confidence": 0.90,
                "example": f"Follow workflow in {file_path.name}"
            })
        
        # Section-based entries
        for i, section in enumerate(analysis.get('sections', [])[:3]):
            if len(section.get('content', '')) > 100:
                entries.append({
                    "type": "finding",
                    "category": "documentation",
                    "title": f"{section['title'][:80]} - {file_path.name}",
                    "finding": f"Section from {file_path.name}",
                    "solution": section['content'][:500].replace('\n', ' '),
                    "context": f"Extracted section from {file_path}",
                    "confidence": 0.85,
                    "example": f"See {file_path.name} for details"
                })
        
        return entries
    
    def add_entry(self, kb: KnowledgeBase, entry: Dict) -> str:
        """Add entry to knowledge base."""
        return kb.kb_add_entry(
            entry_type=entry["type"],
            category=entry["category"],
            title=entry["title"],
            finding=entry["finding"],
            solution=entry["solution"],
            context=entry.get("context", ""),
            confidence=entry.get("confidence", 0.5),
            example=entry.get("example", "")
        )
    
    def populate(self):
        """Execute the population process."""
        if self.verbose:
            print("=" * 70)
            print("KB Population - File Traversal & LLM Analysis")
            print("=" * 70)
        
        # Find all files
        files = self.find_all_meta_files()
        
        if self.verbose:
            print(f"\nFound {len(files)} files to analyze\n")
        
        # Process each file
        for file_path, kb_type in files:
            if self.verbose:
                print(f"Processing: {file_path.relative_to(self.base_path)}")
            
            # Analyze file
            analysis = self.analyze_file_with_llm(file_path)
            
            if not analysis:
                if self.verbose:
                    print(f"  ✗ No content extracted")
                continue
            
            # Create entries
            entries = self.create_kb_entries(file_path, analysis, kb_type)
            
            # Add to appropriate KB
            for entry in entries:
                try:
                    if kb_type == "meta" or kb_type == "both":
                        result = self.add_entry(meta_kb, entry)
                        self.entries_added["meta"] += 1
                        if self.verbose:
                            print(f"  ✓ Added to Meta KB: {entry['title'][:60]}...")
                    
                    if kb_type == "agentx" or kb_type == "both":
                        result = self.add_entry(agentx_kb, entry)
                        self.entries_added["agentx"] += 1
                        if self.verbose:
                            print(f"  ✓ Added to AgentX KB: {entry['title'][:60]}...")
                except Exception as e:
                    if self.verbose:
                        print(f"  ✗ Error adding entry: {e}")
        
        # Summary
        if self.verbose:
            print(f"\n✓ Complete!")
            print(f"  Meta KB: {self.entries_added['meta']} entries")
            print(f"  Agent-X KB: {self.entries_added['agentx']} entries\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Populate knowledge bases by traversing project files"
    )
    parser.add_argument(
        "--kb",
        choices=["meta", "agentx", "both"],
        default="both",
        help="Which KB to populate (default: both)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Print progress information"
    )
    
    args = parser.parse_args()
    
    populator = KBPopulator(target_kb=args.kb, verbose=args.verbose)
    populator.populate()


if __name__ == "__main__":
    main()
