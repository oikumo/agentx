"""Semantic/recursive/text-aware chunking for KB entries.

Supports three chunking strategies:

1. **RecursiveCharacterChunker** — splits text by separators with overlap,
   suitable for generic KB entry text (title + finding + solution + ...).

2. **MarkdownSectionChunker** — splits Markdown documents by heading levels,
   preserving the heading hierarchy as metadata.

3. **CodeElementChunker** — chunks Python AST elements into docstring +
   code body chunks with parent references.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Chunk data model
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """A single chunk produced by one of the chunkers below.

    Attributes:
        text: The chunk text content.
        parent_id: ID of the original KB entry this chunk belongs to.
        chunk_index: Ordinal position of this chunk within the parent entry.
        chunk_type: One of "full", "section", "recursive_chunk", "docstring".
        section_hierarchy: For markdown sections, the heading chain
                           (e.g., ["Installation", "Quick Start"]).
        metadata: Additional key-value pairs to store alongside the chunk.
    """
    text: str
    parent_id: str = ""
    chunk_index: int = 0
    chunk_type: str = "recursive_chunk"
    section_hierarchy: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Recursive Character Chunker
# ---------------------------------------------------------------------------

class RecursiveCharacterChunker:
    """Split text recursively by a prioritized list of separators.

    Designed for KB entry text bodies. Attempts to split on paragraph
    boundaries first, then newlines, then sentence ends, then spaces,
    then individual characters.

    Args:
        chunk_size: Target character length per chunk (default: 512).
        chunk_overlap: Number of overlapping characters between chunks
                       (default: 64).
        separators: Ordered list of separator strings to split on.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        separators: Optional[List[str]] = None,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Split a single text string into chunks.

        Returns:
            A list of text chunks (strings).
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        return self._split_recursive(text, self.separators)

    def _split_recursive(self, text: str, separators: List[str]) -> List[str]:
        """Recursive split using the ordered list of separators."""

        final_chunks: List[str] = []

        # Try the first separator
        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            # Fallback: split by characters
            return [
                text[i:i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
            ]

        splits = text.split(separator) if separator else [text]

        # Combine splits into chunks of target size
        current_chunks: List[str] = []
        for split in splits:
            split_with_sep = split + separator if separator else split
            if not current_chunks:
                current_chunks.append(split_with_sep)
            elif len(current_chunks[-1]) + len(split_with_sep) < self.chunk_size:
                current_chunks[-1] += split_with_sep
            else:
                current_chunks.append(split_with_sep)

        # If we still have splits that are too large, recurse with next separator
        for chunk in current_chunks:
            if len(chunk) > self.chunk_size and remaining_separators:
                final_chunks.extend(
                    self._split_recursive(chunk, remaining_separators)
                )
            else:
                final_chunks.append(chunk)

        # Apply overlap between adjacent chunks
        return self._apply_overlap(final_chunks)

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap between adjacent chunks."""
        if len(chunks) <= 1 or self.chunk_overlap <= 0:
            return chunks

        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            curr = chunks[i]

            # Take overlap chars from end of previous chunk
            overlap_text = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
            result.append(overlap_text + curr)

        return result

    def chunk_entry(
        self,
        text: str,
        parent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """Split a KB entry's text into Chunk objects.

        Args:
            text: The full entry text to chunk.
            parent_id: The parent KB entry ID.
            metadata: Base metadata to attach to each chunk.

        Returns:
            A list of Chunk objects.
        """
        if not text:
            return []

        metadata = metadata or {}
        chunks = self.split_text(text)
        result: List[Chunk] = []

        for i, chunk_text in enumerate(chunks):
            result.append(Chunk(
                text=chunk_text,
                parent_id=parent_id,
                chunk_index=i,
                chunk_type="recursive_chunk" if len(chunks) > 1 else "full",
                metadata={**metadata, "chunk_count": len(chunks)},
            ))

        return result


# ---------------------------------------------------------------------------
# Markdown Section Chunker
# ---------------------------------------------------------------------------

class MarkdownSectionChunker:
    """Split Markdown documents by heading levels.

    Each top-level section (## or ###) becomes a separate chunk.
    Small consecutive sections are merged to avoid tiny chunks.
    The heading hierarchy is preserved in ``section_hierarchy``.

    Args:
        min_section_chars: Minimum characters for a standalone section.
                           Sections below this are merged with the next.
        max_section_chars: Maximum characters before sub-splitting.
    """

    def __init__(self, min_section_chars: int = 100, max_section_chars: int = 2000):
        self.min_section_chars = min_section_chars
        self.max_section_chars = max_section_chars

    def split_markdown(self, markdown_text: str) -> List[Dict]:
        """Split markdown into structured sections.

        Returns:
            A list of dicts with keys: "heading", "content", "level", "hierarchy".
        """
        if not markdown_text:
            return []

        lines = markdown_text.split("\n")
        sections: List[Dict] = []
        current_heading = ""
        current_level = 0
        current_content: List[str] = []
        hierarchy: List[str] = []

        def flush_section() -> None:
            if current_content or current_heading:
                content = "\n".join(current_content).strip()
                if content or current_heading:
                    sections.append({
                        "heading": current_heading,
                        "content": content,
                        "level": current_level,
                        "hierarchy": list(hierarchy),
                    })

        for line in lines:
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                flush_section()
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()

                # Update hierarchy for this heading level
                while len(hierarchy) >= level:
                    hierarchy.pop()
                hierarchy.append(heading_text)

                current_heading = heading_text
                current_level = level
                current_content = []
            else:
                current_content.append(line)

        flush_section()

        # Merge small adjacent sections
        return self._merge_small_sections(sections)

    def _merge_small_sections(self, sections: List[Dict]) -> List[Dict]:
        """Merge sections below min_section_chars with the next section."""
        if not sections:
            return []

        merged = []
        i = 0
        while i < len(sections):
            section = sections[i]
            section_len = len(section.get("content", ""))

            # If section is too small and there's a next section, merge
            if (section_len < self.min_section_chars
                    and i + 1 < len(sections)
                    and section["level"] <= sections[i + 1]["level"]):
                next_sec = sections[i + 1]
                merged_content = section["content"]
                if next_sec.get("heading"):
                    merged_content += f"\n\n## {next_sec['heading']}\n{next_sec['content']}"
                else:
                    merged_content += f"\n\n{next_sec['content']}"

                merged.append({
                    "heading": section["heading"],
                    "content": merged_content,
                    "level": section["level"],
                    "hierarchy": section["hierarchy"],
                })
                i += 2
            else:
                merged.append(section)
                i += 1

        return merged

    def chunk_markdown(
        self,
        markdown_text: str,
        parent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """Convert a markdown document into Chunk objects, one per section.

        Args:
            markdown_text: The full markdown text.
            parent_id: The parent KB entry ID.
            metadata: Base metadata to attach to each chunk.

        Returns:
            A list of Chunk objects.
        """
        metadata = metadata or {}
        sections = self.split_markdown(markdown_text)

        if not sections:
            return [Chunk(
                text=markdown_text,
                parent_id=parent_id,
                chunk_index=0,
                chunk_type="full",
                metadata=metadata,
            )]

        result: List[Chunk] = []
        for i, section in enumerate(sections):
            heading = section.get("heading", "")
            content = section.get("content", "")
            hierarchy = section.get("hierarchy", [])

            # Build text: include heading if present
            text = f"# {heading}\n{content}" if heading else content

            # If content exceeds max_section_chars, sub-chunk recursively
            if len(text) > self.max_section_chars:
                sub_chunker = RecursiveCharacterChunker(
                    chunk_size=self.max_section_chars,
                    chunk_overlap=64,
                )
                sub_chunks = sub_chunker.split_text(text)
                for j, sub_text in enumerate(sub_chunks):
                    result.append(Chunk(
                        text=sub_text,
                        parent_id=parent_id,
                        chunk_index=len(result),
                        chunk_type="recursive_chunk",
                        section_hierarchy=hierarchy,
                        metadata={**metadata, "heading": heading, "sub_chunk": j},
                    ))
            else:
                result.append(Chunk(
                    text=text,
                    parent_id=parent_id,
                    chunk_index=i,
                    chunk_type="section",
                    section_hierarchy=hierarchy,
                    metadata={**metadata, "heading": heading},
                ))

        return result


# ---------------------------------------------------------------------------
# Code Element Chunker
# ---------------------------------------------------------------------------

class CodeElementChunker:
    """Chunk Python AST code elements (classes, methods, functions).

    Produces separate chunks for the docstring (if present) and code body.
    """

    def chunk_code_element(
        self,
        name: str,
        element_type: str,
        docstring: Optional[str],
        code_body: str,
        parent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """Chunk a single code element into docstring + body chunks.

        Args:
            name: Element name (e.g., "MyClass.my_method").
            element_type: "class", "method", or "function".
            docstring: Extracted docstring text (may be None).
            code_body: Full source code of the element.
            parent_id: Parent KB entry ID.
            metadata: Additional metadata.

        Returns:
            A list of Chunk objects.
        """
        metadata = metadata or {}
        chunks: List[Chunk] = []
        base_meta = {**metadata, "element_name": name, "element_type": element_type}

        # Docstring chunk
        if docstring:
            chunks.append(Chunk(
                text=docstring,
                parent_id=parent_id,
                chunk_index=0,
                chunk_type="docstring",
                metadata={**base_meta, "part": "docstring"},
            ))

        # Code body chunk
        body_start_index = 1 if docstring else 0
        if len(code_body) > 512:
            # Recursively chunk long code bodies
            recursive = RecursiveCharacterChunker(chunk_size=512, chunk_overlap=64)
            body_chunks = recursive.split_text(code_body)
            for i, body_text in enumerate(body_chunks):
                chunks.append(Chunk(
                    text=body_text,
                    parent_id=parent_id,
                    chunk_index=body_start_index + i,
                    chunk_type="recursive_chunk",
                    metadata={**base_meta, "part": "code_body", "sub_chunk": i},
                ))
        else:
            chunks.append(Chunk(
                text=code_body,
                parent_id=parent_id,
                chunk_index=body_start_index,
                chunk_type="full",
                metadata={**base_meta, "part": "code_body"},
            ))

        return chunks


# ---------------------------------------------------------------------------
# Convenience: chunk a full KB entry text
# ---------------------------------------------------------------------------

def chunk_entry_text(
    text: str,
    parent_id: str,
    source_type: str = "kb_entry",
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[Chunk]:
    """Convenience function to chunk any KB entry text.

    Args:
        text: The full text to chunk.
        parent_id: Parent entry ID.
        source_type: One of "kb_entry", "markdown", "code".
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between chunks.
        metadata: Additional metadata.

    Returns:
        A list of Chunk objects.
    """
    if source_type == "markdown":
        chunker = MarkdownSectionChunker()
        return chunker.chunk_markdown(text, parent_id, metadata)
    else:
        chunker = RecursiveCharacterChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return chunker.chunk_entry(text, parent_id, metadata)
