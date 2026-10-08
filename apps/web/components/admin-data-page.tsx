import { Card } from "@pocketorbit/ui";
import Link from "next/link";
import { notFound } from "next/navigation";

import { PageHeading } from "@/components/page-heading";
import { getInternalApiUrl } from "@/lib/internal-api-url";
import { getServerSessionCookieHeader } from "@/lib/server-session-cookie";

export type AdminRow = Record<string, unknown>;

export type AdminColumn = {
  key: string;
  label: string;
};

export type AdminRouteProps = {
  searchParams: Promise<{ offset?: string | string[] }>;
};

export async function resolveAdminOffset(
  searchParams: AdminRouteProps["searchParams"]
): Promise<number> {
  const params = await searchParams;
  const rawOffset = Array.isArray(params.offset) ? params.offset[0] : params.offset;
  const offset = Number.parseInt(rawOffset ?? "0", 10);
  return Number.isSafeInteger(offset) && offset >= 0 ? Math.min(offset, 50_000) : 0;
}

export async function fetchAdminData(path: string): Promise<Record<string, unknown>> {
  const apiUrl = getInternalApiUrl();
  if (!apiUrl) throw new Error("Admin data is unavailable because API_INTERNAL_URL is missing.");

  const cookieHeader = await getServerSessionCookieHeader();
  if (!cookieHeader) notFound();
  const response = await fetch(`${apiUrl}/admin/${path}`, {
    cache: "no-store",
    headers: { cookie: cookieHeader },
    signal: AbortSignal.timeout(5000)
  });
  if (response.status === 401 || response.status === 403 || response.status === 404) notFound();
  if (!response.ok) throw new Error("Admin data could not be loaded. Try again shortly.");
  return (await response.json()) as Record<string, unknown>;
}

export function AdminDataTable({
  rows,
  columns,
  emptyMessage = "No records are available."
}: {
  rows: AdminRow[];
  columns: AdminColumn[];
  emptyMessage?: string;
}) {
  if (!rows.length) return <p className="empty-panel-copy">{emptyMessage}</p>;
  return (
    <div className="admin-table-wrap">
      <table className="admin-table">
        <thead>
          <tr>{columns.map((column) => <th key={column.key} scope="col">{column.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={String(row.id ?? `${index}`)}>
              {columns.map((column) => (
                <td key={column.key}>{formatAdminValue(row[column.key])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export async function AdminDataPage({
  title,
  description,
  endpoint,
  columns,
  collection = "items",
  offset = 0
}: {
  title: string;
  description: string;
  endpoint: string;
  columns: AdminColumn[];
  collection?: string;
  offset?: number;
}) {
  const pageSize = 50;
  const boundedOffset = Math.min(Math.max(0, offset), 50_000);
  const data = await fetchAdminData(`${endpoint}?offset=${boundedOffset}&limit=${pageSize}`);
  const value = data[collection];
  const rows = Array.isArray(value) ? value as AdminRow[] : [];
  const total = typeof data.total === "number" ? data.total : rows.length;
  const supportsPages = [
    "users",
    "portfolios",
    "imports",
    "sources",
    "assets",
    "jobs",
    "audit"
  ].includes(endpoint);
  const previousOffset = Math.max(0, boundedOffset - pageSize);
  const nextOffset = boundedOffset + rows.length;

  return (
    <>
      <PageHeading title={title} description={description} />
      <Card className="content-panel">
        <div className="panel-heading">
          <div>
            <h2>{total.toLocaleString()} records</h2>
            <p>Read-only operational data from the API database</p>
          </div>
        </div>
        <AdminDataTable rows={rows} columns={columns} />
        {supportsPages && total > pageSize && (
          <div className="admin-pagination">
            <span>
              {rows.length
                ? `${boundedOffset + 1}–${boundedOffset + rows.length} of ${total}`
                : "No records at this offset"}
            </span>
            <div>
              {boundedOffset > 0 && (
                <Link
                  className="button button--secondary"
                  href={`/admin/${endpoint}?offset=${previousOffset}`}
                >
                  Previous
                </Link>
              )}
              {nextOffset < total && (
                <Link
                  className="button button--secondary"
                  href={`/admin/${endpoint}?offset=${nextOffset}`}
                >
                  Next
                </Link>
              )}
            </div>
          </div>
        )}
      </Card>
    </>
  );
}

export function formatAdminValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "string" || typeof value === "number") return String(value);
  if (Array.isArray(value)) return value.map((item) => String(item)).join(", ");
  return JSON.stringify(value) ?? String(value);
}
