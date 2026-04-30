"""
RAG Ablation Evaluation
=======================

Measures accuracy across three conditions on the 54-question synthetic eval set:

  Condition 0 — LLM-only     : raw GPT answer, no retrieval
  Condition 1 — RAG           : top-3 by cosine similarity
  Condition 2 — RAG + rerank  : top-10 cosine → CrossEncoder → top-3

Usage:
    # Index synthetic corpus first, then run all 3 conditions:
    python rag_eval.py --index-first

    # Index only a subset (faster / cheaper for smoke-tests):
    python rag_eval.py --index-first --subset 300

    # Skip re-indexing if already done:
    python rag_eval.py

    # Skip LLM-only condition (saves API calls):
    python rag_eval.py --skip-llm-only

    # Cap eval questions per condition:
    python rag_eval.py --limit 10

    # Use a custom ChromaDB path:
    python rag_eval.py --db-path path/to/vector_db

Output:
    data/eval_results.json   — per-condition + per-question detail
    Console table            — accuracy / latency / pass counts by category

NOTE: Uses a SEPARATE eval vector DB (data/eval_vectordb/) so the production
      DB (backend/database/vector_db/) is never modified by this script.
"""

import argparse
import json
import os
import random
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from tqdm import tqdm

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent
EVAL_QA_PATH  = REPO_ROOT / "data" / "eval_qa.json"
CORPUS_ROOT   = REPO_ROOT / "data" / "synthetic_docs"
OUT_PATH      = REPO_ROOT / "data" / "eval_results.json"
DEFAULT_DB_PATH = str(REPO_ROOT / "data" / "eval_vectordb")

CHUNK_SIZE    = 500
CHUNK_OVERLAP = 150

# ---------------------------------------------------------------------------
# Corpus indexing
# ---------------------------------------------------------------------------

def _collect_files(
    corpus_root: Path,
    subset: int | None,
    subdirs: tuple[str, ...] = ("policy", "distractor", "noise"),
) -> list[Path]:
    """Return txt/md files from the corpus, optionally capped at *subset*."""
    all_files: list[Path] = []
    for subdir in subdirs:
        d = corpus_root / subdir
        if d.exists():
            all_files.extend(d.glob("*.txt"))
            all_files.extend(d.glob("*.md"))

    if subset and subset < len(all_files):
        random.seed(42)
        all_files = random.sample(all_files, subset)

    return sorted(all_files)


def build_eval_db(
    db_path: str,
    corpus_root: Path,
    embeddings: OpenAIEmbeddings,
    subset: int | None,
    force_rebuild: bool,
    subdirs: tuple[str, ...] = ("policy", "distractor", "noise"),
) -> Chroma:
    """Build (or reuse) the eval-only vector DB from the synthetic corpus."""
    path = Path(db_path)

    if path.exists() and not force_rebuild:
        existing = Chroma(persist_directory=db_path, embedding_function=embeddings)
        n = existing._collection.count()
        if n > 0:
            print(f"Reusing existing eval DB ({n} chunks) at {db_path}")
            return existing
        shutil.rmtree(db_path)

    files = _collect_files(corpus_root, subset, subdirs=subdirs)
    print(f"Indexing {len(files)} corpus files into {db_path} …")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )

    all_chunks = []
    for fp in tqdm(files, desc="Loading + chunking", unit="file"):
        try:
            # TextLoader handles .txt and .md natively — no extra packages needed
            loader = TextLoader(str(fp), encoding="utf-8", autodetect_encoding=True)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = fp.name
            chunks = splitter.split_documents(docs)
            all_chunks.extend(chunks)
        except Exception as e:
            tqdm.write(f"  skip {fp.name}: {e}")

    print(f"Embedding {len(all_chunks)} chunks (this calls OpenAI) …")
    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=db_path,
    )
    print(f"Eval DB built: {db._collection.count()} chunks")
    return db

# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------

def _normalise(s: str) -> str:
    return s.lower().strip().rstrip(".")


def is_correct(predicted: str, expected: str) -> bool:
    """
    Lenient match: expected value must appear in the prediction.

    Handles two GPT rephrasing patterns:
    - Simple: "The limit is $959" → "$959" found literally.
    - Numeric qualifier: expected "60 days", predicted "60 calendar days"
      or "60 business days" — numeric token plus unit matches even when a
      qualifier is inserted between them.
    """
    import re
    pred = _normalise(predicted)
    exp  = _normalise(expected)
    if exp in pred:
        return True
    # Numeric-unit relaxation: extract number and unit from expected
    m = re.match(r"^(\d+)\s+(days?|hours?|minutes?|months?|weeks?)$", exp)
    if m:
        num, unit = m.group(1), m.group(2)
        pattern = rf"\b{re.escape(num)}\s+\w+\s+{re.escape(unit)}"
        if re.search(pattern, pred):
            return True
    return False


# ---------------------------------------------------------------------------
# LLM-only condition
# ---------------------------------------------------------------------------

def run_llm_only(qa_pairs: list[dict], llm: ChatOpenAI) -> list[dict]:
    results = []
    for qa in qa_pairs:
        t0 = time.perf_counter()
        response = llm.invoke(qa["question"])
        latency = time.perf_counter() - t0
        answer = response.content if hasattr(response, "content") else str(response)
        results.append({
            "question":  qa["question"],
            "expected":  qa["answer"],
            "predicted": answer,
            "correct":   is_correct(answer, qa["answer"]),
            "latency_s": round(latency, 3),
            "fact_key":  qa["fact_key"],
            "category":  qa["category"],
            "sources":   [],
        })
    return results


# ---------------------------------------------------------------------------
# RAG conditions (with and without reranker)
# ---------------------------------------------------------------------------

_GROUNDING_PROMPT = (
    "Answer using ONLY the information below. "
    "If the answer is not present, say \"I don't know\".\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\nAnswer:"
)


def _retrieve(query: str, db: Chroma, k: int) -> list:
    return db.similarity_search(query, k=k)


def _filter_policy(docs: list) -> list:
    """Keep only chunks whose source filename starts with 'p_' (policy docs).

    Distractor chunks (d_*) are archived policy versions with stale values.
    Noise chunks (n_*) contain no company-specific facts.
    Filtering to policy-only eliminates stale-value contamination before
    the CrossEncoder re-ranks the remaining candidates.
    """
    return [d for d in docs if d.metadata.get("source", "").startswith("p_")]


def _rerank(query: str, docs: list, model: CrossEncoder, top_k: int) -> list:
    pairs = [(query, d.page_content) for d in docs]
    scores = model.predict(pairs).tolist()
    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:top_k]]


def run_rag(
    qa_pairs: list[dict],
    db: Chroma,
    llm: ChatOpenAI,
    reranker: CrossEncoder | None,
    k_fetch: int = 3,
    k_final: int = 3,
    policy_only: bool = False,
) -> list[dict]:
    results = []
    for qa in qa_pairs:
        t0 = time.perf_counter()

        docs = _retrieve(qa["question"], db, k=k_fetch)
        if policy_only:
            docs = _filter_policy(docs)
        if reranker is not None:
            docs = _rerank(qa["question"], docs, reranker, top_k=k_final)

        context = "\n\n".join(d.page_content for d in docs[:k_final])
        prompt = _GROUNDING_PROMPT.format(context=context, question=qa["question"])
        response = llm.invoke(prompt)
        latency = time.perf_counter() - t0

        answer = response.content if hasattr(response, "content") else str(response)
        results.append({
            "question":  qa["question"],
            "expected":  qa["answer"],
            "predicted": answer,
            "correct":   is_correct(answer, qa["answer"]),
            "latency_s": round(latency, 3),
            "fact_key":  qa["fact_key"],
            "category":  qa["category"],
            "sources":   [d.metadata.get("source", "") for d in docs[:k_final]],
        })
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _accuracy(results: list[dict]) -> float:
    if not results:
        return 0.0
    return sum(r["correct"] for r in results) / len(results)


def _avg_latency(results: list[dict]) -> float:
    if not results:
        return 0.0
    return sum(r["latency_s"] for r in results) / len(results)


def _by_category(results: list[dict]) -> dict[str, dict]:
    cats: dict[str, list] = {}
    for r in results:
        cats.setdefault(r["category"], []).append(r)
    return {
        cat: {
            "accuracy": round(_accuracy(rs), 3),
            "n": len(rs),
            "correct": sum(r["correct"] for r in rs),
        }
        for cat, rs in sorted(cats.items())
    }


def print_report(conditions: list[tuple[str, list[dict]]]) -> None:
    print()
    print("=" * 70)
    print(f"{'Condition':<25} {'Accuracy':>10} {'Avg latency':>13} {'Pass/Total':>12}")
    print("-" * 70)
    for name, results in conditions:
        acc = _accuracy(results)
        lat = _avg_latency(results)
        n   = len(results)
        ok  = sum(r["correct"] for r in results)
        print(f"{name:<25} {acc:>9.1%} {lat:>12.2f}s {ok:>6}/{n:<5}")
    print("=" * 70)

    print()
    print("Accuracy by category (RAG + rerank):")
    print("-" * 50)
    _, best_results = conditions[-1]
    for cat, stats in _by_category(best_results).items():
        bar = "█" * int(stats["accuracy"] * 20)
        print(f"  {cat:<8} {stats['accuracy']:>6.1%}  {bar}  ({stats['correct']}/{stats['n']})")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="RAG ablation evaluation")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH,
                        help="Path to eval ChromaDB (default: data/eval_vectordb)")
    parser.add_argument("--index-first", action="store_true",
                        help="Index the synthetic corpus before running eval")
    parser.add_argument("--force-rebuild", action="store_true",
                        help="Delete and rebuild the eval DB even if it exists")
    parser.add_argument("--subset", type=int, default=None,
                        help="Index only N corpus files (default: all 10K)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Cap number of eval questions (smoke-test mode)")
    parser.add_argument("--skip-llm-only", action="store_true",
                        help="Skip LLM-only condition (saves API calls)")
    parser.add_argument("--skip-policy-filter", action="store_true",
                        help="Skip policy-filtered condition (saves API calls)")
    parser.add_argument("--resume", action="store_true",
                        help="Load C0/C1/C2 from existing eval_results.json and only run C3")
    parser.add_argument("--policy-corpus-only", action="store_true",
                        help="Index/use only policy docs (no distractors/noise); "
                             "use --db-path to set a separate path, e.g. data/policy_vectordb")
    parser.add_argument("--model", default="gpt-4.1-mini",
                        help="OpenAI model for generation")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set.")

    # Load eval set
    qa_pairs: list[dict] = json.loads(EVAL_QA_PATH.read_text())
    if args.limit:
        qa_pairs = qa_pairs[:args.limit]
    print(f"Loaded {len(qa_pairs)} eval questions.")

    # Shared objects
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    llm = ChatOpenAI(model=args.model, temperature=0.0, openai_api_key=api_key)

    subdirs = ("policy",) if args.policy_corpus_only else ("policy", "distractor", "noise")

    # Build or load eval DB
    if args.index_first or args.force_rebuild:
        db = build_eval_db(
            db_path=args.db_path,
            corpus_root=CORPUS_ROOT,
            embeddings=embeddings,
            subset=args.subset,
            force_rebuild=args.force_rebuild,
            subdirs=subdirs,
        )
    else:
        db = Chroma(persist_directory=args.db_path, embedding_function=embeddings)
        n = db._collection.count()
        if n == 0:
            raise SystemExit(
                f"Eval DB at '{args.db_path}' is empty. "
                "Run with --index-first to build it first."
            )
        print(f"Using eval DB with {n} chunks.")

    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    conditions: list[tuple[str, list[dict]]] = []

    if args.resume and OUT_PATH.exists():
        print(f"Resuming from {OUT_PATH} — loading C0/C1/C2 results …")
        saved = json.loads(OUT_PATH.read_text())
        for cond in saved["conditions"]:
            conditions.append((cond["name"], cond["results"]))
            print(f"  loaded '{cond['name']}': accuracy={cond['accuracy']:.1%}")
    else:
        # Condition 0: LLM-only
        if not args.skip_llm_only:
            print("\n[1/4] Running LLM-only …")
            r0 = run_llm_only(qa_pairs, llm)
            conditions.append(("LLM-only (no retrieval)", r0))
            print(f"      accuracy: {_accuracy(r0):.1%}")
        else:
            print("[1/4] LLM-only skipped.")

        # Condition 1: RAG, no rerank
        print("\n[2/4] Running RAG (no re-rank, k=3) …")
        r1 = run_rag(qa_pairs, db, llm, reranker=None, k_fetch=3, k_final=3)
        conditions.append(("RAG, no re-rank (k=3)", r1))
        print(f"      accuracy: {_accuracy(r1):.1%}")

        # Condition 2: RAG + rerank
        print("\n[3/4] Running RAG + re-rank (k=10 → top-3) …")
        r2 = run_rag(qa_pairs, db, llm, reranker=reranker, k_fetch=10, k_final=3)
        conditions.append(("RAG + re-rank (k=10→3)", r2))
        print(f"      accuracy: {_accuracy(r2):.1%}")

    # Condition 3: policy-filtered RAG + rerank
    if not args.skip_policy_filter:
        print("\n[4/4] Running RAG + policy filter + re-rank (k=30 → policy-only → top-3) …")
        r3 = run_rag(
            qa_pairs, db, llm,
            reranker=reranker,
            k_fetch=30,
            k_final=3,
            policy_only=True,
        )
        conditions.append(("RAG + filter + re-rank", r3))
        print(f"      accuracy: {_accuracy(r3):.1%}")
    else:
        print("[4/4] Policy-filtered condition skipped.")

    # Print report
    print_report(conditions)

    # Save results
    output = {
        "model": args.model,
        "n_questions": len(qa_pairs),
        "conditions": [
            {
                "name": name,
                "accuracy": round(_accuracy(results), 4),
                "avg_latency_s": round(_avg_latency(results), 3),
                "pass": sum(r["correct"] for r in results),
                "total": len(results),
                "by_category": _by_category(results),
                "results": results,
            }
            for name, results in conditions
        ],
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"Results saved → {OUT_PATH}")


if __name__ == "__main__":
    main()
