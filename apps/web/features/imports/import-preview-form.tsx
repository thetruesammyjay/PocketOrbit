"use client";

import { useState } from "react";
import type { FormEvent } from "react";

type Preview = { filename: string; columns: string[]; rowsReceived: number; preview: Record<string, string | null>[]; warnings: string[]; recordsAdded: boolean };

export function ImportPreviewForm() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function handlePreview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPreview(null);
    if (!file) {
      setMessage("Choose a CSV file first.");
      return;
    }
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
      setMessage("Set NEXT_PUBLIC_API_URL and start the API to preview a file.");
      return;
    }
    setBusy(true);
    setMessage("");
    const body = new FormData();
    body.append("file", file);
    try {
      const response = await fetch(`${apiUrl.replace(/\/$/, "")}/imports/preview`, { method: "POST", body });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "The file could not be previewed.");
      setPreview(result as Preview);
      setMessage("Preview ready. No records were saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The file could not be previewed.");
    } finally {
      setBusy(false);
    }
  }

  return <section className="panel content-panel">
    <form onSubmit={handlePreview}>
      <div className="form-field"><label htmlFor="exchange-file">Choose a CSV file</label><input id="exchange-file" type="file" accept=".csv,text/csv" onChange={(event) => { setFile(event.target.files?.[0] ?? null); setPreview(null); setMessage(""); }} /><span className="form-help">Up to 5 MB. This preview reads the header and first five rows only.</span></div>
      <button className="button button--primary" type="submit" disabled={busy}>{busy ? "Reading preview…" : "Preview file"}</button>
      {message && <p className="form-help" role="status">{message}</p>}
    </form>
    {preview && <div className="preview-box" aria-live="polite"><strong>{preview.filename}</strong><br />{preview.rowsReceived} rows · Columns: {preview.columns.join(", ") || "none found"}<br />{preview.warnings.join(" ")}<br /><strong>Records added: No</strong></div>}
  </section>;
}
