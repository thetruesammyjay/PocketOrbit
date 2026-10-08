export function getInternalApiUrl(): string | undefined {
  const configuredUrl = process.env.API_INTERNAL_URL?.trim();
  if (configuredUrl) return configuredUrl.replace(/\/+$/, "");
  if (process.env.NODE_ENV !== "production") return "http://localhost:8000/api/v1";
  return undefined;
}
