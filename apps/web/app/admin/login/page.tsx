import Image from "next/image";
import Link from "next/link";

import { AuthForm } from "@/features/auth/auth-form";

type AdminLoginPageProps = {
  searchParams: Promise<{ reason?: string | string[] }>;
};

export default async function AdminLoginPage({ searchParams }: AdminLoginPageProps) {
  const params = await searchParams;
  const accessDenied = params.reason === "not-allowed";

  return (
    <main className="auth-layout">
      <section className="panel auth-card">
        <Link className="brand-lockup" href="/" aria-label="PocketOrbit home">
          <Image
            className="brand-logo"
            src="/brand/PocketOrbit-Logo.png"
            alt="PocketOrbit"
            width={2034}
            height={427}
            priority
          />
        </Link>
        <h1>Admin sign in</h1>
        <p className="muted">Use an email on the admin allowlist and the deployment admin password.</p>
        {accessDenied && (
          <p className="form-message" role="alert">
            This session does not have administrator access. Enter the deployment admin credentials below.
          </p>
        )}
        <AuthForm mode="admin" redirectTo="/admin" />
        <p className="form-help">
          <Link href="/login">Sign in to a regular account</Link>{" · "}<Link href="/">Back to PocketOrbit</Link>
        </p>
      </section>
    </main>
  );
}
