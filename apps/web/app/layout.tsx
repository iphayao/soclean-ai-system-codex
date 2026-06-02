import type { Metadata } from "next";
import {
  BarChart3,
  Boxes,
  CalendarDays,
  ClipboardCheck,
  FileText,
  Library,
  LineChart,
  PlayCircle,
  Settings,
} from "lucide-react";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "SoClean Content System",
  description: "Admin dashboard for SoClean content workflows.",
};

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/brand-memory", label: "Brand Memory", icon: Library },
  { href: "/products", label: "Products", icon: Boxes },
  { href: "/campaigns", label: "Campaigns", icon: FileText },
  { href: "/content-calendar", label: "Calendar", icon: CalendarDays },
  { href: "/content-review", label: "Content Review", icon: ClipboardCheck },
  { href: "/performance", label: "Performance", icon: LineChart },
  { href: "/agent-runs", label: "Agent Runs", icon: PlayCircle },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div className="brand-lockup">
              <strong>SoClean</strong>
              <span>Agentic AI Content System</span>
            </div>
            <nav className="nav" aria-label="Primary navigation">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link key={item.href} href={item.href}>
                    <Icon size={18} aria-hidden="true" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </aside>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
