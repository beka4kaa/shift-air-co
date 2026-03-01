"use client"

import * as React from "react"
import { TrendingDownIcon, TrendingUpIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { getMockSmogData, getAqiLevel } from "@/lib/smog-data"

export function SectionCards() {
  const [data, setData] = React.useState(() => getMockSmogData())

  // Regenerate on mount so every page-load gets fresh random values
  React.useEffect(() => {
    setData(getMockSmogData())
  }, [])

  const { currentAQI, pollutants } = data
  const level = getAqiLevel(currentAQI)
  const whoRatio = Math.round((pollutants.pm25 / 25) * 10) / 10
  const TrendIcon = level.trending === "up" ? TrendingUpIcon : TrendingDownIcon
  const endOfDayAQI = data.forecast[23].predictedValue
  return (
    <div className="*:data-[slot=card]:shadow-xs @xl/main:grid-cols-2 @5xl/main:grid-cols-4 grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card lg:px-6">

      {/* ── Card 1 – Current AQI ───────────────────────────── */}
      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>Current AQI</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold tabular-nums">
            {currentAQI}
          </CardTitle>
          <div className="absolute right-4 top-4">
            <Badge
              variant="outline"
              className={`flex gap-1 rounded-lg text-xs ${level.textClass} ${level.borderClass} ${level.bgClass}`}
            >
              <TrendIcon className="size-3" />
              {level.short}
            </Badge>
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className={`line-clamp-1 flex gap-2 font-medium ${level.textClass}`}>
            {level.label} <TrendIcon className="size-4" />
          </div>
          <div className="text-muted-foreground">
            {currentAQI <= 100
              ? "Air quality acceptable · low health risk"
              : currentAQI <= 200
              ? "Sensitive groups should limit outdoor time"
              : "Everyone should avoid prolonged outdoor exposure"}
          </div>
        </CardFooter>
      </Card>

      {/* ── Card 2 – PM2.5 ─────────────────────────────────── */}
      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>PM2.5 Concentration</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold tabular-nums">
            {pollutants.pm25}{" "}
            <span className="text-base font-normal text-muted-foreground">
              μg/m³
            </span>
          </CardTitle>
          <div className="absolute right-4 top-4">
            {pollutants.pm25 > 25 ? (
              <Badge
                variant="outline"
                className="flex gap-1 rounded-lg text-xs text-red-400 border-red-400/40 bg-red-400/10"
              >
                <TrendingUpIcon className="size-3" />
                {whoRatio}× WHO
              </Badge>
            ) : (
              <Badge
                variant="outline"
                className="flex gap-1 rounded-lg text-xs text-green-400 border-green-400/40 bg-green-400/10"
              >
                <TrendingDownIcon className="size-3" />
                Within WHO
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            PM10: {pollutants.pm10} μg/m³ · CO₂: {pollutants.co2} ppm
          </div>
          <div className="text-muted-foreground">Fine particulate matter · 24 h avg</div>
        </CardFooter>
      </Card>

      {/* ── Card 3 – Active Stations ───────────────────────── */}
      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>Active Stations</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold tabular-nums">
            24
          </CardTitle>
          <div className="absolute right-4 top-4">
            <Badge variant="outline" className="flex gap-1 rounded-lg text-xs text-primary border-primary/40 bg-primary/10">
              <TrendingUpIcon className="size-3" />
              +3 online
            </Badge>
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            All stations reporting normally <TrendingUpIcon className="size-4" />
          </div>
          <div className="text-muted-foreground">Across 6 cities · Central Asia</div>
        </CardFooter>
      </Card>

      {/* ── Card 4 – 24 h Forecast Accuracy ───────────────── */}
      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>24 h Forecast Accuracy</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold tabular-nums">
            94.2%
          </CardTitle>
          <div className="absolute right-4 top-4">
            <Badge variant="outline" className="flex gap-1 rounded-lg text-xs text-emerald-400 border-emerald-400/40 bg-emerald-400/10">
              <TrendingDownIcon className="size-3" />
              Model live
            </Badge>
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            AQI {endOfDayAQI < currentAQI ? "improving" : "worsening"} by end of day{" "}
            {endOfDayAQI < currentAQI
              ? <TrendingDownIcon className="size-4" />
              : <TrendingUpIcon className="size-4" />}
          </div>
          <div className="text-muted-foreground">SmogNet v3.2.1 · training in progress</div>
        </CardFooter>
      </Card>
    </div>
  )
}
