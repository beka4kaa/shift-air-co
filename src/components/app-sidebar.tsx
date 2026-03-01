"use client"

import * as React from "react"
import Link from "next/link"
import {
  ActivityIcon,
  BarChartIcon,
  HelpCircleIcon,
  InfoIcon,
  MapIcon,
  SearchIcon,
  SettingsIcon,
  WindIcon,
  DatabaseIcon,
  AlertTriangleIcon,
  SatelliteIcon,
} from "lucide-react"

import { NavDocuments } from "@/components/nav-documents"
import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: "SmogNet",
    email: "team@shift.ai",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Overview",
      url: "/",
      icon: ActivityIcon,
    },
    {
      title: "Statistics",
      url: "/statistics",
      icon: BarChartIcon,
    },
    {
      title: "Maps",
      url: "/maps",
      icon: MapIcon,
    },
    {
      title: "About the Model",
      url: "/about",
      icon: InfoIcon,
    },
  ],
  navSecondary: [
    {
      title: "Settings",
      url: "#",
      icon: SettingsIcon,
    },
    {
      title: "Help",
      url: "#",
      icon: HelpCircleIcon,
    },
    {
      title: "Search",
      url: "#",
      icon: SearchIcon,
    },
  ],
  documents: [
    {
      name: "Sensor Data",
      url: "#",
      icon: DatabaseIcon,
    },
    {
      name: "Alerts & Reports",
      url: "#",
      icon: AlertTriangleIcon,
    },
    {
      name: "Satellite Feed",
      url: "#",
      icon: SatelliteIcon,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <Link href="/">
                <div className="flex h-5 w-5 items-center justify-center rounded bg-primary">
                  <WindIcon className="h-3 w-3 text-primary-foreground" />
                </div>
                <span className="text-base font-bold tracking-tight">shift.</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavDocuments items={data.documents} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
