# Breathe ESG Prototype

This repository contains a Django REST backend and a React frontend for ingesting SAP, utility, and corporate travel emissions data, normalizing it, and providing an analyst review dashboard.

## Backend

- Location: `breathe_esg/`
- Django app: `core`
- Primary endpoints:
  - `POST /api/ingest/sap/`
  - `POST /api/ingest/utility/`
  - `POST /api/ingest/travel/`
  - `GET /api/records/`
  - `PATCH /api/records/<id>/review/`

## Frontend

- Location: `frontend/`
- Built with Vite, React, Axios
- Proxy configured to backend at `http://localhost:8000`

## Setup

1. Backend
   - `cd breathe_esg`
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `python manage.py migrate`
   - `python manage.py runserver`

2. Frontend
   - `cd frontend`
   - `npm install`
   - `npm run dev`

3. Sample files
   - `samples/sap_fuel_sample.csv`
   - `samples/utility_electricity_sample.csv`
   - `samples/travel_sample.json`

## Notes

- Tenant scoping is implemented with a default tenant slug `demo`.
- Each ingested row is tracked to a batch and source system for source-of-truth auditability.
- Records are held in `pending` status until an analyst approves or rejects them.
# breathe_esg
