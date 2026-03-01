import { BarChart2, TrendingDown, TrendingUp, Calendar } from "lucide-react";

const pollutants = [
  { name: "PM2.5", today: 58.3, yesterday: 61.7, limit: 25, unit: "μg/m³", color: "bg-red-500" },
  { name: "PM10", today: 94.1, yesterday: 102.4, limit: 50, unit: "μg/m³", color: "bg-orange-500" },
  { name: "NO₂", today: 38.2, yesterday: 35.8, limit: 40, unit: "μg/m³", color: "bg-yellow-500" },
  { name: "SO₂", today: 12.4, yesterday: 14.1, limit: 20, unit: "μg/m³", color: "bg-env-teal-500" },
  { name: "CO", today: 0.8, yesterday: 0.9, limit: 10, unit: "mg/m³", color: "bg-env-green-500" },
  { name: "O₃", today: 47.6, yesterday: 44.2, limit: 100, unit: "μg/m³", color: "bg-blue-500" },
];

const weeklyData = [
  { day: "Mon", aqi: 112 },
  { day: "Tue", aqi: 98 },
  { day: "Wed", aqi: 135 },
  { day: "Thu", aqi: 156 },
  { day: "Fri", aqi: 142 },
  { day: "Sat", aqi: 89 },
  { day: "Sun", aqi: 76 },
];

const maxAqi = Math.max(...weeklyData.map((d) => d.aqi));

function aqiColor(aqi: number) {
  if (aqi <= 50) return "bg-env-green-500";
  if (aqi <= 100) return "bg-yellow-400";
  if (aqi <= 150) return "bg-orange-400";
  if (aqi <= 200) return "bg-red-500";
  return "bg-purple-600";
}

export default function StatisticsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-env-text-primary">Statistics</h1>
        <p className="mt-1 text-env-text-secondary">
          Historical air quality data and pollutant trends
        </p>
      </div>

      {/* Weekly AQI Bar Chart */}
      <div className="rounded-xl border border-env-border bg-env-card p-6">
        <div className="mb-6 flex items-center gap-2">
          <BarChart2 size={18} className="text-env-teal-400" />
          <h2 className="text-lg font-semibold text-env-text-primary">
            7-Day AQI Trend
          </h2>
          <span className="ml-auto flex items-center gap-1 text-xs text-env-text-muted">
            <Calendar size={12} /> This Week
          </span>
        </div>
        <div className="flex h-48 items-end gap-3">
          {weeklyData.map((d) => (
            <div key={d.day} className="flex flex-1 flex-col items-center gap-2">
              <span className="text-xs font-mono text-env-text-secondary">{d.aqi}</span>
              <div
                className={`w-full rounded-t-md ${aqiColor(d.aqi)} opacity-90 transition-all hover:opacity-100`}
                style={{ height: `${(d.aqi / maxAqi) * 100}%` }}
              />
              <span className="text-xs text-env-text-muted">{d.day}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Pollutant Table */}
      <div className="rounded-xl border border-env-border bg-env-card p-6">
        <h2 className="mb-4 text-lg font-semibold text-env-text-primary">
          Pollutant Concentrations
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-env-border text-env-text-muted">
                <th className="pb-3 text-left font-medium">Pollutant</th>
                <th className="pb-3 text-right font-medium">Today</th>
                <th className="pb-3 text-right font-medium">Yesterday</th>
                <th className="pb-3 text-right font-medium">WHO Limit</th>
                <th className="pb-3 text-right font-medium">Trend</th>
                <th className="pb-3 text-left pl-6 font-medium">Bar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-env-border">
              {pollutants.map((p) => {
                const pct = Math.min((p.today / p.limit) * 100, 150);
                const improved = p.today < p.yesterday;
                return (
                  <tr key={p.name} className="group hover:bg-env-surface/50">
                    <td className="py-3 font-mono font-semibold text-env-text-primary">
                      {p.name}
                    </td>
                    <td className="py-3 text-right font-mono text-env-text-primary">
                      {p.today}{" "}
                      <span className="text-xs text-env-text-muted">{p.unit}</span>
                    </td>
                    <td className="py-3 text-right font-mono text-env-text-secondary">
                      {p.yesterday}
                    </td>
                    <td className="py-3 text-right font-mono text-env-text-muted">
                      {p.limit}
                    </td>
                    <td className="py-3 text-right">
                      {improved ? (
                        <TrendingDown size={14} className="ml-auto text-env-green-400" />
                      ) : (
                        <TrendingUp size={14} className="ml-auto text-red-400" />
                      )}
                    </td>
                    <td className="py-3 pl-6">
                      <div className="h-2 w-full max-w-[120px] rounded-full bg-env-surface">
                        <div
                          className={`h-2 rounded-full ${p.color} opacity-80`}
                          style={{ width: `${Math.min(pct, 100)}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
