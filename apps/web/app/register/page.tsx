import Image from "next/image";
import Link from "next/link";
import { AuthForm } from "@/features/auth/auth-form";

export default function RegisterPage() {
  return (
    <main className="auth-layout">
      <section className="panel auth-card">
        <Link className="brand-lockup" href="/" aria-label="PocketOrbit home">
          <Image className="brand-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} priority />
        </Link>
        <h1>Create account</h1>
        <p className="muted">Save your wallets, imports, and portfolio history in one private account.</p>
        <AuthForm mode="register" />
        <p className="form-help">You can explore the sample portfolio without an account. <Link href="/app">Open demo</Link>.</p>
      </section>
    </main>
  );
}
