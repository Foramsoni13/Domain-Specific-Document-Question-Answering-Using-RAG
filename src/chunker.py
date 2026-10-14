"""
Text Chunking Module for Domain-Specific RAG.
Implements Recursive Character Chunking and Sentence-Window Chunking
with metadata preservation and boundary overlap management.
"""

import os
import re
from typing import List, Dict, Any, Optional
from src.document_loader import DocumentPage

class TextChunk:
    """Represents a discrete chunk of text extracted from a document page."""
    def __init__(
        self,
        chunk_id: str,
        doc_name: str,
        page_number: int,
        content: str,
        chunk_index: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.doc_name = doc_name
        self.page_number = page_number
        self.content = content.strip()
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        self.char_count = len(self.content)
        self.word_count = len(self.content.split())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_name": self.doc_name,
            "page_number": self.page_number,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "char_count": self.char_count,
            "word_count": self.word_count,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        snippet = self.content[:50].replace("\n", " ") + "..." if len(self.content) > 50 else self.content
        return f"<TextChunk id='{self.chunk_id}' page={self.page_number} words={self.word_count} text='{snippet}'>"


class RecursiveCharacterChunker:
    """
    Splits text recursively using hierarchical separators:
    1. Double newlines (paragraphs)
    2. Single newlines (lines / bullet points)
    3. Sentence terminators (. ! ?)
    4. Word spaces
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be smaller than chunk_size ({chunk_size})")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively splits text into chunks under chunk_size."""
        final_chunks: List[str] = []
        if not text:
            return final_chunks

        # Pick the highest priority separator present in the text
        separator = ""
        new_separators = []
        for i, sep in enumerate(separators):
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        if not separator:
            # No separators found; split by raw character length
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

        splits = text.split(separator)
        good_splits: List[str] = []

        for s in splits:
            if not s:
                continue
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if new_separators:
                    sub_splits = self._split_text(s, new_separators)
                    good_splits.extend(sub_splits)
                else:
                    # Fallback character slicing
                    for j in range(0, len(s), self.chunk_size - self.chunk_overlap):
                        good_splits.append(s[j:j + self.chunk_size])

        # Merge small adjacent splits up to chunk_size with chunk_overlap
        current_chunk = []
        current_length = 0

        for piece in good_splits:
            piece_len = len(piece) + (len(separator) if current_chunk else 0)
            if current_length + piece_len <= self.chunk_size:
                current_chunk.append(piece)
                current_length += piece_len
            else:
                if current_chunk:
                    merged = separator.join(current_chunk).strip()
                    if merged:
                        final_chunks.append(merged)
                    # Manage overlap: keep the trailing elements
                    overlap_accum = []
                    overlap_len = 0
                    for rev_piece in reversed(current_chunk):
                        if overlap_len + len(rev_piece) <= self.chunk_overlap:
                            overlap_accum.insert(0, rev_piece)
                            overlap_len += len(rev_piece)
                        else:
                            break
                    current_chunk = overlap_accum + [piece]
                    current_length = sum(len(p) for p in current_chunk) + (len(separator) * max(0, len(current_chunk) - 1))
                else:
                    final_chunks.append(piece.strip())

        if current_chunk:
            merged = separator.join(current_chunk).strip()
            if merged and (not final_chunks or merged != final_chunks[-1]):
                final_chunks.append(merged)

        return final_chunks

    def chunk_document_page(self, page: DocumentPage) -> List[TextChunk]:
        """Splits a single DocumentPage into TextChunks while preserving page metadata."""
        raw_text = page.content.strip()
        if not raw_text:
            return []

        text_pieces = self._split_text(raw_text, self.separators)
        chunks: List[TextChunk] = []

        # Clean document name for ID prefix
        clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", os.path.splitext(page.doc_name)[0])

        for idx, piece in enumerate(text_pieces):
            piece_clean = piece.strip()
            if len(piece_clean) < 15:  # skip trivial whitespace or single numbers
                continue

            chunk_id = f"{clean_name}_p{page.page_number}_c{idx + 1}"
            chunks.append(TextChunk(
                chunk_id=chunk_id,
                doc_name=page.doc_name,
                page_number=page.page_number,
                content=piece_clean,
                chunk_index=idx,
                metadata={
                    **page.metadata,
                    "chunk_size": len(piece_clean),
                    "split_strategy": "recursive_character"
                }
            ))

        return chunks

    def chunk_document_pages(self, pages: List[DocumentPage]) -> List[TextChunk]:
        """Chunks a collection of DocumentPages across documents."""
        all_chunks: List[TextChunk] = []
        for page in pages:
            page_chunks = self.chunk_document_page(page)
            all_chunks.extend(page_chunks)
        return all_chunks
