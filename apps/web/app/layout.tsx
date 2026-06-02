import type { Metadata } from "next";
import { BarChart3, Boxes, ClipboardCheck, FileText, Library } from "lucide-react";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "SoClean Content System",
  description: "Phase 1/2 operating shell for SoClean content workflows.",
};

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/brand-memory", label: "Brand Memory", icon: Library },
  { href: "/products", label: "Products", icon: Boxes },
  { href: "/campaigns", label: "Campaigns", icon: FileText },
  { href: "/content-review", label: "Content Review", icon: ClipboardCheck },
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
