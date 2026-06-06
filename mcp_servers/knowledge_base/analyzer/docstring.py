#!/usr/bin/env python3
"""
Docstring parser for KB MCP v4.

Parses Google, NumPy, and reStructuredText docstring formats.
"""

import re
from typing import Optional
from dataclasses import dataclass, field

from graph.models import DocstringInfo


@dataclass
class ParsedDocstring:
    """Complete parsed docstring with all components."""
    summary: str = ""
    description: str = ""
    args: dict[str, str] = field(default_factory=dict)
    returns: Optional[str] = None
    raises: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    style: str = "unknown"  # google, numpy, rst, unknown


class DocstringParser:
    """
    Multi-format docstring parser.
    
    Supports:
    - Google style: Args:, Returns:, Raises:, Examples:
    - NumPy style: Parameters, Returns, Raises, Examples
    - reStructuredText: :param, :returns:, :raises:, .. example::
    
    Usage:
        parser = DocstringParser()
        parsed = parser.parse(docstring_text)
    """
    
    # Regex patterns for different formats
    GOOGLE_ARGS_PATTERN = re.compile(
        r'Args?:\s*\n(.*?)(?=\n\s*[A-Z][a-z]+:|\Z)',
        re.DOTALL | re.IGNORECASE,
    )
    GOOGLE_ARG_PATTERN = re.compile(
        r'^\s+(\w+)(?:\s*\([^)]+\))?:\s*(.+?)(?=\n\s+\w+|\Z)',
        re.MULTILINE | re.DOTALL,
    )
    
    RST_PARAM_PATTERN = re.compile(
        r':param\s+(\w+):\s*(.+?)(?=:param\s|\Z)',
        re.DOTALL | re.IGNORECASE,
    )
    RST_RETURNS_PATTERN = re.compile(
        r':returns?:\s*(.+?)(?=:param\s|\Z)',
        re.DOTALL | re.IGNORECASE,
    )
    RST_RAISES_PATTERN = re.compile(
        r':raises?\s+(\w+):?\s*(.+?)(?=:raises?|\Z)',
        re.DOTALL | re.IGNORECASE,
    )
    
    NUMPY_SECTION_PATTERN = re.compile(
        r'^([A-Z][a-zA-Z\s]+)\s*\n\s*-+\s*\n(.*?)(?=\n[A-Z][a-zA-Z\s]+\s*\n\s*-+|\Z)',
        re.MULTILINE | re.DOTALL,
    )
    NUMPY_PARAM_PATTERN = re.compile(
        r'^(\w+)\s*:\s*(\w+)?\s*\n\s+(.+?)(?=\n\w+\s*:|\Z)',
        re.MULTILINE | re.DOTALL,
    )
    
    EXAMPLES_PATTERN = re.compile(
        r'(?:Examples?:|>>>|.. code-block::|::)\s*\n(.*?)(?=\n[A-Z][a-z]+:|\Z)',
        re.DOTALL | re.IGNORECASE,
    )
    
    METADATA_PATTERN = re.compile(
        r'@(?:author|version|since|copyright|license|deprecated|note):\s*(.+?)(?=\n@|\Z)',
        re.DOTALL | re.IGNORECASE,
    )
    
    def __init__(self):
        """Initialize docstring parser."""
        self.parsed: Optional[ParsedDocstring] = None
    
    def parse(self, docstring: str) -> ParsedDocstring:
        """
        Parse a docstring, auto-detecting format.
        
        Args:
            docstring: Raw docstring text
            
        Returns:
            ParsedDocstring with all components
        """
        if not docstring or not docstring.strip():
            return ParsedDocstring()
        
        self.parsed = ParsedDocstring()
        docstring = docstring.strip()
        
        # Detect format
        style = self._detect_style(docstring)
        self.parsed.style = style
        
        # Extract summary and description
        self._extract_summary_description(docstring)
        
        # Parse based on detected style
        if style == 'google':
            self.parse_google_style(docstring)
        elif style == 'numpy':
            self.parse_numpy_style(docstring)
        elif style == 'rst':
            self.parse_rst(docstring)
        else:
            # Try all parsers
            self.parse_google_style(docstring)
            self.parse_numpy_style(docstring)
            self.parse_rst(docstring)
        
        # Extract common elements
        self._extract_examples(docstring)
        self._extract_metadata(docstring)
        
        return self.parsed
    
    def _detect_style(self, docstring: str) -> str:
        """
        Detect docstring style.
        
        Args:
            docstring: Raw docstring text
            
        Returns:
            Style name: 'google', 'numpy', 'rst', or 'unknown'
        """
        # Check for NumPy style (section headers with dashes)
        if re.search(r'^[A-Z][a-zA-Z\s]+\s*\n\s*-+\s*', docstring, re.MULTILINE):
            return 'numpy'
        
        # Check for reStructuredText
        if re.search(r':param\s+\w+:|:returns?:|:raises?\s+\w+', docstring):
            return 'rst'
        
        # Check for Google style
        if re.search(r'\b(?:Args?|Returns?|Raises?|Examples?):\s*\n', docstring):
            return 'google'
        
        return 'unknown'
    
    def _extract_summary_description(self, docstring: str) -> None:
        """
        Extract summary and description from docstring.
        
        Args:
            docstring: Raw docstring text
        """
        lines = docstring.split('\n')
        
        # Find first blank line or section header
        summary_end = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check for section headers
            if re.match(r'^(Args?|Returns?|Raises?|Examples?|Parameters|Returns|Raises|Examples):', stripped):
                summary_end = i
                break
            
            # Check for NumPy-style section
            if i + 1 < len(lines) and re.match(r'^-+\s*$', lines[i + 1].strip()):
                summary_end = i
                break
            
            # Check for RST directives
            if stripped.startswith(':param') or stripped.startswith(':returns'):
                summary_end = i
                break
            
            # Blank line ends summary
            if not stripped:
                if summary_end == 0:
                    summary_end = i
                break
        
        # Extract summary (first paragraph)
        if summary_end > 0:
            self.parsed.summary = ' '.join(line.strip() for line in lines[:summary_end] if line.strip())
        elif lines:
            self.parsed.summary = lines[0].strip()
        
        # Extract description (everything until first section)
        description_lines = []
        in_description = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip if we hit a section
            if re.match(r'^(Args?|Returns?|Raises?|Examples?|Parameters|Returns|Raises|Examples):', stripped):
                break
            if re.match(r'^-+\s*$', stripped):
                break
            if stripped.startswith(':param') or stripped.startswith(':returns'):
                break
            
            # Start collecting description after summary
            if not stripped and self.parsed.summary:
                in_description = True
                continue
            
            if in_description and stripped:
                description_lines.append(stripped)
        
        self.parsed.description = ' '.join(description_lines)
    
    def parse_google_style(self, docstring: str) -> None:
        """
        Parse Google-style docstring.
        
        Format:
            Summary line.
            
            Description paragraph.
            
            Args:
                param1: Description
                param2: Description
            
            Returns:
                Description
            
            Raises:
                ValueError: Description
        
        Args:
            docstring: Raw docstring text
        """
        # Extract Args section
        args_match = self.GOOGLE_ARGS_PATTERN.search(docstring)
        if args_match:
            args_section = args_match.group(1)
            for arg_match in self.GOOGLE_ARG_PATTERN.finditer(args_section):
                arg_name = arg_match.group(1)
                arg_desc = arg_match.group(2).strip()
                self.parsed.args[arg_name] = arg_desc
        
        # Extract Returns section
        returns_match = re.search(
            r'Returns?:\s*\n\s+(.+?)(?=\n\s*[A-Z][a-z]+:|\Z)',
            docstring,
            re.DOTALL | re.IGNORECASE,
        )
        if returns_match:
            self.parsed.returns = returns_match.group(1).strip()
        
        # Extract Raises section
        raises_match = re.search(
            r'Raises?:\s*\n(.*?)(?=\n\s*[A-Z][a-z]+:|\Z)',
            docstring,
            re.DOTALL | re.IGNORECASE,
        )
        if raises_match:
            raises_section = raises_match.group(1)
            for line in raises_section.split('\n'):
                line = line.strip()
                if line:
                    # Parse "ExceptionType: description" or just "ExceptionType"
                    if ':' in line:
                        exc_type = line.split(':')[0].strip()
                    else:
                        exc_type = line
                    self.parsed.raises.append(exc_type)
    
    def parse_numpy_style(self, docstring: str) -> None:
        """
        Parse NumPy-style docstring.
        
        Format:
            Summary line.
            
            Description paragraph.
            
            Parameters
            ----------
            param1 : type
                Description
            param2 : type
                Description
            
            Returns
            -------
            type
                Description
        
        Args:
            docstring: Raw docstring text
        """
        sections = self.NUMPY_SECTION_PATTERN.findall(docstring)
        
        for section_title, section_content in sections:
            section_title = section_title.strip().lower()
            
            if section_title in ('parameters', 'arguments', 'args'):
                for param_match in self.NUMPY_PARAM_PATTERN.finditer(section_content):
                    param_name = param_match.group(1)
                    param_desc = param_match.group(3).strip()
                    self.parsed.args[param_name] = param_desc
            
            elif section_title in ('returns', 'return'):
                # NumPy returns section may have type on first line
                lines = section_content.strip().split('\n')
                if lines:
                    self.parsed.returns = ' '.join(line.strip() for line in lines if line.strip())
            
            elif section_title in ('raises', 'raise'):
                for line in section_content.split('\n'):
                    line = line.strip()
                    if line:
                        # Parse "ExceptionType" or "ExceptionType : description"
                        exc_type = line.split(':')[0].split(' :')[0].strip()
                        self.parsed.raises.append(exc_type)
            
            elif section_title in ('examples', 'example'):
                self.parsed.examples.append(section_content.strip())
    
    def parse_rst(self, docstring: str) -> None:
        """
        Parse reStructuredText-style docstring.
        
        Format:
            Summary line.
            
            Description paragraph.
            
            :param name: Description
            :returns: Description
            :raises ValueError: Description
        
        Args:
            docstring: Raw docstring text
        """
        # Extract parameters
        for param_match in self.RST_PARAM_PATTERN.finditer(docstring):
            param_name = param_match.group(1)
            param_desc = param_match.group(2).strip()
            self.parsed.args[param_name] = param_desc
        
        # Extract returns
        returns_match = self.RST_RETURNS_PATTERN.search(docstring)
        if returns_match:
            self.parsed.returns = returns_match.group(1).strip()
        
        # Extract raises
        for raises_match in self.RST_RAISES_PATTERN.finditer(docstring):
            exc_type = raises_match.group(1)
            self.parsed.raises.append(exc_type)
    
    def _extract_examples(self, docstring: str) -> None:
        """
        Extract examples from any docstring format.
        
        Args:
            docstring: Raw docstring text
        """
        examples_match = self.EXAMPLES_PATTERN.search(docstring)
        if examples_match:
            examples_text = examples_match.group(1).strip()
            
            # Split by >>> for doctest style
            if '>>>' in examples_text:
                for example in examples_text.split('>>>'):
                    example = example.strip()
                    if example:
                        self.parsed.examples.append('>>>' + example)
            else:
                self.parsed.examples.append(examples_text)
    
    def _extract_metadata(self, docstring: str) -> None:
        """
        Extract metadata tags from docstring.
        
        Args:
            docstring: Raw docstring text
        """
        for meta_match in self.METADATA_PATTERN.finditer(docstring):
            # Extract tag and value
            text = meta_match.group(0)
            if ':' in text:
                tag, value = text.split(':', 1)
                tag = tag.strip().lstrip('@').lower()
                value = value.strip()
                self.parsed.metadata[tag] = value
    
    def to_docstring_info(self, parsed: Optional[ParsedDocstring] = None) -> Optional[DocstringInfo]:
        """
        Convert ParsedDocstring to DocstringInfo model.
        
        Args:
            parsed: ParsedDocstring to convert (uses self.parsed if None)
            
        Returns:
            DocstringInfo for use in Entity model
        """
        if parsed is None:
            parsed = self.parsed
        
        if not parsed:
            return None
        
        return DocstringInfo(
            summary=parsed.summary,
            description=parsed.description,
            args=parsed.args,
            returns=parsed.returns,
            raises=parsed.raises,
            examples=parsed.examples,
        )
    
    def parse_to_info(self, docstring: str) -> Optional[DocstringInfo]:
        """
        Parse docstring and return DocstringInfo directly.
        
        Args:
            docstring: Raw docstring text
            
        Returns:
            DocstringInfo for use in Entity model
        """
        parsed = self.parse(docstring)
        return self.to_docstring_info(parsed)
    
    def get_style(self) -> str:
        """
        Get detected style from last parse.
        
        Returns:
            Style name: 'google', 'numpy', 'rst', or 'unknown'
        """
        return self.parsed.style if self.parsed else 'unknown'
    
    def has_returns(self) -> bool:
        """Check if docstring has return value documentation."""
        return bool(self.parsed and self.parsed.returns)
    
    def has_args(self) -> bool:
        """Check if docstring has parameter documentation."""
        return bool(self.parsed and self.parsed.args)
    
    def is_complete(self) -> bool:
        """
        Check if docstring is complete (has summary, args, and returns).
        
        Returns:
            True if docstring appears complete
        """
        if not self.parsed:
            return False
        
        return bool(
            self.parsed.summary and
            (self.parsed.args or not self._needs_args()) and
            self.parsed.returns
        )
    
    def _needs_args(self) -> bool:
        """Check if function likely needs args documentation."""
        # Heuristic: if summary mentions parameters, likely needs args
        if not self.parsed:
            return False
        
        summary_lower = self.parsed.summary.lower()
        return any(word in summary_lower for word in ['param', 'arg', 'input', 'takes'])