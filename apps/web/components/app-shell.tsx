"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { MouseEvent, ReactNode } from "react";

import { Icon, type IconName } from "@/components/icon";
import { API_BASE_PATH } from "@/lib/api-base-path";

const primaryLinks: { href: string; label: string; icon: IconName }[] = [
  { href: "/app", label: "Overview", icon: "home" },
  { href: "/app/portfolio", label: "Portfolio", icon: "wallet" },
  { href: "/app/activity", label: "Activity", icon: "activity" },
  { href: "/app/sources", label: "Sources", icon: "database" },
  { href: "/app/insights", label: "Insights", icon: "chart" },
  { href: "/app/learn", label: "Learn", icon: "book" }
];

const mobileLinks = [
  { href: "/app", label: "Home", icon: "home" as const },
  { href: "/app/portfolio", label: "Portfolio", icon: "wallet" as const },
  { href: "/app/activity", label: "Activity", icon: "activity" as const },
  { href: "/app/insights", label: "Insights", icon: "chart" as const }
];

const moreLinks: { label: string; href: string; icon: IconName }[] = [
  { label: "Sources", href: "/app/sources", icon: "database" },
  { label: "Import a file", href: "/app/import", icon: "upload" },
  { label: "Add a wallet", href: "/app/wallets/add", icon: "walletAdd" },
  { label: "Reports", href: "/app/reports", icon: "clock" },
  { label: "Learn", href: "/app/learn", icon: "book" },
  { label: "Settings", href: "/app/settings", icon: "settings" }
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
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null);

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

  useEffect(() => {
    setPendingNavigation(null);
  }, [pathname]);

  useEffect(() => {
    if (!pendingNavigation) return;
    const timeoutId = window.setTimeout(() => setPendingNavigation(null), 15_000);
    return () => window.clearTimeout(timeoutId);
  }, [pendingNavigation]);

  const isCurrent = (href: string) => pathname === href || (href !== "/app" && pathname.startsWith(`${href}/`));

  function prepareNavigation(event: MouseEvent<HTMLAnchorElement>, href: string, label: string) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.currentTarget.target === "_blank") return;
    setMoreOpen(false);
    if (!isCurrent(href)) setPendingNavigation(label);
  }

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
            <Link className="sidebar-link" href={item.href} aria-current={isCurrent(item.href) ? "page" : undefined} key={item.href} onClick={(event) => prepareNavigation(event, item.href, item.label)}>
              <span className="sidebar-icon"><Icon name={item.icon} /></span><span>{item.label}</span>
            </Link>
          ))}
          <Link className="sidebar-link" href="/app/reports" aria-current={isCurrent("/app/reports") ? "page" : undefined} onClick={(event) => prepareNavigation(event, "/app/reports", "Reports")}>
            <span className="sidebar-icon"><Icon name="clock" /></span><span>Reports</span>
          </Link>
        </nav>
        <div className="sidebar-bottom">
          <span className={`badge ${signedIn ? "badge--success" : "badge--warning"}`}>{signedIn ? "Saved portfolio" : signedIn === false ? "Sample portfolio" : "Loading portfolio"}</span>
          <p className="sample-note">{signedIn ? "Your connected sources are read-only." : "Illustrative values only until you sign in."}</p>
          {signedIn ? <button className="text-link muted" type="button" onClick={() => void signOut()}>Sign out</button> : <Link className="text-link muted" href="/login">Sign in to save</Link>}
        </div>
      </aside>

      <main className="app-main" aria-busy={pendingNavigation !== null}>
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
          <Link className="mobile-nav-link" href={item.href} aria-current={isCurrent(item.href) ? "page" : undefined} key={item.href} onClick={(event) => prepareNavigation(event, item.href, item.label)}>
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
              {moreLinks.map((item) => (
                <Link className="more-grid-link" href={item.href} aria-current={isCurrent(item.href) ? "page" : undefined} key={item.href} onClick={(event) => prepareNavigation(event, item.href, item.label)}>
                  <span className="sidebar-icon"><Icon name={item.icon} size={20} /></span><span>{item.label}</span>
                </Link>
              ))}
              {signedIn ? (
                <button className="more-grid-link" type="button" onClick={() => void signOut()}>
                  <span className="sidebar-icon"><Icon name="logout" size={20} /></span><span>Sign out</span>
                </button>
              ) : (
                <Link className="more-grid-link" href="/login" onClick={() => { setMoreOpen(false); setPendingNavigation("Sign in"); }}>
                  <span className="sidebar-icon"><Icon name="user" size={20} /></span><span>Sign in</span>
                </Link>
              )}
            </nav>
          </section>
        </div>
      )}

      {pendingNavigation && (
        <div className="route-loading-overlay" role="status" aria-live="polite">
          <div className="route-loading-card">
            <span className="route-loading-orbit" aria-hidden="true" />
            <span><strong>Opening {pendingNavigation}</strong><small>Loading your portfolio view</small></span>
          </div>
        </div>
      )}
    </div>
  );
}
