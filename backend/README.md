# shift. Backend — Smog Prediction API

> **Primary service (Railway)**: FastAPI + CatBoost — `/health`, `/forecast`  
> **Secondary (auth + CRUD)**: Django REST API — `/api/auth/`, `/api/aqi/`

---

## Quick Start (local — FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

# Place model artifacts first (see below), then:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger UI → http://localhost:8000/docs

---

## Model Artifacts

Place these files in `backend/artifacts/` (git-ignored — add manually):

| File | Description |
|---|---|
| `bishkek_pm25_catboost.cbm` | Trained CatBoost regressor |
| `feature_columns.json` | Ordered list of feature column names |

Without artifacts the server still starts; `/health` returns `ok: false`.

---

## FastAPI Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness + artifact check |
| `POST` | `/forecast` | PM2.5 prediction |
| `GET` | `/docs` | Swagger UI |

### `GET /health` response
```json
{ "ok": true, "model_loaded": true, "artifacts_present": true, "error": null }
```

### `POST /forecast` request / response
```json
// request
{ "features": { "hour": 14, "day_of_week": 2, "month": 6, "temperature": 28.5, "humidity": 45.0 } }

// response
{ "pm25_predicted": 47.83, "unit": "µg/m³", "model": "bishkek_pm25_catboost" }
```

---

## Railway Deployment (FastAPI)

1. Railway → **New Project** → Deploy from GitHub, set **Root Directory** = `backend`
2. `railway.toml` is already configured — no extra steps
3. **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
4. Set env var: `CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app`
5. Upload model artifacts via Railway volume or inject at build time

---

## Django Auth + AQI Endpoints (local / separate service)

```bash
cd backend
cp .env.example .env   # fill in DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

### Auth (`/api/auth/`)
| Method | URL | Description |
|---|---|---|
| POST | `/register/` | Email registration + JWT |
| POST | `/login/` | Login → access + refresh tokens |
| POST | `/logout/` | Blacklist refresh token |
| GET/PATCH | `/profile/` | View / update profile |

### AQI (`/api/aqi/`)
| Method | URL | Description |
|---|---|---|
| GET | `/stations/` | List monitoring stations |
| GET | `/summary/` | Dashboard snapshot |
| GET | `/forecast/?station=<id>` | 24 h forecast |
| GET/POST | `/alerts/` | User alerts |

---

## Docker (local full stack)

```bash
# from repo root
docker compose up --build
# → db (PostgreSQL :5432) + backend (FastAPI :8000)
```

