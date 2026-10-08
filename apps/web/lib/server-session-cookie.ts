import { cookies } from "next/headers";

export async function getServerSessionCookieHeader(): Promise<string | undefined> {
  const cookieName = process.env.AUTH_COOKIE_NAME?.trim() || "pocketorbit_session";
  const sessionToken = (await cookies()).get(cookieName)?.value;
  return sessionToken ? `${cookieName}=${sessionToken}` : undefined;
}
