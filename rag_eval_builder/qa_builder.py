"""
Build Q&A evaluation pairs from the single-company ground truth.

All questions reference the canonical facts (not per-document facts), so
each question has exactly one correct answer regardless of which document
a RAG system retrieves. Distractor and noise documents do not generate Q&A
pairs -- they only exist to make retrieval harder.
"""

from typing import Any


# ---------------------------------------------------------------------------
# Q&A spec: (question_template, fact_key, unit_fn)
# unit_fn formats the raw value into a human-readable answer string.
# ---------------------------------------------------------------------------

def _dollar(v: Any) -> str:   return f"${v}"
def _days(v: Any) -> str:     return f"{v} days"
def _hours(v: Any) -> str:    return f"{v} hours"
def _mins(v: Any) -> str:     return f"{v} minutes"
def _pct(v: Any) -> str:      return f"{v}%"
def _months(v: Any) -> str:   return f"{v} months"
def _per_wk(v: Any) -> str:   return f"{v} days per week"
def _per_mo(v: Any) -> str:   return f"{v} hours per month"
def _plain(v: Any) -> str:    return str(v)


_QA_SPECS: list[tuple[str, str, Any]] = [
    # Expense
    ("What is the quarterly expense reimbursement limit at {company}?",
     "exp_limit_quarterly", _dollar),
    ("What form must employees use to submit expenses at {company}?",
     "exp_form_code", _plain),
    ("Within how many days must an expense report be submitted at {company}?",
     "exp_submission_days", _days),
    ("What is the single-receipt pre-approval threshold at {company}?",
     "exp_single_receipt_threshold", _dollar),
    ("What is the expense policy ID at {company}?",
     "exp_policy_id", _plain),

    # IT security
    ("How often must passwords be rotated at {company}?",
     "it_password_days", _days),
    ("What is the workstation session timeout at {company}?",
     "it_session_timeout_min", _mins),
    ("What VPN profile ID is required at {company}?",
     "it_vpn_id", _plain),
    ("Within how many hours must security incidents be reported at {company}?",
     "it_incident_hours", _hours),
    ("What is the Security Hotline extension at {company}?",
     "it_hotline_ext", _plain),
    ("How many days do new employees have to enrol in MFA at {company}?",
     "it_mfa_grace_days", _days),

    # Onboarding
    ("What is the probation period for new hires at {company}?",
     "ob_probation_days", _days),
    ("What form must new hires submit before starting at {company}?",
     "ob_form_code", _plain),
    ("Within how many days will a new hire's buddy be assigned at {company}?",
     "ob_buddy_days", _days),
    ("How many hours is the mandatory orientation at {company}?",
     "ob_orientation_hours", _hours),
    ("What is the onboarding checklist ID at {company}?",
     "ob_checklist_id", _plain),

    # Benefits
    ("What is the annual health insurance deductible at {company}?",
     "ben_health_deductible", _dollar),
    ("What is the annual HSA limit at {company}?",
     "ben_hsa_limit", _dollar),
    ("What percentage of dental procedures are covered at {company}?",
     "ben_dental_pct", _pct),
    ("What is the annual vision allowance at {company}?",
     "ben_vision_allowance", _dollar),
    ("How many PTO hours do employees accrue per month at {company}?",
     "ben_pto_hours_per_month", _per_mo),
    ("Within how many days must new employees enrol in benefits at {company}?",
     "ben_enrollment_days", _days),

    # Vacation
    ("How many paid vacation days per year do employees receive at {company}?",
     "vac_max_days", _days),
    ("How many vacation days can be carried over at {company}?",
     "vac_carryover_days", _days),
    ("How many days in advance must vacation requests be submitted at {company}?",
     "vac_advance_days", _days),
    ("At what percentage is unused vacation paid out upon separation at {company}?",
     "vac_payout_pct", _pct),
    ("What form is used to request vacation at {company}?",
     "vac_form", _plain),

    # Code of conduct
    ("What form is used to report a code of conduct violation at {company}?",
     "coc_report_form", _plain),
    ("What is the ethics hotline extension at {company}?",
     "coc_hotline_ext", _plain),
    ("Within how many days does an investigation begin at {company}?",
     "coc_investigation_days", _days),
    ("How often is the code of conduct reviewed at {company}?",
     "coc_review_months", _months),
    ("Who is the compliance officer at {company}?",
     "coc_compliance_officer", _plain),

    # Performance review
    ("How often are performance reviews held at {company}?",
     "prf_review_months", _months),
    ("What is the maximum performance rating at {company}?",
     "prf_rating_max", _plain),
    ("What is the bonus target percentage at {company}?",
     "prf_bonus_pct", _pct),
    ("How many OKRs are employees expected to maintain at {company}?",
     "prf_okr_quota", _plain),
    ("How many days before a review must the self-review be submitted at {company}?",
     "prf_self_review_days", _days),
    ("What form is used for performance calibration at {company}?",
     "prf_calibration_form", _plain),

    # Training
    ("Within how many days must the required training be completed at {company}?",
     "trn_deadline_days", _days),
    ("What certification is awarded upon completing the required training at {company}?",
     "trn_cert_id", _plain),
    ("What passing score is required for the training exam at {company}?",
     "trn_passing_score", _pct),
    ("How many days must employees wait before retaking the training exam at {company}?",
     "trn_retake_days", _days),
    ("What is the LMS access code for required training at {company}?",
     "trn_lms_code", _plain),

    # Procurement
    ("What is the purchase order threshold at {company}?",
     "pro_po_threshold", _dollar),
    ("How many days does vendor approval take at {company}?",
     "pro_vendor_days", _days),
    ("How many days does contract legal review take at {company}?",
     "pro_contract_days", _days),
    ("What approval code is required for purchase orders at {company}?",
     "pro_approval_code", _plain),
    ("What is the emergency purchase limit (no PO required) at {company}?",
     "pro_emergency_limit", _dollar),

    # Remote work
    ("How many days per week can employees work remotely at {company}?",
     "rw_days_per_week", _per_wk),
    ("What is the one-time equipment allowance for remote workers at {company}?",
     "rw_equipment_allowance", _dollar),
    ("What is the monthly remote work stipend at {company}?",
     "rw_monthly_stipend", _dollar),
    ("What VPN profile is required for remote work at {company}?",
     "rw_vpn_id", _plain),
    ("What form must be submitted to request a remote work arrangement at {company}?",
     "rw_request_form", _plain),
    ("What are the core collaboration hours at {company}?",
     "rw_core_start", _plain),
]


def build_all_qa(ground_truth: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate the full Q&A evaluation set from one company's ground truth.

    Returns a list of dicts: {question, answer, fact_key, category}.
    These are independent of any specific document -- the 'correct' answer
    is always the canonical ground truth value.
    """
    company = ground_truth["company"]
    pairs = []
    for question_tpl, fact_key, fmt_fn in _QA_SPECS:
        if fact_key not in ground_truth:
            continue
        category = fact_key.split("_")[0]  # exp, it, ob, ...
        pairs.append({
            "question": question_tpl.format(company=company),
            "answer":   fmt_fn(ground_truth[fact_key]),
            "fact_key": fact_key,
            "category": category,
        })
    return pairs
