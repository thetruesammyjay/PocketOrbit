"use client";

import Link from "next/link";

type AppErrorProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function AppError({ reset }: AppErrorProps) {
  return (
    <section className="panel content-panel" role="alert">
      <span className="eyebrow">Portfolio unavailable</span>
      <h1 className="page-title">We could not load your saved portfolio.</h1>
      <p>
        Your account data is unavailable right now. We will not show sample values as if they were
        yours. Try again in a moment.
      </p>
      <div className="button-row">
        <button className="button button--primary" type="button" onClick={reset}>
          Try again
        </button>
        <Link className="button button--secondary" href="/">
          Go to PocketOrbit home
        </Link>
      </div>
    </section>
  );
}
