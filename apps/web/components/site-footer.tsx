import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="page-container site-footer">
      <span>PocketOrbit · Your crypto, in one clear view.</span>
      <nav aria-label="Footer navigation">
        <Link href="/security">Security</Link>
        <Link href="/privacy">Privacy</Link>
        <Link href="/terms">Terms</Link>
      </nav>
    </footer>
  );
}
