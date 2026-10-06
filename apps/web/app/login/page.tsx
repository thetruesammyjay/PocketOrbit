import Link from "next/link";

export default function LoginPage() {
  return <main className="auth-layout"><section className="panel auth-card"><Link className="brand-lockup" href="/"><span className="brand-mark">PO</span><span>PocketOrbit</span></Link><h1>Sign in</h1><p className="muted">Account access is not configured in this scaffold.</p><label className="form-field"><span>Email</span><input type="email" autoComplete="email" disabled placeholder="you@example.com" /></label><label className="form-field"><span>Password</span><input type="password" autoComplete="current-password" disabled placeholder="••••••••" /></label><button className="button button--primary" type="button" disabled>Sign in is unavailable</button><p className="form-help">No account data is being collected. <Link href="/register">Read about the scaffold</Link>.</p></section></main>;
}
