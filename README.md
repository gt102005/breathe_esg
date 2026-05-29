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

### Prerequisites

- Python 3.10+ installed
- Node.js 16+ and npm installed
- Git installed (optional, if cloning the repo)

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/assignment_breatheesg.git
cd assignment_breatheesg
```

### 2. Backend setup

```bash
cd breathe_esg
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
```

To run the backend server:

```bash
python manage.py runserver
```

The backend will start at `http://127.0.0.1:8000/`.

### 3. Frontend setup

Open a new terminal window/tab and run:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on the Vite development server, usually at `http://localhost:5173/`.

### 4. Access the app

- Frontend: `http://localhost:5173/`
- Backend API: `http://127.0.0.1:8000/api/`

### 5. Sample files

Use the sample data files for ingest testing:

- `samples/sap_fuel_sample.csv`
- `samples/utility_electricity_sample.csv`
- `samples/travel_sample.json`

## Notes

- Tenant scoping is implemented with a default tenant slug `demo`.
- Each ingested row is tracked to a batch and source system for source-of-truth auditability.
- Records are held in `pending` status until an analyst approves or rejects them.
# breathe_esg
