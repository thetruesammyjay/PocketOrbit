"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

export function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="site-header">
      <div className="page-container site-header-inner">
        <Link className="brand-lockup" href="/" aria-label="PocketOrbit home">
          <Image className="brand-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} priority />
        </Link>
        <nav className="site-links" aria-label="Main navigation">
          <Link href="/#features">Product</Link>
          <Link href="/how-it-works">How it works</Link>
          <Link href="/security">Security</Link>
          <Link href="/learn">Learn</Link>
        </nav>
        <div className="site-actions">
          <Link className="button button--quiet" href="/login">Sign in</Link>
          <Link className="button button--primary" href="/app">Explore demo</Link>
          <button
            className="button button--quiet site-menu-trigger"
            type="button"
            aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={menuOpen}
            aria-controls="site-mobile-menu"
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span className="menu-glyph" aria-hidden="true"><span /><span /><span /></span>
          </button>
        </div>
        {menuOpen && (
          <nav className="site-mobile-menu" id="site-mobile-menu" aria-label="Mobile navigation">
            <Link href="/#features" onClick={closeMenu}>Product</Link>
            <Link href="/how-it-works" onClick={closeMenu}>How it works</Link>
            <Link href="/security" onClick={closeMenu}>Security</Link>
            <Link href="/learn" onClick={closeMenu}>Learn</Link>
            <Link href="/privacy" onClick={closeMenu}>Privacy</Link>
            <Link href="/terms" onClick={closeMenu}>Terms</Link>
            <Link href="/login" onClick={closeMenu}>Sign in</Link>
            <Link href="/app" onClick={closeMenu}>Explore sample portfolio</Link>
          </nav>
        )}
      </div>
    </header>
  );
}
