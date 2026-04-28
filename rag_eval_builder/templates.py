"""
Document templates for the single-company corpus.

Every template is a function (f: dict) -> str where f is the company ground
truth from fact_injector.generate_company_facts() (or a distractor version).

Template types per category:
  policy     -- official HR policy document (all facts explicit)
  howto      -- step-by-step procedural guide (references key facts)
  faq        -- FAQ page (conversational, mentions facts inline)
  dept       -- department-specific handbook section (indirect references)
  distractor -- same company, outdated numbers (tests re-ranker)

Plus noise templates (meeting notes, announcements, project updates) that
contain no policy facts and serve as haystack padding.
"""

import random
from faker import Faker
from typing import Callable

fake = Faker()

# ---------------------------------------------------------------------------
# Expense policy templates
# ---------------------------------------------------------------------------

def exp_policy(f: dict) -> str:
    return f"""{f['company']} -- Expense Reimbursement Policy
Policy ID: {f['exp_policy_id']}

PURPOSE
This policy governs reimbursement of business-related expenses for all employees
of {f['company']}.

QUARTERLY LIMIT
Employees may submit expense claims up to ${f['exp_limit_quarterly']} per calendar
quarter. Any single receipt exceeding ${f['exp_single_receipt_threshold']} requires
manager pre-approval using code {f['exp_approval_code']} before the expense is incurred.

SUBMISSION
Complete form {f['exp_form_code']} and email it with scanned receipts to
{f['exp_finance_email']} within {f['exp_submission_days']} calendar days of the expense."""


def exp_howto(f: dict) -> str:
    return f"""How to Submit an Expense Report at {f['company']}

Step 1 -- Check your quarterly balance
Your reimbursement cap is ${f['exp_limit_quarterly']} per quarter.
Items above ${f['exp_single_receipt_threshold']} need manager sign-off first (code {f['exp_approval_code']}).

Step 2 -- Fill in form {f['exp_form_code']}
Download the form from the intranet, itemise each receipt, attach scans.

Step 3 -- Submit
Email the completed form to {f['exp_finance_email']} no later than {f['exp_submission_days']} days
after the purchase date. Late submissions will not be reimbursed."""


def exp_faq(f: dict) -> str:
    return f"""Expense Reimbursement -- Frequently Asked Questions

Q: How much can I claim each quarter?
A: The quarterly cap is ${f['exp_limit_quarterly']}. This resets on the first day of each
   calendar quarter.

Q: Do I need approval before spending?
A: Yes, if a single item costs more than ${f['exp_single_receipt_threshold']}. Use approval
   code {f['exp_approval_code']} and get your manager to sign off before purchasing.

Q: What form do I use?
A: Submit form {f['exp_form_code']} to {f['exp_finance_email']}.

Q: What is the deadline?
A: {f['exp_submission_days']} calendar days from the date of the expense."""


def exp_dept(f: dict) -> str:
    dept = random.choice(["Engineering", "Sales", "Marketing", "Operations", "Design"])
    return f"""{dept} Team -- Expense Guidelines

This page summarises the key points from the company-wide expense policy
(ID {f['exp_policy_id']}) for {dept} team members.

The quarterly limit applies to everyone: ${f['exp_limit_quarterly']}. For {dept}-specific
purchases such as software licences or conference tickets, the same ${f['exp_single_receipt_threshold']}
pre-approval threshold applies. Use form {f['exp_form_code']} and submit within
{f['exp_submission_days']} days. Questions? Email {f['exp_finance_email']}."""


def exp_distractor(f: dict) -> str:
    return f"""{f['company']} -- Expense Reimbursement Policy (SUPERSEDED)
Policy ID: {f['exp_policy_id']} | Version: 2023 | Status: ARCHIVED

NOTE: This document has been superseded. Please refer to the current policy.

QUARTERLY LIMIT (2023)
The quarterly reimbursement limit was ${f['exp_limit_quarterly']} and the single-receipt
threshold was ${f['exp_single_receipt_threshold']}. These figures are no longer current.
Submission deadline was {f['exp_submission_days']} days."""


# ---------------------------------------------------------------------------
# IT security templates
# ---------------------------------------------------------------------------

def it_policy(f: dict) -> str:
    return f"""{f['company']} -- Information Security Policy
Policy ID: {f['it_policy_id']}

PASSWORD MANAGEMENT
All passwords must be rotated every {f['it_password_days']} days and meet complexity
requirements (12+ characters, mixed case, numbers, symbols).

SESSION SECURITY
Workstations lock automatically after {f['it_session_timeout_min']} minutes of inactivity.

VPN
Remote access requires VPN profile {f['it_vpn_id']}. New employees have {f['it_mfa_grace_days']} days
to complete MFA enrolment before enforcement begins.

INCIDENT REPORTING
Security incidents must be reported within {f['it_incident_hours']} hours to the Security
Hotline at extension {f['it_hotline_ext']}."""


def it_howto(f: dict) -> str:
    return f"""How to Stay Secure at {f['company']}

Passwords: rotate every {f['it_password_days']} days using the SSO portal.
Idle lock: your screen locks after {f['it_session_timeout_min']} minutes -- this is automatic.
VPN: connect via profile {f['it_vpn_id']} before accessing any internal system remotely.
MFA: enrol within {f['it_mfa_grace_days']} days of joining. After that, access is blocked until enrolment.
Incident? Call extension {f['it_hotline_ext']} within {f['it_incident_hours']} hours."""


def it_faq(f: dict) -> str:
    return f"""IT Security -- FAQ

Q: How often must I change my password?
A: Every {f['it_password_days']} days. You will receive a reminder 7 days before expiry.

Q: My computer locks too quickly -- can I change the timeout?
A: No. The {f['it_session_timeout_min']}-minute lock is a security policy and cannot be changed.

Q: Which VPN profile should I use?
A: Use profile {f['it_vpn_id']}. Contact IT if it is missing from your client.

Q: I think I've been hacked -- what do I do?
A: Call the Security Hotline at extension {f['it_hotline_ext']} immediately.
   You have {f['it_incident_hours']} hours to report from the moment of discovery."""


def it_dept(f: dict) -> str:
    return f"""Engineering Onboarding -- IT Setup Checklist

Before your first commit, make sure your environment meets {f['company']} security standards
(policy {f['it_policy_id']}):

- Connect to VPN ({f['it_vpn_id']}) before pulling from any internal repo.
- Enrol in MFA within {f['it_mfa_grace_days']} days -- after that the SSO will block you.
- Set your password rotation reminder: every {f['it_password_days']} days.
- Note the Security Hotline: ext. {f['it_hotline_ext']} (response required within {f['it_incident_hours']} hours)."""


def it_distractor(f: dict) -> str:
    return f"""{f['company']} -- Information Security Policy (SUPERSEDED 2023)
Policy ID: {f['it_policy_id']}

ARCHIVED -- Superseded by current policy.

Previous rotation cycle: {f['it_password_days']} days.
Previous session timeout: {f['it_session_timeout_min']} minutes.
Previous VPN profile: {f['it_vpn_id']}.
Previous incident response window: {f['it_incident_hours']} hours."""


# ---------------------------------------------------------------------------
# Onboarding templates
# ---------------------------------------------------------------------------

def ob_policy(f: dict) -> str:
    return f"""{f['company']} -- New Hire Onboarding Checklist
Checklist ID: {f['ob_checklist_id']}

Your HR contact is {f['ob_hr_contact']} (ext. {f['ob_hr_ext']}).

BEFORE DAY ONE
Submit form {f['ob_form_code']} at least 3 business days before your start date.
Request workstation setup using equipment form {f['ob_equipment_form']}.

FIRST WEEK
Attend the mandatory orientation ({f['ob_orientation_hours']} hours).
Your onboarding buddy is assigned within {f['ob_buddy_days']} business days.

PROBATION
Your probation period is {f['ob_probation_days']} calendar days. A formal review is
scheduled at the end of this period."""


def ob_howto(f: dict) -> str:
    return f"""Your First Week at {f['company']} -- What to Do

Day 1: Attend orientation ({f['ob_orientation_hours']} hours). Bring completed form {f['ob_form_code']}.
Days 1-{f['ob_buddy_days']}: Your onboarding buddy will be assigned. If not, contact {f['ob_hr_contact']} at ext. {f['ob_hr_ext']}.
Day 30: Check in with HR. You are in your {f['ob_probation_days']}-day probation window.

Equipment requests go through form {f['ob_equipment_form']} -- submit before you start."""


def ob_faq(f: dict) -> str:
    return f"""New Hire FAQ -- Onboarding at {f['company']}

Q: How long is probation?
A: {f['ob_probation_days']} calendar days from your start date.

Q: When will I get an onboarding buddy?
A: Within {f['ob_buddy_days']} business days. Contact {f['ob_hr_contact']} (ext. {f['ob_hr_ext']}) if it takes longer.

Q: Which form do I submit before starting?
A: Form {f['ob_form_code']}. Also use {f['ob_equipment_form']} for your equipment request.

Q: How long is the orientation session?
A: {f['ob_orientation_hours']} hours, mandatory for all new hires."""


def ob_dept(f: dict) -> str:
    dept = random.choice(["Product", "Finance", "Legal", "People Ops", "Customer Success"])
    return f"""{dept} Team -- Welcoming New Members

All new {dept} hires go through the same company-wide onboarding checklist ({f['ob_checklist_id']}).
Your {f['ob_probation_days']}-day probation starts on day one. Orientation is {f['ob_orientation_hours']} hours and mandatory.
For equipment, file form {f['ob_equipment_form']} ASAP. Questions go to {f['ob_hr_contact']}, ext. {f['ob_hr_ext']}."""


def ob_distractor(f: dict) -> str:
    return f"""{f['company']} -- Onboarding Checklist (SUPERSEDED 2023)
Checklist ID: {f['ob_checklist_id']}

ARCHIVED. The following values reflect the 2023 process:
Probation: {f['ob_probation_days']} days | Orientation: {f['ob_orientation_hours']} hours
Buddy assigned within: {f['ob_buddy_days']} days | Form: {f['ob_form_code']}"""


# ---------------------------------------------------------------------------
# Benefits templates
# ---------------------------------------------------------------------------

def ben_policy(f: dict) -> str:
    return f"""{f['company']} -- Employee Benefits Guide
Plan ID: {f['ben_plan_id']}

HEALTH INSURANCE
Annual deductible: ${f['ben_health_deductible']}. HSA employer contribution limit: ${f['ben_hsa_limit']}.

DENTAL AND VISION
Dental covers {f['ben_dental_pct']}% of eligible procedures. Vision allowance: ${f['ben_vision_allowance']}/year.

PAID TIME OFF
Accrual rate: {f['ben_pto_hours_per_month']} hours per month.

ENROLMENT
New employees must enrol within {f['ben_enrollment_days']} days of their start date."""


def ben_howto(f: dict) -> str:
    return f"""Enrolling in Benefits at {f['company']}

You have {f['ben_enrollment_days']} days from your start date to enrol. After that, changes require a
qualifying life event.

Health: the annual deductible is ${f['ben_health_deductible']}. If you elect the HDHP,
you can contribute up to ${f['ben_hsa_limit']} to your HSA each year.

Dental: reimburses {f['ben_dental_pct']}% of covered procedures.
Vision: ${f['ben_vision_allowance']} annual allowance for frames, lenses, or contacts.
PTO: you start accruing {f['ben_pto_hours_per_month']} hours per month from day one."""


def ben_faq(f: dict) -> str:
    return f"""Benefits FAQ -- {f['company']}

Q: What is my health insurance deductible?
A: ${f['ben_health_deductible']} per year.

Q: How much can I put in my HSA?
A: Up to ${f['ben_hsa_limit']} annually (employer contribution limit).

Q: What percentage of dental is covered?
A: {f['ben_dental_pct']}% of eligible procedures after the deductible.

Q: Is there a vision benefit?
A: Yes -- ${f['ben_vision_allowance']} per year.

Q: How quickly do I earn PTO?
A: {f['ben_pto_hours_per_month']} hours per month, starting from month one.

Q: How long do I have to enrol?
A: {f['ben_enrollment_days']} days from your start date."""


def ben_dept(f: dict) -> str:
    return f"""Benefits Summary for New Team Members

Quick reference for plan {f['ben_plan_id']}:
Health deductible ${f['ben_health_deductible']}, HSA limit ${f['ben_hsa_limit']},
dental coverage {f['ben_dental_pct']}%, vision ${f['ben_vision_allowance']}/yr,
PTO accrual {f['ben_pto_hours_per_month']} hrs/month. Enrol within {f['ben_enrollment_days']} days."""


def ben_distractor(f: dict) -> str:
    return f"""{f['company']} -- Benefits Guide (SUPERSEDED 2023)
Plan ID: {f['ben_plan_id']}

ARCHIVED values: Deductible ${f['ben_health_deductible']}, HSA limit ${f['ben_hsa_limit']},
dental {f['ben_dental_pct']}%, vision ${f['ben_vision_allowance']}, PTO {f['ben_pto_hours_per_month']} hrs/mo."""


# ---------------------------------------------------------------------------
# Vacation templates
# ---------------------------------------------------------------------------

def vac_policy(f: dict) -> str:
    return f"""{f['company']} -- Vacation and PTO Policy
Policy ID: {f['vac_policy_id']}

ENTITLEMENT
Employees receive up to {f['vac_max_days']} paid vacation days per year.

CARRYOVER
Maximum {f['vac_carryover_days']} unused days may carry into the next calendar year.
Excess is forfeited on January 1.

REQUESTING TIME OFF
Submit form {f['vac_form']} at least {f['vac_advance_days']} days in advance.
Additional approval is required during {f['vac_blackout_month']}.

SEPARATION PAYOUT
Accrued vacation is paid out at {f['vac_payout_pct']}% of daily base rate upon separation."""


def vac_howto(f: dict) -> str:
    return f"""How to Request Vacation at {f['company']}

1. Check your balance -- you earn up to {f['vac_max_days']} days/year.
2. Fill in form {f['vac_form']} and submit at least {f['vac_advance_days']} days before you want to leave.
3. Note: requests during {f['vac_blackout_month']} need extra approval.
4. Carryover cap is {f['vac_carryover_days']} days -- use it or lose it at year end."""


def vac_faq(f: dict) -> str:
    return f"""Vacation FAQ -- {f['company']}

Q: How many vacation days do I get?
A: Up to {f['vac_max_days']} days per year.

Q: Can I roll days over?
A: Yes, up to {f['vac_carryover_days']} days. Any excess is forfeited on January 1.

Q: How far in advance do I need to request?
A: At least {f['vac_advance_days']} days. During {f['vac_blackout_month']} you need additional approval.

Q: What form do I use?
A: Form {f['vac_form']}.

Q: What happens to my unused vacation if I leave?
A: It is paid out at {f['vac_payout_pct']}% of your daily rate."""


def vac_dept(f: dict) -> str:
    return f"""Scheduling Time Off -- Team Guide

Company policy ({f['vac_policy_id']}): {f['vac_max_days']} days/yr, up to {f['vac_carryover_days']} day carryover.
Request via form {f['vac_form']} at least {f['vac_advance_days']} days ahead.
Avoid {f['vac_blackout_month']} if possible -- requests that month need extra sign-off."""


def vac_distractor(f: dict) -> str:
    return f"""{f['company']} -- Vacation Policy (SUPERSEDED 2023)
Policy ID: {f['vac_policy_id']}

ARCHIVED: {f['vac_max_days']} days/yr, {f['vac_carryover_days']} day carryover,
{f['vac_advance_days']} days notice required, {f['vac_payout_pct']}% payout on separation."""


# ---------------------------------------------------------------------------
# Code of conduct templates
# ---------------------------------------------------------------------------

def coc_policy(f: dict) -> str:
    return f"""{f['company']} -- Code of Conduct
Policy ID: {f['coc_policy_id']}

REPORTING
Submit report form {f['coc_report_form']} or call the Ethics Hotline at ext. {f['coc_hotline_ext']}.
All reports are confidential. The compliance officer is {f['coc_compliance_officer']}.

INVESTIGATION
Investigations begin within {f['coc_investigation_days']} days. Escalations are processed
within {f['coc_escalation_days']} days. The code is reviewed every {f['coc_review_months']} months."""


def coc_faq(f: dict) -> str:
    return f"""Code of Conduct FAQ -- {f['company']}

Q: How do I report a violation?
A: Use form {f['coc_report_form']} or call ext. {f['coc_hotline_ext']}.

Q: Who leads investigations?
A: {f['coc_compliance_officer']}, who initiates within {f['coc_investigation_days']} days.

Q: How often is the code reviewed?
A: Every {f['coc_review_months']} months."""


def coc_howto(f: dict) -> str:
    return f"""Reporting an Ethics Concern at {f['company']}

Option A: Complete form {f['coc_report_form']} online (anonymous submission available).
Option B: Call the Ethics Hotline, ext. {f['coc_hotline_ext']}.

{f['coc_compliance_officer']} will open an investigation within {f['coc_investigation_days']} days.
Escalations are resolved within {f['coc_escalation_days']} days."""


def coc_dept(f: dict) -> str:
    return f"""Manager Toolkit -- Ethics & Conduct

If a team member raises a concern, direct them to form {f['coc_report_form']} or ext. {f['coc_hotline_ext']}.
Do not attempt to investigate yourself -- all matters go to {f['coc_compliance_officer']}.
Investigations begin within {f['coc_investigation_days']} days (policy {f['coc_policy_id']})."""


def coc_distractor(f: dict) -> str:
    return f"""{f['company']} -- Code of Conduct (SUPERSEDED 2023)
Policy ID: {f['coc_policy_id']}

ARCHIVED: Hotline ext. {f['coc_hotline_ext']}, report form {f['coc_report_form']},
investigation within {f['coc_investigation_days']} days, review every {f['coc_review_months']} months."""


# ---------------------------------------------------------------------------
# Performance review templates
# ---------------------------------------------------------------------------

def prf_policy(f: dict) -> str:
    return f"""{f['company']} -- Performance Review Process
Policy ID: {f['prf_policy_id']}

Reviews are conducted every {f['prf_review_months']} months on a {f['prf_rating_max']}-point scale.
Employees maintain {f['prf_okr_quota']} active OKRs and complete self-review via form
{f['prf_calibration_form']} at least {f['prf_self_review_days']} days before the review date.
High performers are eligible for a bonus of up to {f['prf_bonus_pct']}% of base salary."""


def prf_howto(f: dict) -> str:
    return f"""Performance Review Prep Guide -- {f['company']}

1. Update your {f['prf_okr_quota']} OKRs in the HR system.
2. Complete self-review (form {f['prf_calibration_form']}) {f['prf_self_review_days']} days before your review.
3. Ratings are on a 1-{f['prf_rating_max']} scale; reviews happen every {f['prf_review_months']} months.
4. Bonus eligibility: up to {f['prf_bonus_pct']}% of annual base for top ratings."""


def prf_faq(f: dict) -> str:
    return f"""Performance Review FAQ

Q: How often are reviews?
A: Every {f['prf_review_months']} months.

Q: What is the rating scale?
A: 1 to {f['prf_rating_max']}.

Q: What bonus can I earn?
A: Up to {f['prf_bonus_pct']}% of base salary.

Q: How many OKRs am I expected to have?
A: {f['prf_okr_quota']} active OKRs per cycle.

Q: When is the self-review due?
A: {f['prf_self_review_days']} days before the formal review, using form {f['prf_calibration_form']}."""


def prf_dept(f: dict) -> str:
    return f"""Quarterly Review Checklist -- Team Leads

Remind your reports: {f['prf_okr_quota']} OKRs due, self-review form {f['prf_calibration_form']}
must be in {f['prf_self_review_days']} days early. Reviews every {f['prf_review_months']} months,
{f['prf_rating_max']}-point scale, bonus up to {f['prf_bonus_pct']}% (policy {f['prf_policy_id']})."""


def prf_distractor(f: dict) -> str:
    return f"""{f['company']} -- Performance Review (SUPERSEDED 2023)
Policy ID: {f['prf_policy_id']}

ARCHIVED: {f['prf_review_months']}-month cycle, {f['prf_rating_max']}-pt scale,
{f['prf_bonus_pct']}% bonus target, {f['prf_okr_quota']} OKRs, {f['prf_self_review_days']} days self-review lead."""


# ---------------------------------------------------------------------------
# Training templates
# ---------------------------------------------------------------------------

def trn_policy(f: dict) -> str:
    return f"""{f['company']} -- Required Training Program
Course ID: {f['trn_course_id']}

All employees must complete course {f['trn_course_id']} within {f['trn_deadline_days']} days.
A passing score of {f['trn_passing_score']}% or higher is required. If you fail, wait
{f['trn_retake_days']} days before retaking. Completion awards {f['trn_credit_hours']} credit hours
and certification {f['trn_cert_id']}. Access via LMS code {f['trn_lms_code']}."""


def trn_howto(f: dict) -> str:
    return f"""Completing Your Required Training at {f['company']}

1. Log in to the LMS using code {f['trn_lms_code']}.
2. Find and start course {f['trn_course_id']}. You have {f['trn_deadline_days']} days to finish.
3. Score at least {f['trn_passing_score']}% on the final exam.
4. If you don't pass, wait {f['trn_retake_days']} days and retry.
5. On completion you receive {f['trn_credit_hours']} CPD hours and cert {f['trn_cert_id']}."""


def trn_faq(f: dict) -> str:
    return f"""Required Training FAQ

Q: What is the deadline for the mandatory course?
A: {f['trn_deadline_days']} days from enrolment (course {f['trn_course_id']}).

Q: What score do I need to pass?
A: {f['trn_passing_score']}%.

Q: What if I fail?
A: Wait {f['trn_retake_days']} days, then retake.

Q: What do I get for completing the course?
A: Certification {f['trn_cert_id']} and {f['trn_credit_hours']} CPD credit hours.

Q: How do I access the course?
A: LMS code {f['trn_lms_code']}."""


def trn_dept(f: dict) -> str:
    return f"""Mandatory Training -- Reminder for New Joiners

Please complete course {f['trn_course_id']} within {f['trn_deadline_days']} days.
Pass mark is {f['trn_passing_score']}%; failed attempts require a {f['trn_retake_days']}-day wait.
LMS access: code {f['trn_lms_code']}. Completion yields cert {f['trn_cert_id']}."""


def trn_distractor(f: dict) -> str:
    return f"""{f['company']} -- Training Program (SUPERSEDED 2023)
Course ID: {f['trn_course_id']}

ARCHIVED: Deadline {f['trn_deadline_days']} days, pass score {f['trn_passing_score']}%,
retake wait {f['trn_retake_days']} days, {f['trn_credit_hours']} credits, LMS {f['trn_lms_code']}."""


# ---------------------------------------------------------------------------
# Procurement templates
# ---------------------------------------------------------------------------

def pro_policy(f: dict) -> str:
    return f"""{f['company']} -- Procurement Policy
Policy ID: {f['pro_policy_id']}

PURCHASE ORDERS
All purchases over ${f['pro_po_threshold']} require a PO with approval code {f['pro_approval_code']}.
Emergency purchases below ${f['pro_emergency_limit']} may proceed without a PO.

VENDOR APPROVAL
New vendors take up to {f['pro_vendor_days']} business days to approve.
Contact {f['pro_email']} to start the process.

CONTRACT REVIEW
Legal review takes {f['pro_contract_days']} business days for contracts over ${f['pro_po_threshold']}."""


def pro_howto(f: dict) -> str:
    return f"""How to Raise a Purchase Order at {f['company']}

1. Is the spend above ${f['pro_po_threshold']}? If yes, you need a formal PO.
2. Get approval code {f['pro_approval_code']} from your manager.
3. New vendor? Email {f['pro_email']} -- approval takes {f['pro_vendor_days']} days.
4. Contract involved? Allow {f['pro_contract_days']} days for legal review.
5. Emergencies under ${f['pro_emergency_limit']} can skip the PO -- post-purchase review applies."""


def pro_faq(f: dict) -> str:
    return f"""Procurement FAQ

Q: When do I need a purchase order?
A: Any spend over ${f['pro_po_threshold']}.

Q: What approval code do I need?
A: {f['pro_approval_code']}.

Q: How long does vendor approval take?
A: Up to {f['pro_vendor_days']} business days.

Q: What about contract review?
A: {f['pro_contract_days']} business days. Email {f['pro_email']}.

Q: What is the emergency purchase limit (no PO needed)?
A: ${f['pro_emergency_limit']}."""


def pro_dept(f: dict) -> str:
    return f"""Buying Things for Your Team -- Quick Reference

PO required above ${f['pro_po_threshold']} (use code {f['pro_approval_code']}).
Emergency spend cap (no PO): ${f['pro_emergency_limit']}.
New vendor? Contact {f['pro_email']} -- {f['pro_vendor_days']} days to approve (policy {f['pro_policy_id']})."""


def pro_distractor(f: dict) -> str:
    return f"""{f['company']} -- Procurement Policy (SUPERSEDED 2023)
Policy ID: {f['pro_policy_id']}

ARCHIVED: PO threshold ${f['pro_po_threshold']}, vendor approval {f['pro_vendor_days']} days,
contract review {f['pro_contract_days']} days, emergency limit ${f['pro_emergency_limit']}."""


# ---------------------------------------------------------------------------
# Remote work templates
# ---------------------------------------------------------------------------

def rw_policy(f: dict) -> str:
    return f"""{f['company']} -- Remote Work Policy
Policy ID: {f['rw_policy_id']}

SCHEDULE
Employees may work remotely up to {f['rw_days_per_week']} days per week.
Core hours: {f['rw_core_start']} to {f['rw_core_end']} local time.

EQUIPMENT AND STIPEND
One-time equipment allowance: ${f['rw_equipment_allowance']}.
Monthly internet stipend: ${f['rw_monthly_stipend']}.

VPN AND REQUEST
All remote sessions use VPN {f['rw_vpn_id']}. Submit form {f['rw_request_form']} to request
a remote arrangement."""


def rw_howto(f: dict) -> str:
    return f"""Setting Up Remote Work at {f['company']}

1. Submit form {f['rw_request_form']} for manager approval (up to {f['rw_days_per_week']} days/wk).
2. Claim your ${f['rw_equipment_allowance']} equipment allowance through Procurement.
3. Your monthly stipend of ${f['rw_monthly_stipend']} is paid with your salary.
4. Connect via VPN {f['rw_vpn_id']} before accessing any internal system.
5. Be available during core hours: {f['rw_core_start']} -- {f['rw_core_end']}."""


def rw_faq(f: dict) -> str:
    return f"""Remote Work FAQ

Q: How many days can I work from home?
A: Up to {f['rw_days_per_week']} days per week.

Q: What equipment budget do I get?
A: A one-time allowance of ${f['rw_equipment_allowance']}.

Q: Is there an internet stipend?
A: Yes -- ${f['rw_monthly_stipend']} per month.

Q: Which VPN profile should I use?
A: Profile {f['rw_vpn_id']}.

Q: What are the required working hours?
A: Core hours are {f['rw_core_start']} to {f['rw_core_end']}.

Q: How do I request remote work?
A: Submit form {f['rw_request_form']}."""


def rw_dept(f: dict) -> str:
    return f"""Flexible Working -- Team Information

Remote up to {f['rw_days_per_week']} days/wk per policy {f['rw_policy_id']}.
Equipment: ${f['rw_equipment_allowance']} one-time. Stipend: ${f['rw_monthly_stipend']}/mo.
VPN: {f['rw_vpn_id']}. Core hours: {f['rw_core_start']}-{f['rw_core_end']}. Form: {f['rw_request_form']}."""


def rw_distractor(f: dict) -> str:
    return f"""{f['company']} -- Remote Work Policy (SUPERSEDED 2023)
Policy ID: {f['rw_policy_id']}

ARCHIVED: {f['rw_days_per_week']} days/wk, equipment ${f['rw_equipment_allowance']},
stipend ${f['rw_monthly_stipend']}/mo, VPN {f['rw_vpn_id']}, form {f['rw_request_form']}."""


# ---------------------------------------------------------------------------
# Noise templates (no policy facts -- haystack padding)
# ---------------------------------------------------------------------------

def noise_meeting(f: dict) -> str:
    date = fake.date_this_year().strftime("%B %d, %Y")
    attendees = ", ".join(fake.name() for _ in range(random.randint(3, 7)))
    items = "\n".join(f"- {fake.bs()}" for _ in range(random.randint(3, 6)))
    return f"""{f['company']} -- Team Meeting Notes
Date: {date}
Attendees: {attendees}

AGENDA
{items}

NEXT STEPS
Follow up by {fake.date_between(start_date='today', end_date='+14d').strftime('%B %d')}."""


def noise_announcement(f: dict) -> str:
    name = fake.name()
    role = fake.job()
    dept = random.choice(["Engineering", "Sales", "Product", "Finance", "Design"])
    return f"""Company Announcement -- {f['company']}

We are thrilled to welcome {name} to the {dept} team as {role}.
{name} brings {random.randint(3, 20)} years of experience and joins us from {fake.company()}.
Please join us in welcoming {name.split()[0]} -- their first day is {fake.date_between(start_date='today', end_date='+30d').strftime('%B %d')}."""


def noise_project(f: dict) -> str:
    project = fake.catch_phrase()
    status = random.choice(["on track", "at risk", "ahead of schedule", "in review"])
    items = "\n".join(f"- {fake.bs()}: {random.choice(['Done', 'In Progress', 'Blocked', 'Not Started'])}"
                      for _ in range(random.randint(4, 8)))
    return f"""{f['company']} -- Project Status Update

Project: {project}
Status: {status.upper()}
Owner: {fake.name()}
Updated: {fake.date_this_month().strftime('%B %d, %Y')}

WORK ITEMS
{items}

NEXT MILESTONE: {fake.date_between(start_date='today', end_date='+60d').strftime('%B %d')}"""


def noise_office(f: dict) -> str:
    event = random.choice([
        "office closure", "fire drill", "maintenance window",
        "all-hands meeting", "team offsite", "visiting speakers"
    ])
    return f"""Office Notice -- {f['company']} ({f['hq_city']} office)

Please be aware of the upcoming {event} on {fake.date_between(start_date='today', end_date='+30d').strftime('%A, %B %d')}.

{fake.paragraph(nb_sentences=3)}

Questions? Contact {fake.name()} at {fake.company_email()}."""


# ---------------------------------------------------------------------------
# Template registry
# ---------------------------------------------------------------------------

# (template_fn, doc_type, category)
POLICY_TEMPLATES: list[tuple[Callable, str, str]] = [
    (exp_policy,  "policy",     "expense"),
    (exp_howto,   "howto",      "expense"),
    (exp_faq,     "faq",        "expense"),
    (exp_dept,    "dept",       "expense"),
    (it_policy,   "policy",     "it_security"),
    (it_howto,    "howto",      "it_security"),
    (it_faq,      "faq",        "it_security"),
    (it_dept,     "dept",       "it_security"),
    (ob_policy,   "policy",     "onboarding"),
    (ob_howto,    "howto",      "onboarding"),
    (ob_faq,      "faq",        "onboarding"),
    (ob_dept,     "dept",       "onboarding"),
    (ben_policy,  "policy",     "benefits"),
    (ben_howto,   "howto",      "benefits"),
    (ben_faq,     "faq",        "benefits"),
    (ben_dept,    "dept",       "benefits"),
    (vac_policy,  "policy",     "vacation"),
    (vac_howto,   "howto",      "vacation"),
    (vac_faq,     "faq",        "vacation"),
    (vac_dept,    "dept",       "vacation"),
    (coc_policy,  "policy",     "conduct"),
    (coc_howto,   "howto",      "conduct"),
    (coc_faq,     "faq",        "conduct"),
    (coc_dept,    "dept",       "conduct"),
    (prf_policy,  "policy",     "performance"),
    (prf_howto,   "howto",      "performance"),
    (prf_faq,     "faq",        "performance"),
    (prf_dept,    "dept",       "performance"),
    (trn_policy,  "policy",     "training"),
    (trn_howto,   "howto",      "training"),
    (trn_faq,     "faq",        "training"),
    (trn_dept,    "dept",       "training"),
    (pro_policy,  "policy",     "procurement"),
    (pro_howto,   "howto",      "procurement"),
    (pro_faq,     "faq",        "procurement"),
    (pro_dept,    "dept",       "procurement"),
    (rw_policy,   "policy",     "remote_work"),
    (rw_howto,    "howto",      "remote_work"),
    (rw_faq,      "faq",        "remote_work"),
    (rw_dept,     "dept",       "remote_work"),
]

DISTRACTOR_TEMPLATES: list[tuple[Callable, str, str]] = [
    (exp_distractor, "distractor", "expense"),
    (it_distractor,  "distractor", "it_security"),
    (ob_distractor,  "distractor", "onboarding"),
    (ben_distractor, "distractor", "benefits"),
    (vac_distractor, "distractor", "vacation"),
    (coc_distractor, "distractor", "conduct"),
    (prf_distractor, "distractor", "performance"),
    (trn_distractor, "distractor", "training"),
    (pro_distractor, "distractor", "procurement"),
    (rw_distractor,  "distractor", "remote_work"),
]

NOISE_TEMPLATES: list[tuple[Callable, str, str]] = [
    (noise_meeting,      "noise", "general"),
    (noise_announcement, "noise", "general"),
    (noise_project,      "noise", "general"),
    (noise_office,       "noise", "general"),
]
