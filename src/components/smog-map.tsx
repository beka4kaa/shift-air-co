"use client"

import "leaflet/dist/leaflet.css"
import L from "leaflet"
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet"
import { useEffect } from "react"
import { STATIONS } from "@/lib/stations"

// ---------------------------------------------------------------------------
// Fix Leaflet's broken default icon paths when bundled with webpack
// ---------------------------------------------------------------------------
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:       "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:     "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
})

// ---------------------------------------------------------------------------
// AQI → circle colour
// ---------------------------------------------------------------------------
function aqiColor(aqi: number): string {
  if (aqi <= 50)  return "#22c55e"  // green
  if (aqi <= 100) return "#facc15"  // yellow
  if (aqi <= 150) return "#f97316"  // orange
  if (aqi <= 200) return "#ef4444"  // red
  if (aqi <= 300) return "#a855f7"  // purple
  return "#be123c"                   // maroon / hazardous
}

function aqiLabel(aqi: number): string {
  if (aqi <= 50)  return "Good"
  if (aqi <= 100) return "Moderate"
  if (aqi <= 150) return "Unhealthy for Sensitive Groups"
  if (aqi <= 200) return "Unhealthy"
  if (aqi <= 300) return "Very Unhealthy"
  return "Hazardous"
}

// Radius scales with AQI so higher-pollution stations appear larger
function circleRadius(aqi: number): number {
  return 6 + (aqi / 300) * 22
}

// ---------------------------------------------------------------------------
// Inner hook that forces a Leaflet resize after DOM paint (fixes grey tiles)
// ---------------------------------------------------------------------------
function ResizeFix() {
  const map = useMap()
  useEffect(() => {
    setTimeout(() => map.invalidateSize(), 100)
  }, [map])
  return null
}

// ---------------------------------------------------------------------------
// Main map component (always rendered client-side)
// ---------------------------------------------------------------------------
export function SmogMap() {
  // Centre on Central Asia
  const center: [number, number] = [43.5, 72.0]

  return (
    <MapContainer
      center={center}
      zoom={5}
      scrollWheelZoom={true}
      style={{ height: "100%", width: "100%", background: "#0f172a" }}
      className="rounded-xl"
    >
      <ResizeFix />

      {/* Dark basemap from CartoDB */}
      <TileLayer
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />

      {STATIONS.map((st) => {
        const color  = aqiColor(st.aqi)
        const radius = circleRadius(st.aqi)
        return (
          <CircleMarker
            key={st.name}
            center={[st.lat, st.lng]}
            radius={radius}
            pathOptions={{
              fillColor:   color,
              fillOpacity: 0.75,
              color:       color,
              weight:      1.5,
              opacity:     0.9,
            }}
          >
            <Popup className="smog-popup">
              <div
                style={{
                  background: "#1e1b4b",
                  color: "#e2e8f0",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  minWidth: "180px",
                  fontFamily: "inherit",
                }}
              >
                <p style={{ fontWeight: 700, marginBottom: 6, fontSize: 14 }}>
                  {st.name}
                </p>
                <p style={{ margin: "2px 0", fontSize: 12 }}>
                  AQI:{" "}
                  <span style={{ color, fontWeight: 600 }}>
                    {st.aqi}
                  </span>{" "}
                  — {aqiLabel(st.aqi)}
                </p>
                <p style={{ margin: "2px 0", fontSize: 12, color: "#94a3b8" }}>
                  PM2.5: {st.pm25} μg/m³
                </p>
                <p style={{ margin: "2px 0", fontSize: 12, color: "#94a3b8" }}>
                  PM10: &nbsp;{st.pm10} μg/m³
                </p>
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </MapContainer>
  )
}
