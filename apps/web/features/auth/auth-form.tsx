"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";

import { API_BASE_PATH } from "@/lib/api-base-path";

type AuthFormProps = {
  mode: "register" | "login";
  redirectTo?: "/app" | "/admin";
};

export function AuthForm({ mode, redirectTo = "/app" }: AuthFormProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    setSuccess(false);
    try {
      const response = await fetch(`${API_BASE_PATH}/auth/${mode}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = typeof result.detail === "string" ? result.detail : "Check your details and try again.";
        throw new Error(detail);
      }
      if (isRegister && result.verificationRequired === true) {
        setMessage(typeof result.message === "string" ? result.message : "Check your inbox to verify your account.");
        setSuccess(true);
        return;
      }
      router.replace(redirectTo);
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The account service could not be reached.");
    } finally {
      setBusy(false);
    }
  }

  const isRegister = mode === "register";
  return (
    <form onSubmit={handleSubmit}>
      <label className="form-field"><span>Email</span><input type="email" autoComplete="email" required maxLength={320} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>
      <label className="form-field"><span>Password</span><input type="password" autoComplete={isRegister ? "new-password" : "current-password"} required minLength={12} maxLength={1024} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={isRegister ? "At least 12 characters" : "Your password"} /></label>
      {isRegister && <p className="form-help">Use at least 12 characters. Your portfolio is saved to your account.</p>}
      {message && <p className="form-message" role={success ? "status" : "alert"}>{message}{success && <> <Link href="/verify-email">Resend verification</Link></>}</p>}
      <button className="button button--primary auth-submit" type="submit" disabled={busy}>{busy ? "Please wait…" : isRegister ? "Create account" : "Sign in"}</button>
      {!isRegister && <p className="form-help"><Link href="/forgot-password">Forgot your password?</Link> · <Link href="/verify-email">Verify your email</Link></p>}
      <p className="form-help">{isRegister ? "Already have an account? " : "New to PocketOrbit? "}<Link href={isRegister ? "/login" : "/register"}>{isRegister ? "Sign in" : "Create an account"}</Link></p>
    </form>
  );
}
