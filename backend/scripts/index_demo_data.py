#!/usr/bin/env python3
"""
Bulk-index synthetic demo documents into the production ChromaDB.

Environment variables:
  DOCS_DIR     Path to the directory containing documents (default: /app/data/synthetic_docs)
  POLICY_ONLY  Set to "1" to index only policy docs (p_* prefix), skip distractors/noise.
               Default: 1 (recommended — mirrors the 83% accuracy evaluation setup)
"""
import os
import sys
from pathlib import Path

# Ensure backend package is importable when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.db_manager import DatabaseManager

DOCS_DIR = Path(os.getenv("DOCS_DIR", "/app/data/synthetic_docs"))
POLICY_ONLY = os.getenv("POLICY_ONLY", "1") == "1"
BATCH_SIZE = 200


def main() -> None:
    if not DOCS_DIR.exists():
        print(f"ERROR: {DOCS_DIR} not found. Is the synthetic_docs volume mounted?", flush=True)
        sys.exit(1)

    paths = [p for p in DOCS_DIR.rglob("*") if p.is_file()]

    if POLICY_ONLY:
        paths = [p for p in paths if p.stem.startswith("p_")]
        print(f"Policy-only mode: {len(paths)} policy documents", flush=True)
    else:
        print(f"Full corpus mode: {len(paths)} documents", flush=True)

    if not paths:
        print("No files found. Exiting.", flush=True)
        return

    print("Connecting to ChromaDB...", flush=True)
    dm = DatabaseManager(embedding="openai")

    total_added = 0
    paths_sorted = sorted(str(p) for p in paths)

    for i in range(0, len(paths_sorted), BATCH_SIZE):
        batch = paths_sorted[i : i + BATCH_SIZE]
        pct = min(i + BATCH_SIZE, len(paths_sorted))
        print(f"  [{pct}/{len(paths_sorted)}] indexing batch...", flush=True)
        total_added += dm.update_db(batch)

    print(f"\n✓ Done — {total_added} chunks indexed into ChromaDB.", flush=True)


if __name__ == "__main__":
    main()
