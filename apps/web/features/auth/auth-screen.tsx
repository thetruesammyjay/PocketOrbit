import Image from "next/image";
import Link from "next/link";

import { AuthForm } from "@/features/auth/auth-form";

type AuthScreenProps = {
  mode: "login" | "register";
};

export function AuthScreen({ mode }: AuthScreenProps) {
  const isRegister = mode === "register";

  return (
    <main className="auth-screen">
      <section className="auth-story" aria-labelledby="auth-story-title">
        <Link className="auth-screen-brand" href="/" aria-label="PocketOrbit home">
          <Image
            className="auth-screen-logo"
            src="/brand/PocketOrbit-Logo.png"
            alt="PocketOrbit"
            width={2034}
            height={427}
            priority
          />
        </Link>

        <div className="auth-story-content">
          <p className="auth-readonly-label">
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <path d="M10 2.5 16 5v4.2c0 3.6-2.5 6.4-6 8.3-3.5-1.9-6-4.7-6-8.3V5l6-2.5Z" />
              <path d="m7.3 9.8 1.8 1.8 3.7-3.8" />
            </svg>
            Read-only by design
          </p>
          <h1 id="auth-story-title" className="auth-story-title">
            Your crypto, in one clear view.
          </h1>
          <p className="auth-story-description">
            {isRegister
              ? "Bring public wallets and exchange files together. See what you own and where each number came from."
              : "Your saved wallets and imports, together in one private portfolio. Every number keeps its source in sight."}
          </p>
        </div>

        <div className="auth-visual" aria-hidden="true">
          <span className="auth-orbit-loop auth-orbit-loop--outer" />
          <span className="auth-orbit-loop auth-orbit-loop--inner" />

          <div className="auth-source-card auth-source-card--wallet">
            <span className="auth-source-icon auth-source-icon--mint">
              <svg viewBox="0 0 24 24">
                <path d="M4 7.5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h12" />
                <path d="M16 12h4M6 8V6" />
                <circle cx="16" cy="12" r=".7" />
              </svg>
            </span>
            <span>
              <strong>Public wallet</strong>
              <small>Read-only access</small>
            </span>
          </div>

          <div className="auth-source-card auth-source-card--file">
            <span className="auth-source-icon auth-source-icon--violet">
              <svg viewBox="0 0 24 24">
                <path d="M6 3.5h8l4.5 4.6v12.4H6z" />
                <path d="M14 3.8v4.7h4.3M9 12h6M9 15.5h6" />
              </svg>
            </span>
            <span>
              <strong>Exchange file</strong>
              <small>CSV records</small>
            </span>
          </div>

          <div className="auth-portfolio-card">
            <div className="auth-portfolio-heading">
              <span className="auth-portfolio-mark" />
              <span>Portfolio overview</span>
              <span className="auth-sample-label">Sample view</span>
            </div>
            <strong className="auth-portfolio-title">Everything in its place.</strong>
            <p>Wallet balances and exchange records, gathered into one view.</p>
            <div className="auth-provenance-row">
              <span>Source</span>
              <strong>Shown on every balance</strong>
            </div>
            <div className="auth-provenance-row">
              <span>Updated</span>
              <strong>Time shown with each source</strong>
            </div>
          </div>

          <Image
            className="auth-orbit-mascot"
            src="/brand/PocketOrbit-Orbit.png"
            alt=""
            width={1112}
            height={971}
            priority
          />
        </div>

        <p className="auth-story-footnote">
          Your portfolio stays yours. PocketOrbit never asks for seed phrases or private keys.
        </p>
      </section>

      <section className="auth-form-side" aria-labelledby="auth-form-title">
        <div className="auth-form-card">
          <h2 id="auth-form-title">{isRegister ? "Create your account" : "Sign in"}</h2>
          <p className="auth-form-intro">
            {isRegister
              ? "Use your email and a password. You can add a wallet or file after you sign in."
              : "Sign in to open your saved portfolio and sources."}
          </p>
          <AuthForm mode={mode} />
          <p className="auth-demo-link">
            Want to look around first? <Link href="/app">Explore the sample portfolio</Link>.
          </p>
        </div>
      </section>
    </main>
  );
}
