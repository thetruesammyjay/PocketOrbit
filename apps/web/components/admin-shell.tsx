import Link from "next/link";
import Image from "next/image";
import type { ReactNode } from "react";

const links = ["users", "portfolios", "imports", "sources", "assets", "jobs", "system", "audit", "settings"];

export function AdminShell({ children }: { children: ReactNode }) {
  return (
    <div className="admin-frame">
      <aside className="admin-sidebar">
        <Link className="brand-lockup" href="/admin" aria-label="PocketOrbit admin"><Image className="brand-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} /></Link>
        <p className="sample-note">Read-only operations view. Admin page access is recorded for review.</p>
        <nav className="sidebar-nav" aria-label="Admin navigation">
          <Link className="sidebar-link" href="/admin">Overview</Link>
          {links.map((item) => <Link className="sidebar-link" href={`/admin/${item}`} key={item}>{item[0].toUpperCase() + item.slice(1)}</Link>)}
        </nav>
      </aside>
      <main className="admin-content">{children}</main>
    </div>
  );
}
