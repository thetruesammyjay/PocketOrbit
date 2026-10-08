"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";

import { API_BASE_PATH } from "@/lib/api-base-path";

export function DeleteAccountForm() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    if (confirmation !== "DELETE") {
      setMessage("Type DELETE to confirm account removal.");
      return;
    }

    setBusy(true);
    try {
      const response = await fetch(`${API_BASE_PATH}/auth/account/delete`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });
      if (!response.ok) {
        const result = await response.json().catch(() => ({}));
        throw new Error(typeof result.detail === "string" ? result.detail : "The account could not be deleted.");
      }
      router.replace("/");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The account service could not be reached.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <label className="form-field"><span>Current password</span><input type="password" autoComplete="current-password" minLength={12} maxLength={1024} required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      <label className="form-field"><span>Type DELETE to confirm</span><input value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="off" required /></label>
      {message && <p className="form-message" role="alert">{message}</p>}
      <button className="button button--secondary auth-submit" type="submit" disabled={busy || confirmation !== "DELETE"}>{busy ? "Deleting account…" : "Delete account and saved data"}</button>
    </form>
  );
}
