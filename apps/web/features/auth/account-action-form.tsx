"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

import { API_BASE_PATH } from "@/lib/api-base-path";

type ActionMode = "forgot" | "resend" | "verify" | "reset";

type AccountActionFormProps = { mode: ActionMode };

const endpointByMode: Record<ActionMode, string> = {
  forgot: "password/forgot",
  resend: "verification/resend",
  verify: "verification/confirm",
  reset: "password/reset"
};

export function AccountActionForm({ mode }: AccountActionFormProps) {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [tokenReady, setTokenReady] = useState(false);
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [busy, setBusy] = useState(false);
  const verificationStarted = useRef(false);

  useEffect(() => {
    const value = new URLSearchParams(window.location.hash.slice(1)).get("token") ?? "";
    setToken(value);
    setTokenReady(true);
  }, []);

  const submitAction = useCallback(async (body: Record<string, string>) => {
    setBusy(true);
    setMessage("");
    setSuccess(false);
    try {
      const endpoint = mode === "verify" && !body.token ? "verification/resend" : endpointByMode[mode];
      const response = await fetch(`${API_BASE_PATH}/auth/${endpoint}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(typeof result.detail === "string" ? result.detail : "The request could not be completed.");
      }
      setMessage(typeof result.message === "string" ? result.message : "Check your email for the next step.");
      setSuccess(true);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The account service could not be reached.");
    } finally {
      setBusy(false);
    }
  }, [mode]);

  useEffect(() => {
    if (mode !== "verify" || !token || verificationStarted.current) return;
    verificationStarted.current = true;
    void submitAction({ token });
  }, [mode, submitAction, token]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (mode === "forgot" || mode === "resend" || canRequestVerification) {
      void submitAction({ email });
      return;
    }
    if (mode === "reset") void submitAction({ token, password });
    if (mode === "verify" && token) void submitAction({ token });
  }

  const canRequestVerification = mode === "verify" && (!token || (Boolean(message) && !success));
  const asksForEmail = mode === "forgot" || mode === "resend" || canRequestVerification;
  const showSubmit = mode !== "verify" || canRequestVerification;

  return (
    <form onSubmit={handleSubmit}>
      {asksForEmail && <label className="form-field"><span>Email</span><input type="email" autoComplete="email" required maxLength={320} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>}
      {mode === "reset" && token && <label className="form-field"><span>New password</span><input type="password" autoComplete="new-password" required minLength={12} maxLength={1024} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 12 characters" /></label>}
      {mode === "verify" && token && !message && <p className="form-help">Verifying the email link…</p>}
      {mode === "reset" && tokenReady && !token && <p className="form-message" role="alert">This reset link is missing. <Link href="/forgot-password">Request a new link</Link>.</p>}
      {message && <p className="form-message" role={success ? "status" : "alert"}>{message}</p>}
      {showSubmit && (mode !== "reset" || (tokenReady && Boolean(token))) && <button className="button button--primary auth-submit" type="submit" disabled={busy}>{busy ? "Please wait…" : mode === "forgot" ? "Send reset link" : mode === "reset" ? "Update password" : "Send verification link"}</button>}
      {success && (mode === "verify" || mode === "reset") && <p className="form-help"><Link href="/login">Continue to sign in</Link></p>}
      <p className="form-help"><Link href="/login">Back to sign in</Link></p>
      {mode === "forgot" && <p className="form-help">If the email is registered, we will send a reset link.</p>}
    </form>
  );
}
