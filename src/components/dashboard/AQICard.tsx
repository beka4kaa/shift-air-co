import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Wind } from "lucide-react";

interface AQICardProps {
  aqi: number;
}

function getAQILevel(aqi: number): {
  label: string;
  color: string;
  glow: string;
  bg: string;
  badgeClass: string;
} {
  if (aqi <= 50)
    return {
      label: "Good",
      color: "#22c55e",
      glow: "rgba(34,197,94,0.35)",
      bg: "rgba(34,197,94,0.08)",
      badgeClass: "bg-green-500/20 text-green-400 border-green-500/40",
    };
  if (aqi <= 100)
    return {
      label: "Moderate",
      color: "#eab308",
      glow: "rgba(234,179,8,0.35)",
      bg: "rgba(234,179,8,0.08)",
      badgeClass: "bg-yellow-500/20 text-yellow-400 border-yellow-500/40",
    };
  if (aqi <= 150)
    return {
      label: "Unhealthy · Sensitive",
      color: "#f97316",
      glow: "rgba(249,115,22,0.35)",
      bg: "rgba(249,115,22,0.08)",
      badgeClass: "bg-orange-500/20 text-orange-400 border-orange-500/40",
    };
  if (aqi <= 200)
    return {
      label: "Unhealthy",
      color: "#ef4444",
      glow: "rgba(239,68,68,0.35)",
      bg: "rgba(239,68,68,0.08)",
      badgeClass: "bg-red-500/20 text-red-400 border-red-500/40",
    };
  if (aqi <= 300)
    return {
      label: "Very Unhealthy",
      color: "#a855f7",
      glow: "rgba(168,85,247,0.35)",
      bg: "rgba(168,85,247,0.08)",
      badgeClass: "bg-purple-500/20 text-purple-400 border-purple-500/40",
    };
  return {
    label: "Hazardous",
    color: "#7c0f0f",
    glow: "rgba(124,15,15,0.45)",
    bg: "rgba(124,15,15,0.08)",
    badgeClass: "bg-red-900/30 text-red-300 border-red-800/60",
  };
}

function ArcGauge({ aqi, color, glow }: { aqi: number; color: string; glow: string }) {
  const MAX_AQI = 300;
  const fraction = Math.min(aqi / MAX_AQI, 1);
  const R = 80;
  const cx = 110;
  const cy = 100;

  // Arc from left (180°) to right (0°) going clockwise through top
  const angle = Math.PI * fraction;
  const endX = cx - R * Math.cos(angle);
  const endY = cy - R * Math.sin(angle);
  const largeArc = fraction > 0.5 ? 1 : 0;

  const bgStart = `M ${cx - R} ${cy}`;
  const bgArc = `A ${R} ${R} 0 0 1 ${cx + R} ${cy}`;

  const progressStart = `M ${cx - R} ${cy}`;
  const progressArc =
    fraction < 0.01
      ? ""
      : `A ${R} ${R} 0 ${largeArc} 1 ${endX.toFixed(2)} ${endY.toFixed(2)}`;

  return (
    <svg
      viewBox="0 0 220 115"
      className="w-full max-w-[260px] mx-auto"
      aria-label={`AQI gauge showing ${aqi}`}
    >
      {/* Glow filter */}
      <defs>
        <filter id="arc-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <linearGradient id="arc-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6b21e8" />
          <stop offset="100%" stopColor={color} />
        </linearGradient>
      </defs>

      {/* Tick marks */}
      {Array.from({ length: 11 }).map((_, i) => {
        const tickAngle = Math.PI - (Math.PI * i) / 10;
        const innerR = R - 6;
        const outerR = R + 4;
        const x1 = cx + innerR * Math.cos(tickAngle);
        const y1 = cy - innerR * Math.sin(tickAngle);
        const x2 = cx + outerR * Math.cos(tickAngle);
        const y2 = cy - outerR * Math.sin(tickAngle);
        return (
          <line
            key={i}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke={i % 5 === 0 ? "rgba(139,92,246,0.5)" : "rgba(139,92,246,0.2)"}
            strokeWidth={i % 5 === 0 ? 2 : 1}
          />
        );
      })}

      {/* Background track */}
      <path
        d={`${bgStart} ${bgArc}`}
        fill="none"
        stroke="rgba(139,92,246,0.12)"
        strokeWidth="10"
        strokeLinecap="round"
      />

      {/* Progress arc */}
      {fraction >= 0.01 && (
        <path
          d={`${progressStart} ${progressArc}`}
          fill="none"
          stroke="url(#arc-grad)"
          strokeWidth="10"
          strokeLinecap="round"
          filter="url(#arc-glow)"
          style={{ filter: `drop-shadow(0 0 6px ${glow})` }}
        />
      )}

      {/* Needle dot */}
      {fraction >= 0.01 && (
        <circle
          cx={endX}
          cy={endY}
          r="5"
          fill={color}
          style={{ filter: `drop-shadow(0 0 4px ${glow})` }}
        />
      )}

      {/* Center labels */}
      <text
        x={cx}
        y={cy + 4}
        textAnchor="middle"
        fontSize="28"
        fontWeight="700"
        fontFamily="monospace"
        fill="white"
      >
        {aqi}
      </text>
      <text
        x={cx}
        y={cy + 18}
        textAnchor="middle"
        fontSize="9"
        fill="rgba(255,255,255,0.45)"
        fontFamily="sans-serif"
      >
        AQI
      </text>

      {/* Scale labels */}
      <text x={cx - R - 2} y={cy + 16} fontSize="8" fill="rgba(255,255,255,0.3)" textAnchor="middle">0</text>
      <text x={cx + R + 2} y={cy + 16} fontSize="8" fill="rgba(255,255,255,0.3)" textAnchor="middle">300</text>
    </svg>
  );
}

export function AQICard({ aqi }: AQICardProps) {
  const level = getAQILevel(aqi);

  return (
    <Card
      className="border-border bg-card relative overflow-hidden"
      style={{ boxShadow: `0 0 40px ${level.glow}` }}
    >
      {/* Subtle background glow blob */}
      <div
        className="absolute inset-0 rounded-xl opacity-20 pointer-events-none"
        style={{
          background: `radial-gradient(ellipse at 50% 0%, ${level.glow} 0%, transparent 70%)`,
        }}
      />

      <CardHeader className="pb-2 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wind size={16} className="text-primary" />
            <CardTitle className="text-base font-semibold text-foreground">
              Current AQI
            </CardTitle>
          </div>
          <Badge
            variant="outline"
            className={`text-xs font-semibold ${level.badgeClass}`}
          >
            {level.label}
          </Badge>
        </div>
        <CardDescription>Almaty · Live sensor reading</CardDescription>
      </CardHeader>

      <CardContent className="relative z-10 space-y-4">
        {/* Gauge */}
        <ArcGauge aqi={aqi} color={level.color} glow={level.glow} />

        <Separator className="bg-border" />

        {/* Sub-metrics row */}
        <div className="grid grid-cols-3 gap-2 text-center">
          {[
            { label: "PM2.5", value: "58.3", unit: "μg/m³" },
            { label: "NO₂", value: "38.2", unit: "μg/m³" },
            { label: "O₃", value: "47.6", unit: "μg/m³" },
          ].map((m) => (
            <div key={m.label} className="rounded-lg bg-muted/50 py-2.5 px-1">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-0.5">
                {m.label}
              </p>
              <p className="text-sm font-bold font-mono text-foreground">
                {m.value}
              </p>
              <p className="text-[9px] text-muted-foreground">{m.unit}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
