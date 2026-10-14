"""
Evaluation and Metrics Module for Domain-Specific RAG.
Computes:
- Precision@K, Recall@K, Hit Rate@K, MRR (Mean Reciprocal Rank)
- Refusal Accuracy (Out-of-Domain Detection)
- Groundedness / Faithfulness Score
- Latency and Ablation Comparison
"""

import json
from typing import List, Dict, Any, Optional
import numpy as np

class RAGEvaluator:
    """Evaluates RAG pipeline performance against standardized ground truth benchmarks."""

    def __init__(self, benchmark_path: str):
        with open(benchmark_path, "r", encoding="utf-8") as f:
            self.benchmarks = json.load(f)

    @staticmethod
    def calculate_hit_rate(retrieved_pages: List[int], expected_page: Optional[int], k: int = 3) -> float:
        """Returns 1.0 if the expected page appears within the top k retrieved pages, else 0.0."""
        if expected_page is None:
            return 0.0
        return 1.0 if expected_page in retrieved_pages[:k] else 0.0

    @staticmethod
    def calculate_reciprocal_rank(retrieved_pages: List[int], expected_page: Optional[int]) -> float:
        """Returns 1 / rank of the first occurrence of expected page, or 0.0 if not found."""
        if expected_page is None:
            return 0.0
        for rank, p in enumerate(retrieved_pages, start=1):
            if p == expected_page:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def calculate_precision_at_k(retrieved_docs: List[str], expected_doc: Optional[str], k: int = 3) -> float:
        """Calculates fraction of retrieved documents in top k matching the ground truth document."""
        if not expected_doc or k <= 0:
            return 0.0
        matches = sum(1 for d in retrieved_docs[:k] if expected_doc in d)
        return matches / k

    @staticmethod
    def calculate_groundedness(answer: str, key_entities: List[str]) -> float:
        """Calculates proportion of ground-truth key entities captured in the generated answer."""
        if not key_entities:
            return 1.0
        ans_lower = answer.lower()
        found = sum(1 for entity in key_entities if entity.lower() in ans_lower)
        return found / len(key_entities)

    def evaluate_engine(self, engine, retrieval_mode: str = "hybrid", apply_reranking: bool = True) -> Dict[str, Any]:
        """
        Runs complete benchmark evaluation on the given RAGEngine configuration.
        """
        results_list = []
        hit_rates_k = {1: [], 3: [], 5: []}
        reciprocal_ranks = []
        precision_at_3 = []
        groundedness_scores = []
        refusal_correctness = []
        latencies = []

        for item in self.benchmarks:
            q = item["question"]
            is_ans = item["is_answerable"]
            expected_doc = item["expected_doc"]
            expected_page = item["expected_page"]
            entities = item.get("key_entities", [])

            response = engine.query(
                question=q,
                retrieval_mode=retrieval_mode,
                top_k=5,
                apply_reranking=apply_reranking
            )

            latencies.append(response.telemetry.get("total_ms", 0.0))

            # Check Refusal behavior
            if not is_ans:
                # Expected to refuse
                refused_correctly = response.is_refused
                refusal_correctness.append(1.0 if refused_correctly else 0.0)
            else:
                # Expected to answer
                answered_correctly = not response.is_refused
                refusal_correctness.append(1.0 if answered_correctly else 0.0)

                # Extract retrieved pages and doc names
                retrieved_pages = [r.chunk.page_number for r in response.retrieved_chunks]
                retrieved_docs = [r.chunk.doc_name for r in response.retrieved_chunks]

                for k in [1, 3, 5]:
                    hit_rates_k[k].append(self.calculate_hit_rate(retrieved_pages, expected_page, k=k))

                reciprocal_ranks.append(self.calculate_reciprocal_rank(retrieved_pages, expected_page))
                precision_at_3.append(self.calculate_precision_at_k(retrieved_docs, expected_doc, k=3))
                groundedness_scores.append(self.calculate_groundedness(response.answer, entities))

            results_list.append({
                "id": item["id"],
                "question": q,
                "is_answerable": is_ans,
                "was_refused": response.is_refused,
                "top_score": response.guardrail_verdict.confidence_score,
                "citations_count": len(response.citations),
                "latency_ms": response.telemetry.get("total_ms", 0.0)
            })

        summary = {
            "retrieval_mode": retrieval_mode,
            "reranking_enabled": apply_reranking,
            "total_queries": len(self.benchmarks),
            "hit_rate_at_1": round(float(np.mean(hit_rates_k[1])) if hit_rates_k[1] else 0.0, 4),
            "hit_rate_at_3": round(float(np.mean(hit_rates_k[3])) if hit_rates_k[3] else 0.0, 4),
            "hit_rate_at_5": round(float(np.mean(hit_rates_k[5])) if hit_rates_k[5] else 0.0, 4),
            "mrr": round(float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0, 4),
            "precision_at_3": round(float(np.mean(precision_at_3)) if precision_at_3 else 0.0, 4),
            "groundedness_score": round(float(np.mean(groundedness_scores)) if groundedness_scores else 0.0, 4),
            "refusal_accuracy": round(float(np.mean(refusal_correctness)) if refusal_correctness else 0.0, 4),
            "avg_latency_ms": round(float(np.mean(latencies)) if latencies else 0.0, 2),
            "detailed_results": results_list
        }
        return summary
