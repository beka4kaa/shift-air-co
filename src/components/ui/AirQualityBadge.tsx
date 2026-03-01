interface AirQualityBadgeProps {
  level: string;
  aqi: number;
  compact?: boolean;
}

function getBadgeClasses(aqi: number) {
  if (aqi <= 50) return "bg-green-500/15 border-green-500/40 text-green-400";
  if (aqi <= 100) return "bg-yellow-500/15 border-yellow-500/40 text-yellow-400";
  if (aqi <= 150) return "bg-orange-500/15 border-orange-500/40 text-orange-400";
  if (aqi <= 200) return "bg-red-500/15 border-red-500/40 text-red-400";
  return "bg-purple-600/15 border-purple-600/40 text-purple-400";
}

export function AirQualityBadge({ level, aqi, compact = false }: AirQualityBadgeProps) {
  const classes = getBadgeClasses(aqi);

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold font-mono ${classes}`}
      >
        {aqi}
      </span>
    );
  }

  return (
    <div className={`inline-flex flex-col items-center rounded-xl border px-4 py-2 ${classes}`}>
      <span className="text-2xl font-bold font-mono">{aqi}</span>
      <span className="text-xs font-medium opacity-80">{level}</span>
    </div>
  );
}
