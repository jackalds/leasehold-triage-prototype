# Leasehold Enquiry Triage Prototype

A small prototype letting someone describe a leasehold question in their own words and
get a plain-English next step. Built for the Leasehold Advisory Service take-home
exercise — see `docs/PLAN.md` for the full planning pack and `docs/HARDENING.md` for
the Part 3 hardening & review notes (personal data/security, accessibility, self
code review).

## Prerequisites

- Python 3.x
- Node.js (LTS) and npm

## Running the backend

    cd backend
    python -m venv venv
    venv\Scripts\Activate.ps1   # macOS/Linux: source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Runs at http://localhost:8000 — health check at http://localhost:8000/api/health/

## Running the frontend

    cd frontend
    npm install
    npm run dev

Runs at http://localhost:5173

## Running the tests

Backend (matcher unit tests + API tests — happy path, no-match, scenario id):

    cd backend
    venv\Scripts\Activate.ps1   # macOS/Linux: source venv/bin/activate
    python manage.py test

Frontend (component tests for form submission and results rendering):

    cd frontend
    npm run test

## What's deliberately left out

- **Case-specific advice** — the tool categorises enquiries and gives a plain-English
  next step; it never asserts a legal conclusion or a statement of rights.
- **Account creation / storing real personal data** — no login, no persisted personal
  data. Would need input warnings/redaction and a DPIA before any real deployment.
- **A general-purpose chatbot** — a fixed rule-based keyword matcher (see
  `backend/api/matching.py`), not an LLM, so it's transparent and unit-testable with no
  hallucination risk.
- **Park home enquiries** — LEASE runs park home guidance as a separate subsite
  (`parkhomes.lease-advice.org`); triaging into it would mean duplicating content with
  no basis to write it, so it's left as a deliberate gap rather than a guess.
- **Anonymised "category chosen" event log (stretch, not built)** — would help LAS see
  what people are actually asking about; noted as a natural next step but out of scope
  for this slice.
- **Production-ready deployment, authentication, or infrastructure** — this is a local
  prototype only.

See `docs/PLAN.md` for the full reasoning behind these decisions.
