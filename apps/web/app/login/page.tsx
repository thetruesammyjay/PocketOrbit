import Link from "next/link";
import { AuthForm } from "@/features/auth/auth-form";

export default function LoginPage() {
  return <main className="auth-layout"><section className="panel auth-card"><Link className="brand-lockup" href="/"><span className="brand-mark">PO</span><span>PocketOrbit</span></Link><h1>Sign in</h1><p className="muted">Return to your saved portfolios and connected sources.</p><AuthForm mode="login" /><p className="form-help">Prefer the sample? <Link href="/app">Explore without signing in</Link>.</p></section></main>;
}
