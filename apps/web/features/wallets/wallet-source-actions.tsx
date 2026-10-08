"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { API_BASE_PATH } from "@/lib/api-base-path";

type WalletSourceActionsProps = {
  portfolioId: string;
  sourceId: string;
  sourceName: string;
};

export function WalletSourceActions({
  portfolioId,
  sourceId,
  sourceName
}: WalletSourceActionsProps) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  async function syncWallet() {
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/sources/${encodeURIComponent(sourceId)}/sync`, {
        method: "POST",
        credentials: "include"
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "The wallet could not be refreshed.");
      setMessage(`Updated ${payload.balances?.length ?? 0} balances. Quality: ${String(payload.quality ?? "needs_review").replaceAll("_", " ")}.`);
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The wallet could not be refreshed.");
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  async function removeWallet() {
    if (!window.confirm(`Remove ${sourceName} and its saved wallet snapshots from this portfolio?`)) return;
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/sources/${encodeURIComponent(sourceId)}`, {
        method: "DELETE",
        credentials: "include"
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(typeof payload.detail === "string" ? payload.detail : "The wallet could not be removed.");
      }
      setMessage("Wallet and its saved snapshots were removed.");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The wallet could not be removed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="wallet-source-actions">
      <button className="button button--secondary" type="button" disabled={busy} onClick={() => void syncWallet()}>
        {busy ? "Working…" : "Refresh wallet"}
      </button>
      <button className="button button--quiet" type="button" disabled={busy} onClick={() => void removeWallet()}>
        Remove
      </button>
      {message && <p className="form-help" role="status">{message}</p>}
    </div>
  );
}
