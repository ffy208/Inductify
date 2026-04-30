# rag_eval_builder

Synthetic document corpus generator for RAG ablation studies.

Produces a realistic enterprise onboarding corpus — 10K+ documents from one
fictional company — and a paired Q&A evaluation set. Designed to measure
whether accuracy improvements come from the RAG pipeline itself rather than
from LLM parametric memory.

---

## Why This Exists

The core problem with using public HR documents for RAG evaluation is that
modern LLMs may have memorised them during training. A model that scores
high without any retrieved context proves nothing about retrieval quality.

This tool solves the problem by injecting **synthetic unique facts** —
specific numbers and codes randomly generated per company that cannot
exist in any training corpus. Questions in the eval set target these facts
exclusively, so LLM-only performance is structurally bounded.

---

## Corpus Structure

All documents belong to **one fictional company** with **one canonical set
of policy values**. This matches the real enterprise scenario: one expense
limit, one VPN profile ID, one probation period.

| Type | Fraction | Description |
|------|----------|-------------|
| `policy/` | 55% | Official policies, how-to guides, FAQs, dept handbooks — all contain the correct facts |
| `distractor/` | 10% | Archived 2023 policies — same company, perturbed numbers. Tests whether re-ranking surfaces the current version |
| `noise/` | 35% | Meeting notes, announcements, project updates — no policy facts. Simulates a realistic enterprise haystack |

**10 policy domains:** expense, IT security, onboarding, benefits, vacation,
code of conduct, performance review, training, procurement, remote work.

**5 document variants per domain:** policy, howto, faq, dept, distractor.

---

## Ablation Design

Run three conditions on the same 54-question eval set:

| Condition | Setup | Expected accuracy |
|-----------|-------|-------------------|
| LLM-only | No retrieved context | ~10-20% (synthetic facts are unknown to LLM) |
| RAG, no re-rank | top-3 by cosine similarity | ~60-75% |
| RAG + re-rank | top-10 → CrossEncoder → top-3 | ~85-92% |

A gap between LLM-only and RAG conditions confirms the improvement comes
from retrieval, not parametric memory. The distractor documents create
realistic precision pressure: a weak retriever surfaces the old policy.

---

## Quick Start

```bash
# Install dependencies
pip install -r rag_eval_builder/requirements.txt

# Generate 10K documents + eval set (all formats)
python rag_eval_builder/generate_docs.py --count 10000 --seed 42

# Text/Markdown only (no fpdf2/openpyxl needed)
python rag_eval_builder/generate_docs.py --count 10000 --formats txt,md

# Preview the plan without writing any files
python rag_eval_builder/generate_docs.py --count 10000 --dry-run
```

**Output files:**

```
data/
├── ground_truth.json      # Company name + all canonical policy values
├── eval_qa.json           # 54 Q&A pairs (one per policy fact)
└── synthetic_docs/
    ├── policy/            # 5,500 docs with correct facts
    ├── distractor/        # 1,000 docs with outdated facts
    └── noise/             # 3,500 docs with no policy facts
```

---

## Modules

| File | Role |
|------|------|
| `fact_injector.py` | Generates one company's canonical ground truth; also produces a distractor (outdated) version |
| `templates.py` | 54 document templates across 10 domains and 5 variant types, plus 4 noise templates |
| `doc_writers.py` | Writes rendered text to `.txt`, `.md`, `.pdf`, or `.xlsx` |
| `qa_builder.py` | Derives 54 Q&A pairs directly from the ground truth dict |
| `generate_docs.py` | CLI orchestrator |

---

## Reproducibility

The `--seed` flag controls both the company facts and document sampling.
The same seed always produces the same corpus and the same eval set.

```bash
python rag_eval_builder/generate_docs.py --seed 42   # canonical run
python rag_eval_builder/generate_docs.py --seed 99   # different company, same structure
```

`data/ground_truth.json` records the exact values used, so the eval set
can be reconstructed from it at any time.
