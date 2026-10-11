import Image from "next/image";
import Link from "next/link";

export default function VerifyEmailPage() {
  return (
    <main className="auth-layout">
      <section className="panel auth-card">
        <Link className="brand-lockup" href="/" aria-label="PocketOrbit home">
          <Image className="brand-logo" src="/brand/PocketOrbit-Logo.png" alt="PocketOrbit" width={2034} height={427} priority />
        </Link>
        <h1>Email confirmation is not required</h1>
        <p className="muted">You can use your PocketOrbit account with your email and password. Email delivery is only needed for password recovery.</p>
        <p className="form-help"><Link href="/login">Sign in</Link> · <Link href="/register">Create an account</Link></p>
      </section>
    </main>
  );
}
