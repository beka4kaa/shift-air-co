import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Droplets, Thermometer, Wind, CloudFog } from "lucide-react";
import { LucideIcon } from "lucide-react";

interface Metric {
  label: string;
  value: number;
  displayValue: string;
  unit: string;
  icon: LucideIcon;
  max: number;
  who?: number;
  description: string;
  status: string;
  statusClass: string;
  progressColor: string;
}

const metrics: Metric[] = [
  {
    label: "PM2.5",
    value: 58.3,
    displayValue: "58.3",
    unit: "μg/m³",
    icon: CloudFog,
    max: 100,
    who: 25,
    description: "Fine particulate matter",
    status: "High",
    statusClass: "bg-red-500/15 text-red-400 border-red-500/30",
    progressColor: "#ef4444",
  },
  {
    label: "PM10",
    value: 94.1,
    displayValue: "94.1",
    unit: "μg/m³",
    icon: Wind,
    max: 150,
    who: 50,
    description: "Coarse particulate matter",
    status: "Elevated",
    statusClass: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    progressColor: "#f97316",
  },
  {
    label: "Humidity",
    value: 67,
    displayValue: "67",
    unit: "%",
    icon: Droplets,
    max: 100,
    description: "Relative humidity",
    status: "Normal",
    statusClass: "bg-primary/15 text-primary border-primary/30",
    progressColor: "#8b5cf6",
  },
  {
    label: "Temperature",
    value: 24.6,
    displayValue: "24.6",
    unit: "°C",
    icon: Thermometer,
    max: 50,
    description: "Ambient air temperature",
    status: "Warm",
    statusClass: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    progressColor: "#eab308",
  },
];

function MetricCard({ metric }: { metric: Metric }) {
  const Icon = metric.icon;
  const pct = Math.min((metric.value / metric.max) * 100, 100);
  const whoPct = metric.who ? Math.min((metric.who / metric.max) * 100, 100) : null;

  return (
    <Card className="border-border bg-card hover:border-primary/40 transition-colors group">
      <CardHeader className="pb-3 space-y-0">
        <div className="flex items-center justify-between mb-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted border border-border group-hover:border-primary/30 transition-colors">
            <Icon size={15} className="text-primary" />
          </div>
          <Badge
            variant="outline"
            className={`text-[10px] font-semibold ${metric.statusClass}`}
          >
            {metric.status}
          </Badge>
        </div>
        <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {metric.label}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Value */}
        <div className="flex items-end gap-1.5">
          <span className="text-3xl font-bold font-mono leading-none text-foreground">
            {metric.displayValue}
          </span>
          <span className="text-sm text-muted-foreground mb-0.5">{metric.unit}</span>
        </div>

        <p className="text-[11px] text-muted-foreground">{metric.description}</p>

        {/* Progress bar */}
        <div className="space-y-1.5">
          <div className="relative h-2 w-full rounded-full bg-muted overflow-visible">
            <div
              className="absolute top-0 left-0 h-full rounded-full transition-all duration-700"
              style={{
                width: `${pct}%`,
                background: `linear-gradient(90deg, #6b21e8, ${metric.progressColor})`,
                boxShadow: `0 0 8px ${metric.progressColor}50`,
              }}
            />
            {/* WHO marker */}
            {whoPct !== null && (
              <div
                className="absolute top-1/2 -translate-y-1/2 h-4 w-px bg-white/50"
                style={{ left: `${whoPct}%` }}
                title={`WHO limit: ${metric.who} ${metric.unit}`}
              />
            )}
          </div>
          <div className="flex justify-between text-[9px] text-muted-foreground">
            <span>0</span>
            {metric.who && (
              <span
                className="text-white/30"
                style={{ marginLeft: `${whoPct! - 5}%` }}
              >
                WHO
              </span>
            )}
            <span>{metric.max}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function MetricsGrid() {
  return (
    <div className="grid grid-cols-2 gap-4 xl:grid-cols-4 col-span-full">
      {metrics.map((m) => (
        <MetricCard key={m.label} metric={m} />
      ))}
    </div>
  );
}
