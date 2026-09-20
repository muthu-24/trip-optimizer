# Trip Optimizer

A personalized travel planning and route optimization system for Sri Lanka. Built with FastAPI (Python) and React + TypeScript (Vite).

## Features

- **User Authentication** — Register, login, JWT-secured sessions
- **Trip Preferences** — Budget, duration, travel style, season, and activity preferences
- **Smart Recommendations** — Multi-factor scoring algorithm (budget, activity match, season, style, rating)
- **Itinerary Generation** — Day-by-day plans with preference-aware activity selection and diversity enforcement
- **Route Optimization** — Haversine-based nearest-neighbor sequencing with 2-opt improvement
- **Cost Breakdown** — Accommodation, food, transport, and activities scaled per traveler
- **Save & Manage Trips** — Save itineraries, view details, delete with ownership enforcement

## Tech Stack

| Layer    | Technology                          |
| -------- | ----------------------------------- |
| Backend  | Python 3.14, FastAPI, SQLAlchemy    |
| Database | PostgreSQL + psycopg                |
| Frontend | React 19, TypeScript, Vite          |
| Auth     | JWT (python-jose), bcrypt (passlib) |

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL

### Backend Setup

```bash
cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/trip_optimizer
SECRET_KEY=<your-secret-key>
```

Seed the database and start the server:

```bash
python -c "from app.seed_destinations import seed_all; seed_all()"
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

### Environment Variables

| Variable       | Location      | Description                                    |
| -------------- | ------------- | ---------------------------------------------- |
| `DATABASE_URL` | `backend/.env` | PostgreSQL connection string                  |
| `SECRET_KEY`   | `backend/.env` | JWT signing key (defaults to dev key if unset)|
| `VITE_API_URL` | `frontend/.env`| Backend API URL (defaults to localhost:8000)  |

## Running Tests

```bash
cd backend

# Pytest suite (50 tests)
.\.venv\Scripts\pytest.exe

# Standalone verification scripts
.\.venv\Scripts\python.exe test_phase1_travelers_budget.py
.\.venv\Scripts\python.exe test_phase2_itinerary_reliability.py
.\.venv\Scripts\python.exe test_itinerary_preferences.py
.\.venv\Scripts\python.exe test_recommendations_dataset.py
.\.venv\Scripts\python.exe test_phase4_smoke_test.py

# Integration test (requires running server on port 8000)
.\.venv\Scripts\python.exe test_saved_trips.py
```

### Frontend Build

```bash
cd frontend
npm run build
```

## Project Structure

```
trip-optimizer/
├── backend/
│   ├── app/
│   │   ├── auth/          # Authentication routes & JWT security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── schemas/       # Pydantic request/response models
│   │   ├── services/      # Business logic (recommendations, routing, planning)
│   │   ├── database.py    # DB engine & session
│   │   ├── main.py        # FastAPI app entry point
│   │   └── seed_destinations.py  # Database seeder
│   ├── test_*.py          # Test suites
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # API client & typed service modules
│   │   ├── components/    # Navbar, ProtectedRoute
│   │   └── pages/         # Login, Register, Dashboard, TripPreferences, etc.
│   ├── package.json
│   └── vite.config.ts
└── .gitignore
```