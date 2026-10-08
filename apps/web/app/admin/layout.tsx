import { notFound } from "next/navigation";
import type { ReactNode } from "react";

import { AdminShell } from "@/components/admin-shell";
import { getInternalApiUrl } from "@/lib/internal-api-url";
import { getServerSessionCookieHeader } from "@/lib/server-session-cookie";

export const dynamic = "force-dynamic";

async function isAllowedAdmin(): Promise<boolean> {
  const adminEmails = new Set(
    (process.env.ADMIN_EMAILS ?? "")
      .split(",")
      .map((email) => email.trim().toLowerCase())
      .filter(Boolean)
  );
  const apiUrl = getInternalApiUrl();
  if (!adminEmails.size || !apiUrl) return false;

  const cookieHeader = await getServerSessionCookieHeader();
  if (!cookieHeader) return false;

  try {
    const response = await fetch(`${apiUrl}/auth/me`, {
      cache: "no-store",
      headers: { cookie: cookieHeader },
      signal: AbortSignal.timeout(3000)
    });
    if (!response.ok) return false;
    const account = (await response.json()) as { email?: unknown };
    return typeof account.email === "string" && adminEmails.has(account.email.trim().toLowerCase());
  } catch {
    return false;
  }
}

export default async function AdminLayout({ children }: Readonly<{ children: ReactNode }>) {
  if (process.env.NODE_ENV === "production" && !(await isAllowedAdmin())) notFound();
  return <AdminShell>{children}</AdminShell>;
}
