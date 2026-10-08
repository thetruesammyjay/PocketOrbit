"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { Icon, type IconName } from "@/components/icon";
import { API_BASE_PATH } from "@/lib/api-base-path";

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
  const router = useRouter();
  const [moreOpen, setMoreOpen] = useState(false);
  const [signedIn, setSignedIn] = useState<boolean | null>(null);

  useEffect(() => {
    void fetch(`${API_BASE_PATH}/auth/me`, { credentials: "include", cache: "no-store" })
      .then((response) => setSignedIn(response.ok))
      .catch(() => setSignedIn(false));
  }, []);

  useEffect(() => {
    if (!moreOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMoreOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [moreOpen]);

  const isCurrent = (href: string) => pathname === href || (href !== "/app" && pathname.startsWith(`${href}/`));

  async function signOut() {
    await fetch(`${API_BASE_PATH}/auth/logout`, {
      method: "POST",
      credentials: "include"
    }).catch(() => undefined);
    setSignedIn(false);
    setMoreOpen(false);
    router.replace("/app");
    router.refresh();
  }

  return (
    <div className="app-frame">
      <aside className="app-sidebar" aria-label="Portfolio navigation">
        <Brand />
        <div className="nav-label">Your portfolio</div>
        <nav className="sidebar-nav">
          {primaryLinks.map((item) => (
            <Link className="sidebar-link" href={item.href} aria-current={isCurrent(item.href) ? "page" : undefined} key={item.href}>
              <span className="sidebar-icon"><Icon name={item.icon} /></span><span>{item.label}</span>
            </Link>
          ))}
          <Link className="sidebar-link" href="/app/reports" aria-current={isCurrent("/app/reports") ? "page" : undefined}>
            <span className="sidebar-icon"><Icon name="clock" /></span><span>Reports</span>
          </Link>
        </nav>
        <div className="sidebar-bottom">
          <span className={`badge ${signedIn ? "badge--success" : "badge--warning"}`}>{signedIn ? "Saved portfolio" : signedIn === false ? "Sample portfolio" : "Loading portfolio"}</span>
          <p className="sample-note">{signedIn ? "Your connected sources are read-only." : "Illustrative values only until you sign in."}</p>
          {signedIn ? <button className="text-link muted" type="button" onClick={() => void signOut()}>Sign out</button> : <Link className="text-link muted" href="/login">Sign in to save</Link>}
        </div>
      </aside>

      <main className="app-main">
        <div className="mobile-app-header">
          <Brand />
          <div className="mobile-app-header-actions">
            <span className={`badge ${signedIn ? "badge--success" : "badge--warning"}`}>{signedIn ? "Saved" : "Sample"}</span>
            <button className="button button--quiet app-menu-trigger" type="button" aria-label={moreOpen ? "Close page menu" : "Open page menu"} aria-expanded={moreOpen} aria-haspopup="dialog" aria-controls="more-sheet" onClick={() => setMoreOpen((open) => !open)}>
              <span className="menu-glyph" aria-hidden="true"><span /><span /><span /></span>
            </button>
          </div>
        </div>
        <header className="app-topbar">
          <div className="topbar-context"><span className="topbar-name">My portfolio</span>{signedIn ? "Saved portfolio" : "Sample view"}</div>
          <span className="topbar-context">{signedIn ? "Read-only sources · update times shown" : "Sample snapshot · not live data"}</span>
        </header>
        <div className="app-content">{children}</div>
      </main>

      <nav className="mobile-bottom-nav" aria-label="Main portfolio navigation">
        {mobileLinks.map((item) => (
          <Link className="mobile-nav-link" href={item.href} aria-current={isCurrent(item.href) ? "page" : undefined} key={item.href}>
            <span className="sidebar-icon"><Icon name={item.icon} size={21} /></span><span>{item.label}</span>
          </Link>
        ))}
        <button className="mobile-nav-link" type="button" aria-expanded={moreOpen} aria-haspopup="dialog" onClick={() => setMoreOpen(true)}>
          <span className="sidebar-icon"><Icon name="more" size={21} /></span><span>More</span>
        </button>
      </nav>

      {moreOpen && (
        <div className="more-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setMoreOpen(false); }}>
          <section className="more-sheet" id="more-sheet" role="dialog" aria-modal="true" aria-labelledby="more-title">
            <div className="more-sheet-header"><h2 id="more-title">More</h2><button className="button button--quiet" type="button" onClick={() => setMoreOpen(false)} aria-label="Close menu">Close</button></div>
            <nav className="more-grid" aria-label="More portfolio pages">
              {moreLinks.map(([label, href]) => <Link href={href} key={href} onClick={() => setMoreOpen(false)}>{label}</Link>)}
              {signedIn ? <button type="button" onClick={() => void signOut()}>Sign out</button> : <Link href="/login" onClick={() => setMoreOpen(false)}>Sign in</Link>}
            </nav>
          </section>
        </div>
      )}
    </div>
  );
}
