"use client"

import dynamic from "next/dynamic"

const SmogMapLeaflet = dynamic(
  () => import("@/components/smog-map").then((m) => m.SmogMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
        Loading map…
      </div>
    ),
  }
)

export function SmogMapClient() {
  return <SmogMapLeaflet />
}
