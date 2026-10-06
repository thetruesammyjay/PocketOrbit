"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { Icon, type IconName } from "@/components/icon";

const primaryLinks: { href: string; label: string; icon: IconName }[] = [
  { href: "/app", label: "Overview", icon: "home" },
  { href: "/app/portfolio", label: "Portfolio", icon: "wallet" },
  { href: "/app/activity", label: "Activity", icon: "activity" },
  { href: "/app/sources", label: "Sources", icon: "chart" },
  { href: "/app/insights", label: "Insights", icon: "chart" },
  { href: "/app/learn", label: "Learn", icon: "more" }
];

const mobileLinks = [
  { href: "/app", label: "Home", icon: "home" as const },
  { href: "/app/portfolio", label: "Portfolio", icon: "wallet" as const },
  { href: "/app/activity", label: "Activity", icon: "activity" as const },
  { href: "/app/insights", label: "Insights", icon: "chart" as const }
];

const moreLinks = [
  ["Sources", "/app/sources"],
  ["Import a file", "/app/import"],
  ["Add a wallet", "/app/wallets/add"],
  ["Reports", "/app/reports"],
  ["Learn", "/app/learn"],
  ["Settings", "/app/settings"]
];

function Brand() {
  return (
    <Link className="brand-lockup" href="/app" aria-label="PocketOrbit overview">
      <Image className="brand-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} priority />
    </Link>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [moreOpen, setMoreOpen] = useState(false);

  useEffect(() => {
    if (!moreOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMoreOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [moreOpen]);

  const isCurrent = (href: string) => pathname === href || (href !== "/app" && pathname.startsWith(`${href}/`));

  return (
    <div className="app-frame">
      <aside className="app-sidebar" aria-label="Portfolio navigation">
        <Brand />
        <div className="nav-label">Your portfolio</div>
        <nav className="sidebar-nav">
          {primaryLinks.map((item) => (
            <Link className="sidebar-link" href={item.href} aria-current={isCurrent(item.href) ? "page" : undefined} key={item.href}>
              <span className="sidebar-icon"><Icon name={item.icon} /></span>
              <span>{item.label}</span>
            </Link>
          ))}
          <Link className="sidebar-link" href="/app/reports" aria-current={isCurrent("/app/reports") ? "page" : undefined}>
            <span className="sidebar-icon"><Icon name="clock" /></span>
            <span>Reports</span>
          </Link>
        </nav>
        <div className="sidebar-bottom">
          <span className="badge badge--warning">Sample portfolio</span>
          <p className="sample-note">Illustrative values only. No wallet is connected.</p>
        </div>
      </aside>

      <main className="app-main">
        <div className="mobile-app-header">
          <Brand />
          <div className="mobile-app-header-actions">
            <span className="badge badge--warning">Sample</span>
            <button
              className="button button--quiet app-menu-trigger"
              type="button"
              aria-label={moreOpen ? "Close page menu" : "Open page menu"}
              aria-expanded={moreOpen}
              aria-haspopup="dialog"
              aria-controls="more-sheet"
              onClick={() => setMoreOpen((open) => !open)}
            >
              <span className="menu-glyph" aria-hidden="true"><span /><span /><span /></span>
            </button>
          </div>
        </div>
        <header className="app-topbar">
          <div className="topbar-context"><span className="topbar-name">My portfolio</span>Reporting in USD</div>
          <span className="topbar-context">Sample snapshot · not live data</span>
        </header>
        <div className="app-content">{children}</div>
      </main>

      <nav className="mobile-bottom-nav" aria-label="Main portfolio navigation">
        {mobileLinks.map((item) => (
          <Link className="mobile-nav-link" href={item.href} aria-current={isCurrent(item.href) ? "page" : undefined} key={item.href}>
            <span className="sidebar-icon"><Icon name={item.icon} size={21} /></span>
            <span>{item.label}</span>
          </Link>
        ))}
        <button className="mobile-nav-link" type="button" aria-expanded={moreOpen} aria-haspopup="dialog" onClick={() => setMoreOpen(true)}>
          <span className="sidebar-icon"><Icon name="more" size={21} /></span>
          <span>More</span>
        </button>
      </nav>

      {moreOpen && (
        <div className="more-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setMoreOpen(false); }}>
          <section className="more-sheet" id="more-sheet" role="dialog" aria-modal="true" aria-labelledby="more-title">
            <div className="more-sheet-header">
              <h2 id="more-title">More</h2>
              <button className="button button--quiet" type="button" onClick={() => setMoreOpen(false)} aria-label="Close menu">Close</button>
            </div>
            <nav className="more-grid" aria-label="More portfolio pages">
              {moreLinks.map(([label, href]) => <Link href={href} key={href} onClick={() => setMoreOpen(false)}>{label}</Link>)}
            </nav>
          </section>
        </div>
      )}
    </div>
  );
}
