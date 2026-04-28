"""
Single-company ground truth generator.

One call to generate_company_facts() produces a flat dict representing
the canonical HR policies for ONE fictitious company. All documents in the
corpus reference these same values, matching the real-world scenario where
a company has one expense limit, one VPN profile ID, etc.

generate_distractor_facts() returns a perturbed copy simulating an outdated
policy version -- used to create "old policy" documents that the re-ranker
must deprioritize in favour of the canonical version.
"""

import random
from typing import Any

from faker import Faker

fake = Faker()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _code(prefix: str, digits: int = 4) -> str:
    return f"{prefix}-{random.randint(10 ** (digits - 1), 10 ** digits - 1)}"


def _amount(lo: int, hi: int, step: int = 1) -> int:
    return random.randrange(lo, hi + 1, step)


def _days(lo: int, hi: int) -> int:
    return random.randint(lo, hi)


def _pct(lo: int, hi: int) -> int:
    return random.randint(lo, hi)


def _ext() -> str:
    return str(random.randint(1000, 9999))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_company_facts(seed: int = 42) -> dict[str, Any]:
    """
    Return the canonical ground truth for one fictional company.

    All keys are prefixed by domain (exp_, it_, ob_, ben_, vac_, coc_,
    prf_, trn_, pro_, rw_) so templates can reference them unambiguously.
    """
    random.seed(seed)
    Faker.seed(seed)

    return {
        # Company identity
        "company":              fake.company(),
        "company_short":        fake.company_suffix().upper(),
        "hq_city":              fake.city(),

        # Expense policy
        "exp_policy_id":                _code("EXP"),
        "exp_form_code":                _code("NHR"),
        "exp_limit_quarterly":          _amount(200, 1200),
        "exp_single_receipt_threshold": _amount(50, 300, 5),
        "exp_submission_days":          _days(10, 45),
        "exp_approval_code":            _code("MGR"),
        "exp_finance_email":            fake.company_email(),

        # IT security
        "it_policy_id":           _code("ITS"),
        "it_password_days":       _days(30, 120),
        "it_session_timeout_min": random.choice([15, 20, 30, 45, 60]),
        "it_vpn_id":              _code("VPN"),
        "it_incident_hours":      random.randint(1, 24),
        "it_hotline_ext":         _ext(),
        "it_mfa_grace_days":      _days(1, 7),

        # Onboarding
        "ob_checklist_id":      _code("OBD"),
        "ob_form_code":         _code("NHR"),
        "ob_equipment_form":    _code("EQP"),
        "ob_probation_days":    random.choice([30, 60, 90, 120]),
        "ob_buddy_days":        _days(1, 10),
        "ob_orientation_hours": random.randint(2, 16),
        "ob_hr_contact":        fake.name(),
        "ob_hr_ext":            _ext(),

        # Benefits
        "ben_plan_id":              _code("BEN"),
        "ben_health_deductible":    _amount(500, 3000, 50),
        "ben_hsa_limit":            _amount(1000, 3850, 50),
        "ben_dental_pct":           _pct(50, 90),
        "ben_vision_allowance":     _amount(100, 400, 10),
        "ben_pto_hours_per_month":  random.choice([6, 8, 10, 12]),
        "ben_enrollment_days":      _days(14, 60),

        # Vacation
        "vac_policy_id":      _code("VAC"),
        "vac_max_days":       random.randint(10, 30),
        "vac_carryover_days": random.randint(0, 15),
        "vac_advance_days":   _days(3, 30),
        "vac_payout_pct":     _pct(0, 100),
        "vac_blackout_month": fake.month_name(),
        "vac_form":           _code("VAC"),

        # Code of conduct
        "coc_policy_id":            _code("COC"),
        "coc_report_form":          _code("ETH"),
        "coc_hotline_ext":          _ext(),
        "coc_investigation_days":   _days(10, 60),
        "coc_escalation_days":      _days(3, 14),
        "coc_compliance_officer":   fake.name(),
        "coc_review_months":        random.choice([6, 12, 18, 24]),

        # Performance review
        "prf_policy_id":          _code("PRF"),
        "prf_review_months":      random.choice([6, 12]),
        "prf_rating_max":         random.choice([4, 5, 7, 10]),
        "prf_bonus_pct":          _pct(5, 25),
        "prf_okr_quota":          random.randint(3, 7),
        "prf_self_review_days":   _days(5, 21),
        "prf_calibration_form":   _code("CAL"),

        # Training
        "trn_course_id":      _code("TRN"),
        "trn_deadline_days":  _days(30, 90),
        "trn_cert_id":        _code("CERT"),
        "trn_passing_score":  _pct(70, 90),
        "trn_retake_days":    _days(3, 30),
        "trn_credit_hours":   random.randint(1, 8),
        "trn_lms_code":       _code("LMS"),

        # Procurement
        "pro_policy_id":       _code("PRO"),
        "pro_po_threshold":    _amount(500, 5000, 50),
        "pro_vendor_days":     _days(5, 30),
        "pro_contract_days":   _days(3, 21),
        "pro_approval_code":   _code("APR"),
        "pro_email":           fake.company_email(),
        "pro_emergency_limit": _amount(200, 1000, 50),

        # Remote work
        "rw_policy_id":           _code("RWP"),
        "rw_days_per_week":       random.randint(1, 5),
        "rw_equipment_allowance": _amount(200, 1500, 50),
        "rw_monthly_stipend":     _amount(30, 200, 5),
        "rw_vpn_id":              _code("VPN"),
        "rw_core_start":          random.choice(["8:00 AM", "9:00 AM", "10:00 AM"]),
        "rw_core_end":            random.choice(["3:00 PM", "4:00 PM", "5:00 PM"]),
        "rw_request_form":        _code("RWF"),
    }


def generate_distractor_facts(ground_truth: dict[str, Any]) -> dict[str, Any]:
    """
    Return an 'outdated policy' copy with perturbed numeric values.

    Simulates a previous year's policy from the same company -- the company
    name stays identical so the document looks plausibly related, but the
    key numeric facts differ. This tests whether the RAG pipeline surfaces
    the canonical (newer) version rather than the stale one.
    """
    outdated = dict(ground_truth)

    # Keys that represent categorical choices, not continuous policy values
    _non_perturb = {
        "it_session_timeout_min", "ob_probation_days",
        "prf_review_months", "prf_rating_max",
        "ben_pto_hours_per_month", "rw_days_per_week",
    }

    for key, val in ground_truth.items():
        if isinstance(val, int) and key not in _non_perturb:
            factor = random.uniform(0.4, 0.75)
            outdated[key] = max(1, int(val * factor))

    return outdated
