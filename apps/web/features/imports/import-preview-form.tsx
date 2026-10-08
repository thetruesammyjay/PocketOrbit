"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { ChangeEvent } from "react";

import { API_BASE_PATH } from "@/lib/api-base-path";

type ColumnField = "occurred_at" | "asset" | "quantity" | "kind" | "network" | "contract_address" | "transaction_id";
type ImportMode = "transactions" | "balances";
type Mapping = Record<ColumnField, string>;
type Preview = {
  filename: string;
  columns: string[];
  rowsReceived: number;
  preview: Record<string, string | null>[];
  warnings: string[];
  suggestedMapping: Record<ColumnField, string | null>;
};
type ImportResult = {
  importId: string;
  sourceId: string;
  filename: string;
  rowsReceived: number;
  rowsAccepted: number;
  rowsRejected: number;
  unmatchedAssets: string[];
  warnings: string[];
  rejectedRows: { row: number; reason: string }[];
};
type PortfolioOption = { id: string };
type BalanceSourceOption = { id: string; name: string; kind: string };
type ImportJob = {
  id: string;
  filename: string;
  status: string;
  rowsReceived: number;
  rowsAccepted: number;
  rowsRejected: number;
  createdAt: string;
};

const fields: { key: ColumnField; label: string; required: boolean; help: string }[] = [
  { key: "occurred_at", label: "Transaction date", required: true, help: "When the transaction happened." },
  { key: "asset", label: "Asset symbol", required: true, help: "For example, BTC or SOL. Ticker-only assets stay unmatched." },
  { key: "quantity", label: "Amount", required: true, help: "Use a type column for unsigned amounts, or map signed amounts." },
  { key: "kind", label: "Transaction type", required: false, help: "Map buys, sells, deposits, withdrawals, sends, or receives." },
  { key: "network", label: "Network", required: false, help: "Map this when the file identifies a supported network." },
  { key: "contract_address", label: "Token contract or mint", required: false, help: "Maps a token to its exact network identity." },
  { key: "transaction_id", label: "Transaction ID", required: false, help: "Used to identify duplicate rows in the file." }
];

const emptyMapping: Mapping = {
  occurred_at: "",
  asset: "",
  quantity: "",
  kind: "",
  network: "",
  contract_address: "",
  transaction_id: ""
};

async function loadBalanceSources(portfolioId: string): Promise<BalanceSourceOption[]> {
  const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/sources`, {
    credentials: "include",
    cache: "no-store"
  });
  if (!response.ok) return [];
  const sources = (await response.json()) as BalanceSourceOption[];
  return sources.filter((source) => source.kind === "exchange_balance_import");
}

export function ImportPreviewForm() {
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<ImportMode>("transactions");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [mapping, setMapping] = useState<Mapping>(emptyMapping);
  const [portfolioId, setPortfolioId] = useState("");
  const [balanceSources, setBalanceSources] = useState<BalanceSourceOption[]>([]);
  const [balanceSourceId, setBalanceSourceId] = useState("");
  const [balanceSourceName, setBalanceSourceName] = useState("");
  const [signedIn, setSignedIn] = useState<boolean | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [imports, setImports] = useState<ImportJob[]>([]);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void fetch(`${API_BASE_PATH}/auth/me`, { credentials: "include", cache: "no-store" })
      .then(async (response) => {
        setSignedIn(response.ok);
        if (!response.ok) return;
        const portfolioResponse = await fetch(`${API_BASE_PATH}/portfolios`, { credentials: "include", cache: "no-store" });
        if (portfolioResponse.ok) {
          const portfolios = (await portfolioResponse.json()) as PortfolioOption[];
          const firstPortfolio = portfolios[0];
          setPortfolioId(firstPortfolio?.id ?? "");
          if (firstPortfolio) {
            const importResponse = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(firstPortfolio.id)}/imports`, { credentials: "include", cache: "no-store" });
            if (importResponse.ok) setImports((await importResponse.json()) as ImportJob[]);
            setBalanceSources(await loadBalanceSources(firstPortfolio.id));
          }
        }
      })
      .catch(() => setMessage("PocketOrbit could not reach the API. Start the API and try again."));
  }, []);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null;
    setFile(nextFile);
    setBalanceSourceName(nextFile?.name ?? "");
    setPreview(null);
    setResult(null);
    setMessage("");
  }

  async function handlePreview() {
    setPreview(null);
    setResult(null);
    setMessage("");
    if (!file) {
      setMessage("Choose a CSV file first.");
      return;
    }
    setBusy(true);
    const body = new FormData();
    body.append("file", file);
    try {
      const response = await fetch(`${API_BASE_PATH}/imports/preview`, { method: "POST", body });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "The file could not be previewed.");
      const nextPreview = payload as Preview;
      setPreview(nextPreview);
      setMapping({
        occurred_at: nextPreview.suggestedMapping.occurred_at ?? "",
        asset: nextPreview.suggestedMapping.asset ?? "",
        quantity: nextPreview.suggestedMapping.quantity ?? "",
        kind: nextPreview.suggestedMapping.kind ?? "",
        network: nextPreview.suggestedMapping.network ?? "",
        contract_address: nextPreview.suggestedMapping.contract_address ?? "",
        transaction_id: nextPreview.suggestedMapping.transaction_id ?? ""
      });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The file could not be previewed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleImport() {
    setMessage("");
    setResult(null);
    if (!file || !preview || !portfolioId) {
      setMessage("Sign in, choose a file, and preview it before importing.");
      return;
    }
    if (!mapping.asset || !mapping.quantity || (mode === "transactions" && !mapping.occurred_at)) {
      setMessage(mode === "transactions"
        ? "Choose a date, asset, and amount column before importing."
        : "Choose an asset and balance column before importing.");
      return;
    }
    setBusy(true);
    const body = new FormData();
    body.append("file", file);
    body.append("mode", mode);
    if (mode === "balances") {
      if (balanceSourceId) {
        body.append("balanceSourceId", balanceSourceId);
      } else {
        body.append("balanceSourceName", balanceSourceName.trim());
      }
    }
    body.append("mapping", JSON.stringify(mode === "transactions" ? {
      occurredAt: mapping.occurred_at,
      asset: mapping.asset,
      quantity: mapping.quantity,
      kind: mapping.kind || null,
      network: mapping.network || null,
      contractAddress: mapping.contract_address || null,
      transactionId: mapping.transaction_id || null
    } : {
      asset: mapping.asset,
      quantity: mapping.quantity,
      network: mapping.network || null,
      contractAddress: mapping.contract_address || null
    }));
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/imports`, {
        method: "POST",
        credentials: "include",
        body
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "The file could not be imported.");
      setResult(payload as ImportResult);
      await refreshImports();
      await refreshBalanceSources();
      setMessage(mode === "balances"
        ? "Balance statement saved for review. The original file was not stored."
        : "Transaction history saved. The original file was not stored.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The file could not be imported.");
    } finally {
      setBusy(false);
    }
  }

  async function refreshImports() {
    if (!portfolioId) return;
    const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/imports`, {
      credentials: "include",
      cache: "no-store"
    });
    if (response.ok) setImports((await response.json()) as ImportJob[]);
  }

  async function refreshBalanceSources(id = portfolioId) {
    if (!id) return;
    const sources = await loadBalanceSources(id);
    setBalanceSources(sources);
    setBalanceSourceId((current) => sources.some((source) => source.id === current) ? current : "");
  }

  async function removeImport(importId: string, filename: string) {
    if (!portfolioId || !window.confirm(`Remove ${filename} and its imported rows and balances from this portfolio?`)) return;
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/imports/${encodeURIComponent(importId)}`, {
        method: "DELETE",
        credentials: "include"
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(typeof payload.detail === "string" ? payload.detail : "The import could not be removed.");
      }
      if (result?.importId === importId) setResult(null);
      await refreshImports();
      await refreshBalanceSources();
      setMessage("Import and its saved rows were removed.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The import could not be removed.");
    } finally {
      setBusy(false);
    }
  }

  if (signedIn === false) {
    return <section className="panel content-panel"><h2>Sign in to save an import</h2><p>Validated transaction records or balance statements are stored in your portfolio. The uploaded file itself is discarded after processing.</p><Link className="button button--primary" href="/login">Sign in</Link></section>;
  }

  return <section className="panel content-panel">
    <div className="form-field"><label htmlFor="import-mode">What does this CSV contain?</label><select id="import-mode" value={mode} onChange={(event) => setMode(event.target.value as ImportMode)}><option value="transactions">Transaction history</option><option value="balances">Current account balances</option></select><span className="form-help">Balance statements show the quantities in your exchange account. Transaction history is saved as activity and does not establish current balances by itself.</span></div>
    {mode === "balances" && <>
      <div className="form-field"><label htmlFor="balance-source">Account source</label><select id="balance-source" value={balanceSourceId} onChange={(event) => setBalanceSourceId(event.target.value)}><option value="">Create a new account source</option>{balanceSources.map((source) => <option key={source.id} value={source.id}>{source.name}</option>)}</select><span className="form-help">Select the same source when importing an updated statement. PocketOrbit will keep its snapshot history without counting old and new balances together.</span></div>
      {!balanceSourceId && <div className="form-field"><label htmlFor="balance-source-name">Exchange or account name</label><input id="balance-source-name" required maxLength={160} value={balanceSourceName} onChange={(event) => setBalanceSourceName(event.target.value)} placeholder="For example, Coinbase main account" /></div>}
    </>}
    <div className="form-field"><label htmlFor="exchange-file">Choose a CSV file</label><input id="exchange-file" type="file" accept=".csv,text/csv" onChange={handleFileChange} /><span className="form-help">Up to 5 MB and 20,000 rows. PocketOrbit saves normalized records, not the uploaded file.</span></div>
    <button className="button button--secondary" type="button" onClick={() => void handlePreview()} disabled={busy}>{busy ? "Reading file…" : "Preview and map columns"}</button>
    {message && <p className="form-help" role="status">{message}</p>}

    {preview && <div className="csv-import-review" aria-live="polite">
      <div className="panel-heading"><div><h2>Check the columns</h2><p>{preview.filename} · {preview.rowsReceived.toLocaleString()} rows</p></div></div>
      <div className="csv-mapping-grid">
        {fields.filter((field) => mode === "transactions" || !["occurred_at", "kind", "transaction_id"].includes(field.key)).map((field) => {
          const required = mode === "transactions"
            ? field.key === "occurred_at" || field.key === "asset" || field.key === "quantity"
            : field.key === "asset" || field.key === "quantity";
          const label = mode === "balances" && field.key === "quantity" ? "Current balance" : field.label;
          return <div className="form-field" key={field.key}>
          <label htmlFor={`mapping-${field.key}`}>{label}{required ? " *" : ""}</label>
          <select id={`mapping-${field.key}`} required={required} value={mapping[field.key]} onChange={(event) => setMapping((current) => ({ ...current, [field.key]: event.target.value }))}>
            <option value="">{required ? "Choose a column" : "Skip this field"}</option>
            {preview.columns.map((column) => <option key={column} value={column}>{column}</option>)}
          </select>
          <span className="form-help">{mode === "balances" && field.key === "quantity" ? "The current amount held in this account. Negative values are rejected." : field.help}</span>
        </div>})}
      </div>
      <div className="csv-sample-rows"><strong>First rows</strong><div className="table-wrap"><table className="data-table"><thead><tr>{preview.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{preview.preview.map((row, index) => <tr key={index}>{preview.columns.map((column) => <td key={column}>{row[column] ?? ""}</td>)}</tr>)}</tbody></table></div></div>
      {preview.warnings.map((warning) => <p className="form-help" key={warning}>{warning}</p>)}
      <button className="button button--primary" type="button" onClick={() => void handleImport()} disabled={busy || !portfolioId || (mode === "balances" && !balanceSourceId && !balanceSourceName.trim())}>{busy ? "Saving import…" : mode === "balances" ? "Import current balances" : "Import transactions"}</button>
    </div>}

    {result && <div className="wallet-sync-result" role="status"><div><strong>Import saved</strong><span>{result.filename}</span></div><p>{result.rowsAccepted} accepted · {result.rowsRejected} rejected</p>{result.unmatchedAssets.length > 0 && <p>Needs asset matching: {result.unmatchedAssets.join(", ")}</p>}{result.rejectedRows.length > 0 && <details><summary>Review rejected rows</summary><ul>{result.rejectedRows.map((row) => <li key={row.row}>Row {row.row}: {row.reason}</li>)}</ul></details>}<ul>{result.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul><Link className="text-link" href="/app">View portfolio</Link><button className="button button--quiet" type="button" disabled={busy} onClick={() => void removeImport(result.importId, result.filename)}>Remove this import</button></div>}
    {signedIn && imports.length > 0 && <div className="import-history"><div className="panel-heading"><div><h2>Saved imports</h2><p>Remove an import to remove its saved records and allow a corrected re-import.</p></div></div>{imports.map((item) => <div className="import-history-row" key={item.id}><span><strong>{item.filename}</strong><small>{new Date(item.createdAt).toLocaleString()} · {item.rowsAccepted}/{item.rowsReceived} rows saved · {item.status.replaceAll("_", " ")}</small></span><button className="button button--quiet" type="button" disabled={busy} onClick={() => void removeImport(item.id, item.filename)}>Remove</button></div>)}</div>}
  </section>;
}
