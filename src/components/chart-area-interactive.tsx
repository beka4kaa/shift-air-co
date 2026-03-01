    "use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, ReferenceLine, XAxis, YAxis } from "recharts"

import { useIsMobile } from "@/hooks/use-mobile"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group"
import { getMockSmogData, getAqiLevel } from "@/lib/smog-data"

// AQI band reference lines for visual context
const AQI_BANDS = [
  { value: 50,  label: "Good",      color: "hsl(142 71% 45%)" },
  { value: 100, label: "Moderate",  color: "hsl(48 96% 53%)"  },
  { value: 150, label: "Sensitive", color: "hsl(25 95% 53%)"  },
  { value: 200, label: "Unhealthy", color: "hsl(0 84% 60%)"   },
]

export function ChartAreaInteractive() {
  const isMobile = useIsMobile()
  const [city, setCity] = React.useState("almaty")

  // Generate fresh mock data per city on every mount
  const almatyData = React.useMemo(() => getMockSmogData(), [])
  const bishkekData = React.useMemo(() => getMockSmogData(), [])

  React.useEffect(() => {
    if (isMobile) setCity("almaty")
  }, [isMobile])

  const activeData = city === "almaty" ? almatyData : bishkekData
  const cityLabel  = city === "almaty" ? "Almaty" : "Bishkek"

  // Merge forecast points from both cities into one chart series
  const chartData = React.useMemo(() =>
    almatyData.forecast.map((pt, i) => ({
      time:    pt.time,
      almaty:  pt.predictedValue,
      bishkek: bishkekData.forecast[i].predictedValue,
    })),
    [almatyData, bishkekData]
  )

  const currentLevel = getAqiLevel(activeData.currentAQI)

  const chartConfig = {
    almaty: {
      label: "Almaty",
      color: getAqiLevel(almatyData.currentAQI).chartColor,
    },
    bishkek: {
      label: "Bishkek",
      color: getAqiLevel(bishkekData.currentAQI).chartColor,
    },
  } satisfies ChartConfig
  return (
    <Card className="@container/card">
      <CardHeader className="relative">
        <CardTitle>24 h AQI Forecast — Almaty vs Bishkek</CardTitle>
        <CardDescription>
          <span className="@[540px]/card:block hidden">
            Predicted Air Quality Index for the next 24 hours · Mock data refreshed on load
          </span>
          <span className="@[540px]/card:hidden">24 h forecast · AQI</span>
        </CardDescription>
        <div className="absolute right-4 top-4">
          <ToggleGroup
            type="single"
            value={city}
            onValueChange={(v) => v && setCity(v)}
            variant="outline"
            className="@[540px]/card:flex hidden"
          >
            <ToggleGroupItem value="almaty" className="h-8 px-2.5">
              Almaty
            </ToggleGroupItem>
            <ToggleGroupItem value="bishkek" className="h-8 px-2.5">
              Bishkek
            </ToggleGroupItem>
            <ToggleGroupItem value="both" className="h-8 px-2.5">
              Both
            </ToggleGroupItem>
          </ToggleGroup>
        </div>
      </CardHeader>

      {/* Current AQI pill */}
      <div className="px-6 pb-2 flex items-center gap-3 text-sm">
        <span className="text-muted-foreground">
          {cityLabel} now:
        </span>
        <span className={`font-semibold ${currentLevel.textClass}`}>
          AQI {activeData.currentAQI} — {currentLevel.label}
        </span>
      </div>

      <CardContent className="px-2 pt-2 sm:px-6 sm:pt-4">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[260px] w-full"
        >
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="fillAlmaty24" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="var(--color-almaty)"  stopOpacity={0.85} />
                <stop offset="95%" stopColor="var(--color-almaty)"  stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="fillBishkek24" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="var(--color-bishkek)" stopOpacity={0.7}  />
                <stop offset="95%" stopColor="var(--color-bishkek)" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid vertical={false} strokeDasharray="3 3" opacity={0.3} />

            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={28}
            />
            <YAxis
              domain={[0, 350]}
              tickLine={false}
              axisLine={false}
              tickMargin={4}
              width={32}
              tickCount={6}
            />

            {/* EPA AQI band reference lines */}
            {AQI_BANDS.map((band) => (
              <ReferenceLine
                key={band.value}
                y={band.value}
                stroke={band.color}
                strokeDasharray="4 4"
                strokeOpacity={0.5}
                label={{
                  value: band.label,
                  position: "insideTopRight",
                  fill: band.color,
                  fontSize: 10,
                  opacity: 0.8,
                }}
              />
            ))}

            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => `${value} today`}
                  indicator="dot"
                />
              }
            />

            {(city === "bishkek" || city === "both") && (
              <Area
                dataKey="bishkek"
                type="monotone"
                fill="url(#fillBishkek24)"
                stroke="var(--color-bishkek)"
                strokeWidth={2}
              />
            )}
            {(city === "almaty" || city === "both") && (
              <Area
                dataKey="almaty"
                type="monotone"
                fill="url(#fillAlmaty24)"
                stroke="var(--color-almaty)"
                strokeWidth={2}
              />
            )}
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
