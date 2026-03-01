# Smog Prediction Dashboard

A Next.js + Tailwind CSS dashboard for real-time smog and air quality prediction visualization across Central Asia.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS
- **Icons**: lucide-react
- **Language**: TypeScript

## Pages

| Route | Page |
|---|---|
| `/` | Home — KPI cards, recent alerts, model accuracy |
| `/statistics` | Statistics — 7-day AQI bar chart, pollutant table |
| `/maps` | Maps — Geographic heatmap, monitored locations |
| `/about` | About the Model — Architecture, timeline, metrics |

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout with Sidebar
│   ├── page.tsx            # Home page
│   ├── statistics/page.tsx
│   ├── maps/page.tsx
│   └── about/page.tsx
├── components/
│   ├── layout/
│   │   └── Sidebar.tsx     # Navigation sidebar
│   └── ui/
│       ├── StatCard.tsx    # KPI metric card
│       └── AirQualityBadge.tsx
└── lib/
    └── utils.ts            # cn() utility
```

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Backend — Smog Prediction API (Railway)

The backend lives in `backend/` and is a **FastAPI** service that exposes:

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness + artifact check |
| `POST` | `/forecast` | PM2.5 prediction (CatBoost) |

### Local run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger UI → http://localhost:8000/docs  
`/health` returns `ok: false` until model artifacts are placed.

### Model artifacts

Place these files in `backend/artifacts/` (git-ignored — must be added manually):

- `bishkek_pm25_catboost.cbm` — trained CatBoost regressor
- `feature_columns.json` — ordered list of feature column names

### Railway deployment

1. Railway → **New Project** → Deploy from GitHub
2. Set **Root Directory** = `backend`
3. Railway auto-detects `railway.toml` — start command is already configured
4. Set env var: `CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app`
5. Upload model artifacts via Railway volume or inject at build time

Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
