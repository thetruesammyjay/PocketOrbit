import Image from "next/image";
import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="page-container site-footer-inner">
        <div className="site-footer-brand">
          <Link className="site-footer-logo-link" href="/" aria-label="PocketOrbit home">
            <Image className="site-footer-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} />
          </Link>
          <p>Your crypto, in one clear view.</p>
        </div>
        <div className="site-footer-meta">
          <span className="site-footer-live"><span aria-hidden="true" />Live demo <small>sample data</small></span>
          <nav aria-label="Footer navigation">
            <Link href="/security">Security</Link>
            <Link href="/privacy">Privacy</Link>
            <Link href="/terms">Terms</Link>
          </nav>
        </div>
      </div>
    </footer>
  );
}
