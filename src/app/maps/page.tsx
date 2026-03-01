import { MapPin } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { STATIONS } from "@/lib/stations"
import { SmogMapClient } from "@/components/smog-map-client"

const AQI_LEGEND = [
  { label: "Good",            range: "0–50",   color: "bg-green-500"  },
  { label: "Moderate",        range: "51–100",  color: "bg-yellow-400" },
  { label: "Sensitive Groups",range: "101–150", color: "bg-orange-400" },
  { label: "Unhealthy",       range: "151–200", color: "bg-red-500"    },
  { label: "Very Unhealthy",  range: "201–300", color: "bg-purple-500" },
  { label: "Hazardous",       range: "301+",    color: "bg-rose-700"   },
]

function aqiBadgeClass(aqi: number): string {
  if (aqi <= 50)  return "text-green-400  border-green-400/40  bg-green-400/10"
  if (aqi <= 100) return "text-yellow-400 border-yellow-400/40 bg-yellow-400/10"
  if (aqi <= 150) return "text-orange-400 border-orange-400/40 bg-orange-400/10"
  if (aqi <= 200) return "text-red-400    border-red-400/40    bg-red-400/10"
  if (aqi <= 300) return "text-purple-400 border-purple-400/40 bg-purple-400/10"
  return                  "text-rose-600  border-rose-600/40   bg-rose-600/10"
}

function aqiLabel(aqi: number): string {
  if (aqi <= 50)  return "Good"
  if (aqi <= 100) return "Moderate"
  if (aqi <= 150) return "Sensitive"
  if (aqi <= 200) return "Unhealthy"
  if (aqi <= 300) return "Very Unhealthy"
  return "Hazardous"
}

export default function MapsPage() {
  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-col gap-6 px-4 py-6 lg:px-6">

      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Smog Map</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Live air-quality monitoring stations across Central Asia · Click a circle for details
        </p>
      </div>

      {/* Map card */}
      <Card className="overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-base">AQI Heatmap — Central Asia</CardTitle>
            <CardDescription>Circle size and colour scale with AQI level</CardDescription>
          </div>
          {/* Legend pills */}
          <div className="hidden sm:flex flex-wrap gap-2 justify-end">
            {AQI_LEGEND.map((l) => (
              <span key={l.label} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className={`inline-block h-2.5 w-2.5 rounded-full ${l.color}`} />
                {l.label}
              </span>
            ))}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {/* Map fills the card — fixed height, flex-grows on larger screens */}
          <div className="h-[420px] w-full lg:h-[520px]">
            <SmogMapClient />
          </div>
        </CardContent>
      </Card>

      {/* Mobile legend */}
      <div className="flex sm:hidden flex-wrap gap-x-4 gap-y-2">
        {AQI_LEGEND.map((l) => (
          <span key={l.label} className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={`inline-block h-2.5 w-2.5 rounded-full ${l.color}`} />
            {l.label} ({l.range})
          </span>
        ))}
      </div>

      {/* Station grid */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <MapPin className="size-4 text-primary" />
            Monitoring Stations
          </CardTitle>
          <CardDescription>{STATIONS.length} stations · Central Asia</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {STATIONS.map((st) => (
              <div
                key={st.name}
                className="flex items-center justify-between rounded-lg border border-border bg-muted/30 px-4 py-3"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium text-sm">{st.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {st.lat.toFixed(2)}°N, {st.lng.toFixed(2)}°E
                  </p>
                </div>
                <Badge
                  variant="outline"
                  className={`ml-3 shrink-0 rounded-lg text-xs ${aqiBadgeClass(st.aqi)}`}
                >
                  {st.aqi} · {aqiLabel(st.aqi)}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
