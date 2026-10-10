import Image from "next/image";
import Link from "next/link";
import { AuthForm } from "@/features/auth/auth-form";

export default function LoginPage() {
  return (
    <main className="auth-layout">
      <section className="panel auth-card">
        <Link className="brand-lockup" href="/" aria-label="PocketOrbit home">
          <Image className="brand-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} priority />
        </Link>
        <h1>Sign in</h1>
        <p className="muted">Return to your saved portfolios and connected sources.</p>
        <AuthForm mode="login" />
        <p className="form-help">Prefer the sample? <Link href="/app">Explore without signing in</Link>.</p>
      </section>
    </main>
  );
}
