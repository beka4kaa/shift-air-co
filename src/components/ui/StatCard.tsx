import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  unit: string;
  change: string;
  trend: "up" | "down";
  icon: LucideIcon;
  color: string;
}

export function StatCard({ title, value, unit, change, trend, icon: Icon, color }: StatCardProps) {
  return (
    <div className="rounded-xl border border-env-border bg-env-card p-5 hover:border-env-green-500/30 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-medium uppercase tracking-widest text-env-text-muted">
          {title}
        </span>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-env-surface border border-env-border">
          <Icon size={15} className={color} />
        </div>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <span className="text-2xl font-bold font-mono text-env-text-primary">
            {value}
          </span>
          {unit && (
            <span className="ml-1 text-xs text-env-text-muted">{unit}</span>
          )}
        </div>
        <div
          className={`flex items-center gap-1 text-xs font-medium ${
            trend === "down" ? "text-env-green-400" : "text-red-400"
          }`}
        >
          {trend === "down" ? (
            <TrendingDown size={12} />
          ) : (
            <TrendingUp size={12} />
          )}
          {change}
        </div>
      </div>
    </div>
  );
}
