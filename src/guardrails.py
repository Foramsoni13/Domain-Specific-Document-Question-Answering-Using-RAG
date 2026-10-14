"""
Guardrails Module for Domain-Specific RAG.
Identifies out-of-domain, unanswerable, or low-confidence queries to prevent
hallucinations, providing transparent, grounded refusal messages.
"""

import re
from typing import List, Tuple, Dict, Any, Optional
from src.vector_store import SearchResult

class GuardrailVerdict:
    """Represents the safety and answerability verdict for a given user query."""
    def __init__(
        self,
        is_answerable: bool,
        confidence_score: float,
        reason: Optional[str] = None,
        top_chunk: Optional[SearchResult] = None
    ):
        self.is_answerable = is_answerable
        self.confidence_score = float(confidence_score)
        self.reason = reason
        self.top_chunk = top_chunk

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_answerable": self.is_answerable,
            "confidence_score": round(self.confidence_score, 4),
            "reason": self.reason
        }

    def __repr__(self) -> str:
        return f"<GuardrailVerdict answerable={self.is_answerable} conf={self.confidence_score:.3f} reason='{self.reason}'>"


class RAGGuardrails:
    """
    Multi-stage verification system:
    1. Confidence Threshold Verification (using calibrated Cross-Encoder / Cosine scores)
    2. Query-Context Lexical & Semantic Overlap
    3. Transparent Refusal Message Generation
    """

    def __init__(
        self,
        rerank_threshold: float = 0.20,
        similarity_threshold: float = 0.35,
        min_keyword_overlap_ratio: float = 0.15
    ):
        self.rerank_threshold = rerank_threshold
        self.similarity_threshold = similarity_threshold
        self.min_keyword_overlap_ratio = min_keyword_overlap_ratio

    def evaluate_answerability(
        self,
        query: str,
        retrieved_results: List[SearchResult]
    ) -> GuardrailVerdict:
        """
        Assesses whether the retrieved passages contain sufficient, trustworthy
        information to answer the user query.
        """
        if not retrieved_results:
            return GuardrailVerdict(
                is_answerable=False,
                confidence_score=0.0,
                reason="No candidate passages could be retrieved from the document corpus."
            )

        top_match = retrieved_results[0]
        score = top_match.score

        # 1. Reranker / Similarity threshold check
        is_cross_encoded = top_match.retrieval_type == "cross_encoder_reranked"
        active_threshold = self.rerank_threshold if is_cross_encoded else self.similarity_threshold

        if score < active_threshold:
            return GuardrailVerdict(
                is_answerable=False,
                confidence_score=score,
                reason=f"Top candidate passage relevance score ({score:.3f}) falls below the confidence threshold ({active_threshold:.2f}).",
                top_chunk=top_match
            )

        # 2. Key entity / content word overlap check
        q_tokens = self._extract_informative_tokens(query)
        if q_tokens:
            top_content_lower = top_match.chunk.content.lower()
            matching_tokens = [t for t in q_tokens if t in top_content_lower]
            overlap_ratio = len(matching_tokens) / len(q_tokens)

            # If score is marginal and there is zero keyword overlap, flag as unanswerable
            if overlap_ratio == 0.0 and score < (active_threshold + 0.15):
                return GuardrailVerdict(
                    is_answerable=False,
                    confidence_score=score,
                    reason=f"The query keywords {q_tokens[:4]} have zero presence in the most relevant retrieved passages.",
                    top_chunk=top_match
                )

        return GuardrailVerdict(
            is_answerable=True,
            confidence_score=score,
            reason="Passages satisfy confidence and semantic grounding thresholds.",
            top_chunk=top_match
        )

    @staticmethod
    def _extract_informative_tokens(text: str) -> List[str]:
        """Filters out common English stopwords to focus on content words and domain terms."""
        stopwords = {
            "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "can", "could", "should", "would", "may", "might",
            "must", "the", "a", "an", "and", "or", "but", "if", "because", "as",
            "until", "while", "of", "at", "by", "for", "with", "about", "against",
            "between", "into", "through", "during", "before", "after", "above", "below",
            "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
            "again", "further", "then", "once", "here", "there", "all", "any", "both",
            "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "s", "t", "just", "don",
            "now", "tell", "me", "please", "give", "explain"
        }
        tokens = re.findall(r"\b[a-zA-Z0-9_\$%-]+\b", text.lower())
        return [t for t in tokens if t not in stopwords and len(t) > 2]

    @staticmethod
    def generate_refusal_message(query: str, verdict: GuardrailVerdict) -> str:
        """Constructs a concise, direct refusal explaining that the answer is not in the documents."""
        return (
            f"**Not found in documents**: This question cannot be answered from the provided documents.\n\n"
            f"**Reason**: {verdict.reason}\n\n"
            f"*To prevent hallucinations, queries with low confidence ({verdict.confidence_score:.3f}) are safely declined.*"
        )
