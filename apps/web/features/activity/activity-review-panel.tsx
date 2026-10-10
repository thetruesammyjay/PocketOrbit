"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { PortfolioActivity } from "@pocketorbit/types";

import { ActivityList } from "./activity-list";
import { API_BASE_PATH } from "@/lib/api-base-path";

type TransferMatch = {
  id: string;
  assetSymbol: string;
  quantitySent: string;
  quantityReceived: string;
  outgoingSource: string;
  incomingSource: string;
  occurredAt: string;
  confidence: number;
  rationale: string;
  status: "suggested" | "matched" | "rejected";
};

export function ActivityReviewPanel({
  portfolioId,
  items
}: {
  portfolioId: string;
  items: PortfolioActivity[];
}) {
  const router = useRouter();
  const [activityItems, setActivityItems] = useState(items);
  const [hasMoreActivity, setHasMoreActivity] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [matches, setMatches] = useState<TransferMatch[]>([]);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  const refreshMatches = useCallback(async () => {
    const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/transfers`, {
      credentials: "include",
      cache: "no-store"
    });
    if (response.ok) setMatches((await response.json()) as TransferMatch[]);
  }, [portfolioId]);

  const refreshActivity = useCallback(async () => {
    const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/activity?offset=0&limit=100`, {
      credentials: "include",
      cache: "no-store"
    });
    if (response.ok) {
      const nextItems = (await response.json()) as PortfolioActivity[];
      setActivityItems(nextItems);
      setHasMoreActivity(nextItems.length === 100);
    }
  }, [portfolioId]);

  useEffect(() => {
    void refreshMatches();
    void refreshActivity();
  }, [refreshActivity, refreshMatches]);

  async function loadOlderActivity() {
    setLoadingMore(true);
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/activity?offset=${activityItems.length}&limit=100`, {
        credentials: "include",
        cache: "no-store"
      });
      if (!response.ok) return;
      const olderItems = (await response.json()) as PortfolioActivity[];
      setActivityItems((current) => [...current, ...olderItems]);
      setHasMoreActivity(olderItems.length === 100);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Older activity could not be loaded.");
    } finally {
      setLoadingMore(false);
    }
  }

  async function reviewActivity(id: string, accepted: boolean) {
    setBusyId(id);
    setMessage("");
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/activity/${encodeURIComponent(id)}/review`, {
        method: "POST",
        credentials: "include",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ accepted })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "The record could not be reviewed.");
      await refreshMatches();
      await refreshActivity();
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The record could not be reviewed.");
    } finally {
      setBusyId(null);
    }
  }

  async function reviewTransfer(id: string, accepted: boolean) {
    setBusyId(id);
    setMessage("");
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/transfers/${encodeURIComponent(id)}/review`, {
        method: "POST",
        credentials: "include",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ accepted })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "The transfer could not be reviewed.");
      await refreshMatches();
      await refreshActivity();
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The transfer could not be reviewed.");
    } finally {
      setBusyId(null);
    }
  }

  const reviewable = activityItems.filter((item) => item.status === "needs_review");
  const suggested = matches.filter((match) => match.status === "suggested");
  const resolved = matches.filter((match) => match.status !== "suggested");

  return <div className="activity-review-stack">
    {message && <p className="form-help" role="alert">{message}</p>}
    <section className="panel">
      <div className="panel-heading"><div><h2>Recent records</h2><p>CSV records remain user-provided. Review them before they affect performance calculations.</p></div></div>
      {activityItems.length ? <ActivityList items={activityItems} /> : <p className="empty-panel-copy">Transaction records from imported files will appear here.</p>}
      {hasMoreActivity && <div className="activity-load-more"><button className="button button--secondary" disabled={loadingMore} onClick={() => void loadOlderActivity()}>{loadingMore ? "Loading…" : "Load older records"}</button></div>}
      {reviewable.length > 0 && <div className="activity-review-list"><h3>Needs your review</h3>{reviewable.map((item) => <div className="activity-review-row" key={item.id}><span><strong>{item.kind} {item.assetSymbol}</strong><small>{item.quantity} {item.assetSymbol} · {item.sourceName} · {new Date(item.occurredAt).toLocaleString()}</small>{item.transactionHash && <small>Transaction hash: {item.transactionHash}</small>}</span><div className="activity-review-actions"><button className="button button--secondary" disabled={busyId !== null} onClick={() => void reviewActivity(item.id, false)}>Reject</button><button className="button button--primary" disabled={busyId !== null} onClick={() => void reviewActivity(item.id, true)}>{busyId === item.id ? "Saving…" : "Mark reviewed"}</button></div></div>)}</div>}
    </section>

    <section className="panel">
      <div className="panel-heading"><div><h2>Possible internal transfers</h2><p>Suggestions use exact asset identity, amounts, timestamps, and transaction hashes when available. Confirm only records that represent your own movement.</p></div></div>
      {suggested.length === 0 && <p className="empty-panel-copy">No transfer suggestions are waiting for review. Suggestions appear after both activity records are marked reviewed.</p>}
      {suggested.map((match) => <div className="transfer-match-row" key={match.id}><div><strong>{match.assetSymbol}: {match.quantitySent} sent · {match.quantityReceived} received</strong><p>{match.outgoingSource} → {match.incomingSource} · {new Date(match.occurredAt).toLocaleString()}</p><p>{match.rationale}</p><small>Match confidence: {Math.round(match.confidence * 100)}% · review required</small></div><div className="activity-review-actions"><button className="button button--secondary" disabled={busyId !== null} onClick={() => void reviewTransfer(match.id, false)}>Not a transfer</button><button className="button button--primary" disabled={busyId !== null} onClick={() => void reviewTransfer(match.id, true)}>{busyId === match.id ? "Saving…" : "Confirm transfer"}</button></div></div>)}
      {resolved.length > 0 && <details className="transfer-match-history"><summary>Reviewed suggestions ({resolved.length})</summary>{resolved.map((match) => <p key={match.id}>{match.assetSymbol} · {match.outgoingSource} → {match.incomingSource} · {match.status}</p>)}</details>}
    </section>
  </div>;
}
