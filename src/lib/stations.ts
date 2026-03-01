// ---------------------------------------------------------------------------
// Monitoring station definitions — importable from both server and client code
// ---------------------------------------------------------------------------

export interface Station {
  name: string
  lat: number
  lng: number
  aqi: number
  pm25: number
  pm10: number
}

export const STATIONS: Station[] = [
  { name: "Almaty Central",          lat: 43.2515, lng: 76.9450, aqi: 142, pm25: 52.4, pm10:  98.3 },
  { name: "Almaty Industrial Zone",  lat: 43.3200, lng: 77.0800, aqi: 198, pm25: 73.1, pm10: 140.2 },
  { name: "Bishkek North",           lat: 42.8700, lng: 74.5900, aqi: 114, pm25: 42.1, pm10:  79.5 },
  { name: "Bishkek South Ring",      lat: 42.8200, lng: 74.6200, aqi: 163, pm25: 60.3, pm10: 114.7 },
  { name: "Tashkent Downtown",       lat: 41.2995, lng: 69.2401, aqi: 128, pm25: 47.3, pm10:  89.6 },
  { name: "Tashkent Airport",        lat: 41.2570, lng: 69.2810, aqi:  97, pm25: 35.8, pm10:  68.2 },
  { name: "Nur-Sultan Central Park", lat: 51.1801, lng: 71.4460, aqi:  54, pm25: 19.9, pm10:  38.1 },
  { name: "Nur-Sultan Industrial",   lat: 51.1500, lng: 71.5200, aqi:  87, pm25: 32.1, pm10:  61.4 },
  { name: "Shymkent Central",        lat: 42.3200, lng: 69.5900, aqi: 119, pm25: 43.9, pm10:  83.5 },
  { name: "Shymkent Highway M-39",   lat: 42.2900, lng: 69.6600, aqi: 135, pm25: 49.8, pm10:  94.7 },
  { name: "Dushanbe City Centre",    lat: 38.5598, lng: 68.7738, aqi:  87, pm25: 32.1, pm10:  61.0 },
  { name: "Fergana Valley",          lat: 40.3800, lng: 71.7800, aqi: 156, pm25: 57.6, pm10: 109.4 },
  { name: "Almaty Mountain",         lat: 43.0500, lng: 76.9300, aqi:  38, pm25: 14.0, pm10:  26.7 },
  { name: "Aral Sea Reference",      lat: 45.0000, lng: 59.6000, aqi:  63, pm25: 23.3, pm10:  44.2 },
]
