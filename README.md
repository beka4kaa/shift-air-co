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

## 🌫️ ML Pipeline — Предсказание PM2.5 в Бишкеке

CatBoost-модель для прогнозирования среднесуточной концентрации PM2.5 в Бишкеке на основе метеоданных Open-Meteo.

### Архитектура

```
smog/
├── __init__.py
├── config.py       # Location, Paths, API URLs
├── open_meteo.py   # HTTP-клиент Open-Meteo с retry
├── ingest.py       # Загрузка погоды + PM2.5 → daily parquet
├── features.py     # Feature engineering (лаги, сезонность, ветер)
└── train.py        # CatBoost TimeSeriesSplit CV + holdout
main.py             # Единый пайплайн: ingest → train
requirements.txt    # Python-зависимости
```

### Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Запустить пайплайн (загрузка данных + обучение модели)
python main.py
```

После запуска вы получите:
- `data/processed/bishkek_daily.parquet` — датасет
- `artifacts/bishkek_pm25_catboost.cbm` — обученная модель
- `artifacts/feature_columns.json` — список фичей
- `artifacts/metrics.json` — метрики CV и holdout (MAE, RMSE, R²)

### Данные

- **Источник**: [Open-Meteo Archive API](https://open-meteo.com/) (погода) + [Air Quality API](https://open-meteo.com/) (PM2.5)
- **Период**: с 2022-08-01 по текущую дату
- **Гранулярность**: почасовые → агрегация в дневные (день/ночь)

### Модель

| Параметр | Значение |
|---|---|
| Алгоритм | CatBoostRegressor |
| Loss | MAE |
| CV | TimeSeriesSplit (5 фолдов) |
| Iterations | до 6000 (early stopping 250) |
| Holdout MAE | ~3.09 |
| Holdout R² | ~0.51 |
