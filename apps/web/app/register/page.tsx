import Link from "next/link";
import { AuthForm } from "@/features/auth/auth-form";

export default function RegisterPage() {
  return <main className="auth-layout"><section className="panel auth-card"><Link className="brand-lockup" href="/"><span className="brand-mark">PO</span><span>PocketOrbit</span></Link><h1>Create account</h1><p className="muted">Save your wallets, imports, and portfolio history in one private account.</p><AuthForm mode="register" /><p className="form-help">You can explore the sample portfolio without an account. <Link href="/app">Open demo</Link>.</p></section></main>;
}
