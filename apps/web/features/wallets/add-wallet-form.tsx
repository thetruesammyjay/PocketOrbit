"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { WalletNetworkId, WalletSyncResponse } from "@pocketorbit/types";

import { API_BASE_PATH } from "@/lib/api-base-path";

type PortfolioOption = { id: string; name: string; reportingCurrency: string };
type NetworkOption = { id: WalletNetworkId; name: string; configured: boolean; coverage: string };

export function AddWalletForm() {
  const router = useRouter();
  const [portfolio, setPortfolio] = useState<PortfolioOption | null>(null);
  const [networks, setNetworks] = useState<NetworkOption[]>([]);
  const [network, setNetwork] = useState<WalletNetworkId | "">("");
  const [name, setName] = useState("Public wallet");
  const [address, setAddress] = useState("");
  const [result, setResult] = useState<WalletSyncResponse | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [signedIn, setSignedIn] = useState<boolean | null>(null);

  useEffect(() => {
    void Promise.all([
      fetch(`${API_BASE_PATH}/auth/me`, { credentials: "include", cache: "no-store" }),
      fetch(`${API_BASE_PATH}/wallets/capabilities`, { cache: "no-store" })
    ]).then(async ([authResponse, capabilityResponse]) => {
      setSignedIn(authResponse.ok);
      if (authResponse.ok) {
        const portfolioResponse = await fetch(`${API_BASE_PATH}/portfolios`, { credentials: "include", cache: "no-store" });
        if (portfolioResponse.ok) {
          const items = (await portfolioResponse.json()) as PortfolioOption[];
          setPortfolio(items[0] ?? null);
        }
      }
      if (capabilityResponse.ok) {
        const payload = (await capabilityResponse.json()) as { networks: NetworkOption[] };
        setNetworks(payload.networks.filter((item) => item.configured));
      }
    }).catch(() => setMessage("PocketOrbit could not reach the API. Start the API and try again."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setResult(null);
    if (!portfolio || !network) {
      setMessage("Choose a configured network and sign in before adding a wallet.");
      return;
    }
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolio.id)}/sources/wallets`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, network, address })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "The wallet could not be synced.");
      setResult(payload as WalletSyncResponse);
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The wallet could not be synced.");
    } finally {
      setBusy(false);
    }
  }

  if (signedIn === false) {
    return <section className="panel content-panel wallet-connect-card"><h2>Sign in to save this wallet</h2><p>Wallet snapshots belong to your account so they can appear in your portfolio history.</p><Link className="button button--primary" href="/login">Sign in</Link></section>;
  }

  return (
    <section className="panel content-panel wallet-connect-card">
      <form onSubmit={handleSubmit}>
        <div className="form-field"><label htmlFor="wallet-name">Name for this wallet</label><input id="wallet-name" required maxLength={160} value={name} onChange={(event) => setName(event.target.value)} /></div>
        <div className="form-field"><label htmlFor="network">Network</label><select id="network" required value={network} onChange={(event) => setNetwork(event.target.value as WalletNetworkId)}><option value="">Choose a configured network</option>{networks.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><span className="form-help">Only networks configured by the API are shown.</span></div>
        <div className="form-field"><label htmlFor="wallet-address">Public address</label><input id="wallet-address" type="text" required maxLength={64} autoCapitalize="off" autoCorrect="off" spellCheck={false} value={address} onChange={(event) => setAddress(event.target.value)} placeholder={network === "solana" ? "Solana public address" : "0x…"} /><span className="form-help">PocketOrbit reads public data. Never enter a seed phrase or private key.</span></div>
        {message && <p className="form-message" role="alert">{message}</p>}
        <button className="button button--primary" type="submit" disabled={busy || signedIn === null || !portfolio || networks.length === 0}>{busy ? "Reading wallet…" : "Add and sync wallet"}</button>
        {signedIn && !portfolio && <p className="form-help">No portfolio is available for this account. Refresh after the API is ready.</p>}
        {networks.length === 0 && signedIn && <p className="form-help">No wallet RPC is configured on the API yet.</p>}
      </form>
      {result && <div className="wallet-sync-result" role="status"><div><strong>{result.isLive ? "Wallet saved and synced" : "Wallet saved; live sync needs attention"}</strong><span>{result.isLive ? `${result.balances.length} balances · ${result.quality.replaceAll("_", " ")}` : "No balances were read yet."}</span></div><p>{result.isLive ? `Known value: ${result.totalValue === null ? "Partial data" : new Intl.NumberFormat("en-US", { style: "currency", currency: result.quoteCurrency }).format(Number(result.totalValue))}` : "You can retry the sync from your saved sources."}</p>{result.warnings.length > 0 && <ul>{result.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>}<Link className="text-link" href={result.isLive ? "/app" : "/app/sources"}>{result.isLive ? "View portfolio" : "Review saved source"}</Link></div>}
    </section>
  );
}
