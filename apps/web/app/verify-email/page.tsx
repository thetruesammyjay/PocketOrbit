import Image from "next/image";
import Link from "next/link";
import { AccountActionForm } from "@/features/auth/account-action-form";

export default function VerifyEmailPage() {
  return (
    <main className="auth-layout">
      <section className="panel auth-card">
        <Link className="brand-lockup" href="/" aria-label="PocketOrbit home">
          <Image className="brand-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} priority />
        </Link>
        <h1>Verify your email</h1>
        <p className="muted">Use the link in your inbox, or request a fresh one.</p>
        <AccountActionForm mode="verify" />
      </section>
    </main>
  );
}
