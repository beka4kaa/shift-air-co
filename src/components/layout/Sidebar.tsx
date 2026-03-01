"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Wind, BarChart2, Map, Info, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Home", icon: Activity },
  { href: "/statistics", label: "Statistics", icon: BarChart2 },
  { href: "/maps", label: "Maps", icon: Map },
  { href: "/about", label: "About the Model", icon: Info },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-60 flex-col border-r border-border bg-card shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 border-b border-border px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary shadow-lg shadow-primary/30">
          <Wind size={18} className="text-primary-foreground" />
        </div>
        <div>
          <p className="text-sm font-bold text-foreground leading-none">
            shift.
          </p>
          <p className="text-[10px] text-muted-foreground uppercase tracking-widest mt-0.5">
            smog dashboard
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
          Navigation
        </p>
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all",
                active
                  ? "bg-primary/15 text-primary border border-primary/30 font-medium"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon
                size={16}
                className={active ? "text-primary" : "text-muted-foreground"}
              />
              {label}
              {active && (
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-border px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
          <span className="text-xs text-muted-foreground">Live · Updated now</span>
        </div>
        <p className="mt-1 text-[10px] text-muted-foreground">SmogNet v3.2.1</p>
      </div>
    </aside>
  );
}
