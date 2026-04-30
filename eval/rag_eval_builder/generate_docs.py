"""
Generate the single-company synthetic corpus for RAG evaluation.

All documents belong to ONE fictional company sharing ONE set of canonical
policy facts. Document variety comes from topic type (policy/howto/faq/dept),
distractor versions (old policies with wrong numbers), and noise documents
(meeting notes, announcements -- no policy facts).

Usage:
    python rag_eval_builder/generate_docs.py --count 10000
    python rag_eval_builder/generate_docs.py --count 500 --formats txt,md
    python rag_eval_builder/generate_docs.py --count 100 --dry-run --seed 0
"""

import json
import random
import sys
from pathlib import Path
from typing import Optional

import typer
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))

from fact_injector import generate_company_facts, generate_distractor_facts
from templates import POLICY_TEMPLATES, DISTRACTOR_TEMPLATES, NOISE_TEMPLATES
from doc_writers import write_doc, FORMATS, DocFormat
from qa_builder import build_all_qa

app = typer.Typer(add_completion=False)

# Distribution across doc types (must sum to 1.0)
_DIST = {
    "policy":     0.55,   # canonical docs with correct facts
    "distractor": 0.10,   # old policies with wrong numbers
    "noise":      0.35,   # meeting notes, announcements, etc.
}


@app.command()
def main(
    count: int = typer.Option(10_000, "--count", "-n",
                              help="Total number of documents to generate"),
    out: Path = typer.Option(Path("data/synthetic_docs"), "--out", "-o",
                             help="Output directory for documents"),
    qa: Path = typer.Option(Path("data/eval_qa.json"), "--qa",
                            help="Output path for Q&A evaluation set"),
    gt: Path = typer.Option(Path("data/ground_truth.json"), "--gt",
                            help="Output path for company ground truth"),
    formats: Optional[str] = typer.Option(None, "--formats",
                                          help="Comma-separated subset: txt,md,pdf,xlsx"),
    seed: int = typer.Option(42, "--seed", help="Random seed (controls both facts and sampling)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print plan without writing files"),
) -> None:
    """
    Build a synthetic onboarding corpus for RAG ablation studies.

    Generates documents from ONE company with ONE canonical set of policy facts.
    Includes distractor documents (outdated policies, same company, different numbers)
    and noise documents (no policy facts) to simulate a realistic enterprise corpus.
    """
    random.seed(seed)

    # Validate formats
    active_formats: list[DocFormat] | None = None
    if formats:
        parsed = [f.strip() for f in formats.split(",")]
        bad = set(parsed) - set(FORMATS)
        if bad:
            typer.echo(f"Unknown formats: {bad}. Choose from: {set(FORMATS)}", err=True)
            raise typer.Exit(1)
        active_formats = parsed  # type: ignore[assignment]

    # Compute counts
    n_policy = int(count * _DIST["policy"])
    n_distractor = int(count * _DIST["distractor"])
    n_noise = count - n_policy - n_distractor

    typer.echo(f"Company seed   : {seed}")
    typer.echo(f"Total docs     : {count:,}")
    typer.echo(f"  policy/howto : {n_policy:,}  ({_DIST['policy']*100:.0f}%)")
    typer.echo(f"  distractor   : {n_distractor:,}  ({_DIST['distractor']*100:.0f}%)")
    typer.echo(f"  noise        : {n_noise:,}  ({_DIST['noise']*100:.0f}%)")
    typer.echo(f"Formats        : {active_formats or FORMATS}")

    if dry_run:
        typer.echo("[dry-run] No files written.")
        return

    # Generate ground truth (one company)
    ground_truth = generate_company_facts(seed=seed)
    distractor_facts = generate_distractor_facts(ground_truth)

    out.mkdir(parents=True, exist_ok=True)

    format_counts: dict[str, int] = {f: 0 for f in FORMATS}
    failed = 0

    def _write(doc_id: str, text: str, subdir: str, fmt: DocFormat | None) -> None:
        nonlocal failed
        # write_doc creates output_dir/{category}/ automatically
        meta = {"company": ground_truth["company"], "category": subdir}
        try:
            path = write_doc(out, doc_id, text, meta, fmt=fmt)
            format_counts[path.suffix.lstrip(".")] += 1
        except ImportError as e:
            if failed == 0:
                typer.echo(f"\nWarning: {e}\nUse --formats txt,md to avoid this.", err=True)
            failed += 1

    def _fmt() -> DocFormat | None:
        if active_formats:
            return random.choice(active_formats)  # type: ignore[return-value]
        return None

    total_bar = tqdm(total=count, desc="Writing docs", unit="doc")

    # 1 — Policy / howto / faq / dept documents
    for i in range(n_policy):
        fn, doc_type, category = random.choice(POLICY_TEMPLATES)
        text = fn(ground_truth)
        _write(f"p_{i:06d}", text, "policy", _fmt())
        total_bar.update(1)

    # 2 — Distractor documents (outdated policies)
    for i in range(n_distractor):
        fn, doc_type, category = random.choice(DISTRACTOR_TEMPLATES)
        text = fn(distractor_facts)
        _write(f"d_{i:06d}", text, "distractor", _fmt())
        total_bar.update(1)

    # 3 — Noise documents (no policy facts)
    for i in range(n_noise):
        fn, doc_type, category = random.choice(NOISE_TEMPLATES)
        text = fn(ground_truth)   # only uses company name + hq_city, not policy values
        _write(f"n_{i:06d}", text, "noise", _fmt())
        total_bar.update(1)

    total_bar.close()

    # Save ground truth
    gt.parent.mkdir(parents=True, exist_ok=True)
    with open(gt, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)

    # Build and save Q&A evaluation set
    qa_pairs = build_all_qa(ground_truth)
    qa.parent.mkdir(parents=True, exist_ok=True)
    with open(qa, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)

    # Summary
    total_written = count - failed
    typer.echo("\n-- Summary ----------------------------------------")
    typer.echo(f"Company          : {ground_truth['company']}")
    typer.echo(f"Documents written: {total_written:,}")
    if failed:
        typer.echo(f"Skipped (dep err): {failed:,}")
    for fmt, n in format_counts.items():
        if n:
            typer.echo(f"  .{fmt:<6}         : {n:,}")
    typer.echo(f"Q&A pairs        : {len(qa_pairs)}")
    typer.echo(f"Ground truth  -> : {gt}")
    typer.echo(f"Eval Q&A      -> : {qa}")
    typer.echo(f"Corpus        -> : {out}/")


if __name__ == "__main__":
    app()
