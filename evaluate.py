"""
Evaluation and Benchmarking Script for Domain-Specific RAG.
Runs standardized evaluation across multiple retrieval and reranking configurations,
computing Hit Rate@K, MRR, Refusal Accuracy, Groundedness, and Latency.
Outputs markdown summary table and persists results to JSON.
"""

import os
import sys
import json
import time
from tabulate import tabulate

from src.rag_engine import RAGEngine
from src.metrics import RAGEvaluator

def run_evaluation_suite():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "raw")
    benchmarks_path = os.path.join(base_dir, "data", "eval_benchmarks.json")
    results_path = os.path.join(base_dir, "eval_results.json")

    print("=" * 80)
    print(" DOMAIN-SPECIFIC RAG BENCHMARK EVALUATION SUITE")
    print("=" * 80)

    # Ingest document corpus
    print("\n[1] Initializing RAG Engine and ingesting document corpus...")
    engine = RAGEngine(
        chunk_size=700,
        chunk_overlap=150,
        enable_reranking=True,
        rerank_threshold=0.20
    )
    engine.ingest_documents(data_dir)

    print(f"\n[2] Loading evaluation benchmarks from {benchmarks_path}...")
    evaluator = RAGEvaluator(benchmarks_path)
    print(f"Total benchmark test queries: {len(evaluator.benchmarks)}")

    # Configurations to evaluate (Ablation study)
    configurations = [
        {"name": "Dense Semantic Only (Bi-Encoder)", "mode": "dense", "rerank": False},
        {"name": "Sparse Lexical Only (BM25)", "mode": "sparse", "rerank": False},
        {"name": "Hybrid (Dense + BM25 RRF)", "mode": "hybrid", "rerank": False},
        {"name": "Full System (Hybrid + Cross-Encoder Reranker)", "mode": "hybrid", "rerank": True}
    ]

    all_summaries = []
    table_rows = []

    print("\n[3] Executing Comparative Ablation Benchmarks...\n")
    for cfg in configurations:
        print(f"-> Testing: {cfg['name']}...")
        summary = evaluator.evaluate_engine(
            engine=engine,
            retrieval_mode=cfg["mode"],
            apply_reranking=cfg["rerank"]
        )
        summary["pipeline_name"] = cfg["name"]
        all_summaries.append(summary)

        table_rows.append([
            cfg["name"],
            f"{summary['hit_rate_at_1'] * 100:.1f}%",
            f"{summary['hit_rate_at_3'] * 100:.1f}%",
            f"{summary['mrr']:.3f}",
            f"{summary['refusal_accuracy'] * 100:.1f}%",
            f"{summary['groundedness_score'] * 100:.1f}%",
            f"{summary['avg_latency_ms']:.1f} ms"
        ])

    headers = [
        "Configuration",
        "Hit@1",
        "Hit@3",
        "MRR",
        "Refusal Acc",
        "Groundedness",
        "Avg Latency"
    ]

    print("\n" + "=" * 80)
    print(" BENCHMARK RESULTS MATRIX")
    print("=" * 80)
    table_str = tabulate(table_rows, headers=headers, tablefmt="github")
    print(table_str)
    print("=" * 80)

    # Save detailed evaluation JSON
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)
    print(f"\nEvaluation telemetry saved to: {results_path}")

    return all_summaries

if __name__ == "__main__":
    run_evaluation_suite()
