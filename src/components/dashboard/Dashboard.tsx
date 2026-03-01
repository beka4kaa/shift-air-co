import { AQICard } from "./AQICard";
import { PredictionChart } from "./PredictionChart";
import { MetricsGrid } from "./MetricsGrid";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { MapPin, RefreshCw, ShieldAlert } from "lucide-react";

// Mock current data
const MOCK_AQI = 142;
const MOCK_CITY = "Almaty, Kazakhstan";
const MOCK_UPDATED = "March 1, 2026 · 14:37 UTC";

export function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <MapPin size={14} className="text-primary" />
            <span className="text-sm text-muted-foreground font-medium">
              {MOCK_CITY}
            </span>
            <Badge
              variant="outline"
              className="text-[10px] bg-primary/10 text-primary border-primary/25 py-0"
            >
              Mock Data
            </Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Air Quality Dashboard
          </h1>
        </div>

        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <div className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
            <span>Live</span>
          </div>
          <Separator orientation="vertical" className="h-3 bg-border" />
          <div className="flex items-center gap-1.5">
            <RefreshCw size={11} className="text-muted-foreground" />
            <span>{MOCK_UPDATED}</span>
          </div>
        </div>
      </div>

      {/* Training notice */}
      <div className="flex items-start gap-3 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm">
        <ShieldAlert size={16} className="text-primary mt-0.5 shrink-0" />
        <div>
          <span className="font-semibold text-primary">Model training in progress</span>
          <span className="text-muted-foreground ml-2">
            All displayed values are mock data for UI demonstration purposes only.
            SmogNet v3.2.1 is currently training on the 2021–2026 dataset.
          </span>
        </div>
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        {/* AQI Gauge — 1 col */}
        <div className="lg:col-span-1">
          <AQICard aqi={MOCK_AQI} />
        </div>

        {/* Prediction Chart — 2 cols */}
        <div className="lg:col-span-2">
          <PredictionChart />
        </div>
      </div>

      {/* Metrics row */}
      <MetricsGrid />
    </div>
  );
}
