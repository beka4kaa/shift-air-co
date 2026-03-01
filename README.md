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
