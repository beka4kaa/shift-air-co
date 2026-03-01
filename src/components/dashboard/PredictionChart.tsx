"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingDown, Activity } from "lucide-react";

// Mock 24-hour prediction data (past 12h actual + next 12h predicted)
const data = [
  { time: "00:00", actual: 161, predicted: 158 },
  { time: "02:00", actual: 155, predicted: 153 },
  { time: "04:00", actual: 149, predicted: 147 },
  { time: "06:00", actual: 158, predicted: 155 },
  { time: "08:00", actual: 163, predicted: 160 },
  { time: "10:00", actual: 156, predicted: 154 },
  { time: "12:00", actual: 148, predicted: 146 },
  { time: "14:00", actual: 142, predicted: null },
  { time: "16:00", actual: null, predicted: 135 },
  { time: "18:00", actual: null, predicted: 128 },
  { time: "20:00", actual: null, predicted: 121 },
  { time: "22:00", actual: null, predicted: 115 },
  { time: "24:00", actual: null, predicted: 108 },
];

const PURPLE = "#8b5cf6";
const VIOLET = "#6366f1";
const MUTED = "rgba(139,92,246,0.25)";

interface TooltipPayloadItem {
  name: string;
  value: number | null;
  color: string;
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-border bg-card/95 backdrop-blur-sm px-4 py-3 shadow-xl shadow-black/40 text-sm">
      <p className="text-xs text-muted-foreground mb-2 font-mono">{label}</p>
      {payload.map((entry) =>
        entry.value != null ? (
          <div key={entry.name} className="flex items-center gap-2">
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-muted-foreground capitalize">{entry.name}:</span>
            <span className="font-bold font-mono text-foreground">
              {entry.value} AQI
            </span>
          </div>
        ) : null
      )}
    </div>
  );
}

export function PredictionChart() {
  return (
    <Card className="border-border bg-card col-span-full lg:col-span-2">
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-primary" />
            <CardTitle className="text-base font-semibold">
              Smog Level Forecast
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className="text-xs bg-primary/10 text-primary border-primary/30"
            >
              Next 24 hours
            </Badge>
            <Badge
              variant="outline"
              className="text-xs bg-green-500/10 text-green-400 border-green-500/30 flex items-center gap-1"
            >
              <TrendingDown size={10} /> −19% predicted
            </Badge>
          </div>
        </div>
        <CardDescription>
          Mock model output · SmogNet v3.2.1 · Training in progress
        </CardDescription>
      </CardHeader>

      <CardContent>
        {/* Legend */}
        <div className="flex items-center gap-5 mb-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-5 rounded-full bg-violet-500" />
            Actual
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="h-2 w-5 rounded-full"
              style={{
                background:
                  "repeating-linear-gradient(90deg, #8b5cf6 0,#8b5cf6 4px,transparent 4px,transparent 8px)",
              }}
            />
            Predicted
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <span className="h-px w-5 border-t border-dashed border-red-500/60" />
            <span className="text-red-400/70">WHO limit 100</span>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={260}>
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="gradActual" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={VIOLET} stopOpacity={0.35} />
                <stop offset="100%" stopColor={VIOLET} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={PURPLE} stopOpacity={0.2} />
                <stop offset="100%" stopColor={PURPLE} stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(139,92,246,0.1)"
              vertical={false}
            />

            <XAxis
              dataKey="time"
              tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              interval={1}
            />

            <YAxis
              domain={[60, 200]}
              tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}`}
            />

            <Tooltip content={<CustomTooltip />} />

            <ReferenceLine
              y={100}
              stroke="rgba(239,68,68,0.5)"
              strokeDasharray="4 3"
              label={{
                value: "WHO",
                position: "insideTopRight",
                fill: "rgba(239,68,68,0.6)",
                fontSize: 10,
              }}
            />

            {/* Now marker */}
            <ReferenceLine
              x="14:00"
              stroke={MUTED}
              strokeDasharray="3 3"
              label={{
                value: "NOW",
                position: "insideTopLeft",
                fill: "rgba(139,92,246,0.6)",
                fontSize: 10,
              }}
            />

            <Area
              type="monotone"
              dataKey="actual"
              name="actual"
              stroke={VIOLET}
              strokeWidth={2.5}
              fill="url(#gradActual)"
              dot={false}
              connectNulls={false}
            />

            <Area
              type="monotone"
              dataKey="predicted"
              name="predicted"
              stroke={PURPLE}
              strokeWidth={2}
              strokeDasharray="6 3"
              fill="url(#gradPredicted)"
              dot={false}
              connectNulls={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
