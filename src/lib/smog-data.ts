// ---------------------------------------------------------------------------
// getMockSmogData — generates a realistic randomised AQI snapshot on every call
// ---------------------------------------------------------------------------

export interface ForecastPoint {
  time: string  // "00:00", "01:00", …
  hour: number  // 0–23
  predictedValue: number
}

export interface Pollutants {
  pm25: number   // μg/m³
  pm10: number   // μg/m³
  co2: number    // ppm
}

export interface SmogData {
  currentAQI: number
  forecast: ForecastPoint[]
  pollutants: Pollutants
}

/** Seeded-ish random in [min, max] using Math.random */
function rand(min: number, max: number): number {
  return Math.round(Math.random() * (max - min) + min)
}

/** Clamp a value between lo and hi */
function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, v))
}

/**
 * Returns a fresh mock smog dataset every time it is called.
 *
 * - `currentAQI`  — random integer 50–300
 * - `forecast`    — 24 hourly points that drift realistically around currentAQI
 * - `pollutants`  — PM2.5 / PM10 / CO2 values correlated with AQI
 */
export function getMockSmogData(): SmogData {
  const currentAQI = rand(50, 300)

  // Build a 24-hour forecast centred on currentAQI with smooth drift
  const forecast: ForecastPoint[] = []
  let value = currentAQI

  for (let h = 0; h < 24; h++) {
    // Apply a small random walk (-15…+15) clamped to realistic AQI range
    const delta = rand(-15, 15)
    value = clamp(value + delta, 30, 350)

    const hh = String(h).padStart(2, "0")
    forecast.push({
      time: `${hh}:00`,
      hour: h,
      predictedValue: value,
    })
  }

  // Pollutants scale linearly with AQI (rough real-world correlation)
  const ratio = currentAQI / 150
  const pollutants: Pollutants = {
    pm25: Math.round(ratio * 55.4 * 10) / 10,          // WHO threshold: 25 μg/m³
    pm10: Math.round(ratio * 120 * 10) / 10,            // WHO threshold: 50 μg/m³
    co2: clamp(rand(400, 400 + currentAQI * 2), 400, 1000), // 400 ppm baseline
  }

  return { currentAQI, forecast, pollutants }
}

// ---------------------------------------------------------------------------
// AQI level descriptors used by UI components for colour-coding
// ---------------------------------------------------------------------------

export interface AqiLevel {
  label: string
  /** Short label for badges */
  short: string
  textClass: string
  borderClass: string
  bgClass: string
  /** Chart stroke / fill colour (CSS hsl string) */
  chartColor: string
  trending: "up" | "down"
}

/**
 * Maps an AQI integer to EPA-band colours and labels.
 *
 * | AQI      | Category                      | Colour   |
 * |----------|-------------------------------|----------|
 * | 0–50     | Good                          | green    |
 * | 51–100   | Moderate                      | yellow   |
 * | 101–150  | Unhealthy for Sensitive Groups | orange   |
 * | 151–200  | Unhealthy                     | red      |
 * | 201–300  | Very Unhealthy                | purple   |
 * | 301+     | Hazardous                     | maroon   |
 */
export function getAqiLevel(aqi: number): AqiLevel {
  if (aqi <= 50)
    return {
      label: "Good",
      short: "Good",
      textClass: "text-green-400",
      borderClass: "border-green-400/40",
      bgClass: "bg-green-400/10",
      chartColor: "hsl(142 71% 45%)",
      trending: "down",
    }
  if (aqi <= 100)
    return {
      label: "Moderate",
      short: "Moderate",
      textClass: "text-yellow-400",
      borderClass: "border-yellow-400/40",
      bgClass: "bg-yellow-400/10",
      chartColor: "hsl(48 96% 53%)",
      trending: "up",
    }
  if (aqi <= 150)
    return {
      label: "Unhealthy for Sensitive Groups",
      short: "Sensitive",
      textClass: "text-orange-400",
      borderClass: "border-orange-400/40",
      bgClass: "bg-orange-400/10",
      chartColor: "hsl(25 95% 53%)",
      trending: "up",
    }
  if (aqi <= 200)
    return {
      label: "Unhealthy",
      short: "Unhealthy",
      textClass: "text-red-400",
      borderClass: "border-red-400/40",
      bgClass: "bg-red-400/10",
      chartColor: "hsl(0 84% 60%)",
      trending: "up",
    }
  if (aqi <= 300)
    return {
      label: "Very Unhealthy",
      short: "Very Unhealthy",
      textClass: "text-purple-400",
      borderClass: "border-purple-400/40",
      bgClass: "bg-purple-400/10",
      chartColor: "hsl(271 76% 53%)",
      trending: "up",
    }
  return {
    label: "Hazardous",
    short: "Hazardous",
    textClass: "text-rose-600",
    borderClass: "border-rose-600/40",
    bgClass: "bg-rose-600/10",
    chartColor: "hsl(347 77% 50%)",
    trending: "up",
  }
}
