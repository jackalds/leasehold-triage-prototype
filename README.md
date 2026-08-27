# Leasehold Enquiry Triage Prototype

A small prototype letting someone describe a leasehold question in their own words and
get a plain-English next step. Built for the Leasehold Advisory Service take-home
exercise — see `docs/PLAN.md` for the full planning pack.

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

## What's deliberately left out

_(filled in as the build progresses)_
