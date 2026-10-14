"""
Command-Line Interface for Domain-Specific Document Question Answering (RAG).
Usage:
    python3 main.py --query "What is the minimum attendance requirement?"
    python3 main.py --interactive
    python3 main.py --docs data/raw/
"""

import os
import sys
import argparse
from src.rag_engine import RAGEngine

def print_separator(char="=", length=80):
    print(char * length)

def main():
    parser = argparse.ArgumentParser(
        description="Domain-Specific Document Question Answering System using RAG",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--docs", type=str, default="data/raw", help="Path to document file or directory")
    parser.add_argument("--query", type=str, default=None, help="Question to ask the system")
    parser.add_argument("--mode", type=str, choices=["dense", "sparse", "hybrid"], default="hybrid", help="Retrieval strategy")
    parser.add_argument("--top_k", type=int, default=3, help="Number of final context passages to consider")
    parser.add_argument("--no-rerank", action="store_true", help="Disable Cross-Encoder neural reranker")
    parser.add_argument("--threshold", type=float, default=0.20, help="Confidence threshold for refusal guardrail")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive multi-turn query CLI loop")

    args = parser.parse_args()

    # Determine absolute path to data if relative
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_path = os.path.join(base_dir, args.docs) if not os.path.isabs(args.docs) else args.docs

    print_separator()
    print(" DOMAIN-SPECIFIC QUESTION ANSWERING SYSTEM USING RAG")
    print(" Office of Academic Affairs | HR Regulations | Municipal Circulars")
    print_separator()

    # Initialize Engine
    engine = RAGEngine(
        chunk_size=700,
        chunk_overlap=150,
        enable_reranking=not args.no_rerank,
        rerank_threshold=args.threshold
    )

    print(f"\n[1] Ingesting documents from: {docs_path}")
    engine.ingest_documents(docs_path)

    def process_query(q_str: str):
        print(f"\n[QUERY]: {q_str}")
        print("-" * 80)
        res = engine.query(
            question=q_str,
            retrieval_mode=args.mode,
            top_k=args.top_k,
            confidence_threshold=args.threshold
        )

        if res.is_refused:
            print("\n[GUARDRAIL STATUS]: \033[91mQUESTION REFUSED (Out-of-Domain / Low Grounding)\033[0m")
            print(res.answer)
        else:
            print("\n[GUARDRAIL STATUS]: \033[92mGROUNDED ANSWER VERIFIED\033[0m")
            print("\n" + res.answer)

        print("\n" + "-" * 80)
        print(f"[TELEMETRY]: Retrieval: {res.telemetry.get('retrieval_ms', 0):.1f}ms | "
              f"Reranking: {res.telemetry.get('rerank_ms', 0):.1f}ms | "
              f"Total: {res.telemetry.get('total_ms', 0):.1f}ms")
        print_separator()

    if args.interactive:
        print("\nEntering Interactive Mode. Type 'exit' or 'quit' to stop.\n")
        while True:
            try:
                user_q = input("\nAsk a question: ").strip()
                if not user_q:
                    continue
                if user_q.lower() in ["exit", "quit", "q"]:
                    print("Exiting RAG system.")
                    break
                process_query(user_q)
            except (KeyboardInterrupt, EOFError):
                print("\nSession ended.")
                break
    elif args.query:
        process_query(args.query)
    else:
        # Default demonstration queries
        sample_queries = [
            "What is the minimum attendance percentage required to appear in the final exam?",
            "How much paid parental leave is provided to employees?",
            "What is the capital of Australia and what is its population?"
        ]
        print("\nNo query specified. Running default demonstration queries across domains:\n")
        for q in sample_queries:
            process_query(q)

if __name__ == "__main__":
    main()
