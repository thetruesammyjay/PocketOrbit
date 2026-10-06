import Link from "next/link";

export default function RegisterPage() {
  return <main className="auth-layout"><section className="panel auth-card"><Link className="brand-lockup" href="/"><span className="brand-mark">PO</span><span>PocketOrbit</span></Link><h1>Create account</h1><p className="muted">Registration is not configured in this scaffold.</p><label className="form-field"><span>Email</span><input type="email" autoComplete="email" disabled placeholder="you@example.com" /></label><label className="form-field"><span>Password</span><input type="password" autoComplete="new-password" disabled placeholder="At least 12 characters" /></label><button className="button button--primary" type="button" disabled>Create account is unavailable</button><p className="form-help">You can explore the sample portfolio without an account. <Link href="/app">Open demo</Link>.</p></section></main>;
}
