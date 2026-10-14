# Workout App

A personalized fitness app that uses computer-vision body analysis to build a 12-week
roadmap, budget grocery list, and workout plan — and tracks progress with weekly re-checks.

## Stack

- **Backend** — Python 3.11, FastAPI, SQLAlchemy 2, Alembic, MediaPipe, OpenCV
- **Frontend** — Vite, React 18, TypeScript, Tailwind, React Query, Recharts
- **Data** — PostgreSQL (relational), Cloudinary (photos) with local-disk fallback for dev

## Folder layout

```
workout_app/
├── backend/   # FastAPI app
└── frontend/  # Vite + React
```

## Quick start

### 1. PostgreSQL

```bash
# Create a local database
createdb workout_app
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # fill in DATABASE_URL + Cloudinary creds (optional)
alembic upgrade head          # create tables
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

> **Cloudinary:** optional for development. If `CLOUDINARY_*` env vars are blank, photos are
> written to `backend/uploads/` and served at `/uploads/...`. Set them in `.env` for production.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

Vite is configured to proxy `/api/*` to `http://localhost:8000`; the frontend talks to
`http://localhost:8000` by default (set `VITE_API_URL` to override).

## Flow

1. **Onboarding** (`/onboarding`) — height, weight, age, gender, target weight, budget, city,
   vegetarian, gym access, schedule.
2. **Photo upload** (`/upload`) — 3 photos (front, side, back). Triggers MediaPipe Pose →
   body fat %, muscle mass, posture score, weak muscles, fat distribution.
3. **Plan** (`/plan`) — 12-week roadmap (calories + macros), budget grocery list (₹3000/mo,
   veg-aware), workout plan (gym or home, with YouTube demos).
4. **Weekly** (`/weekly`) — re-upload 3 photos. AI compares to last week, adjusts the plan,
   updates the predicted target date.

## API (auto-documented at `/docs`)

| Method | Path                                  | Purpose                                    |
|--------|---------------------------------------|--------------------------------------------|
| POST   | `/users`                              | Create profile                             |
| GET    | `/users/{id}`                         | Fetch profile                              |
| POST   | `/photos/upload?user_id=…`            | Upload 3 photos, run AI analysis           |
| GET    | `/analysis/{user_id}/latest`          | Latest analysis                            |
| GET    | `/analysis/{user_id}/history`         | All analyses (for charts)                  |
| POST   | `/plan/{user_id}/generate`            | Generate 12-week plan                      |
| GET    | `/plan/{user_id}`                     | Fetch plan                                 |
| POST   | `/reanalyze/{user_id}`                | Weekly re-analyse + plan adjustment        |

## Notes & limitations

- All body composition numbers are **estimates**, not medical measurements. They are most
  useful for tracking **relative** change week over week, not absolute values.
- Grocery data uses approximate India retail prices (₹). Edit `backend/app/data/foods_inr.json`
  to localise.
- Live wearable / heart-rate / step tracking is out of scope for this MVP.

## Deploy

### Docker (recommended)

```bash
cp backend/.env.example .env   # fill in DATABASE_URL + Cloudinary (optional)
docker compose up --build
```

- Frontend (nginx → SPA) → http://localhost:8080
- Backend API (FastAPI) → http://localhost:8000 (also reachable at `/api/*` via the nginx proxy)
- Postgres → `localhost:5432`

`docker compose` automatically runs `alembic upgrade head` on backend start, mounts a
named volume for uploads, and waits for Postgres' healthcheck before booting the API.

### Deploying elsewhere (Render / Fly / Railway)

The backend ships a `Procfile` that runs migrations then uvicorn:

```
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set the env vars from `backend/.env.example` in the platform's UI. The frontend is a
plain Vite SPA — `npm ci && npm run build` produces `frontend/dist/`, which can be served
by any static host (Netlify, Vercel, S3+CloudFront). Point `VITE_API_URL` at the backend
URL at build time.

### Healthchecks

- `GET /health` — liveness, always 200 once the process is up.
- `GET /health/db` — readiness, 200 once Postgres is reachable, 503 otherwise. Use this
  as a readiness probe in your orchestrator (k8s `readinessProbe`, ECS health check, etc.).
