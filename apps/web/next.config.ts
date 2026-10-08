import type { NextConfig } from "next";

const configuredApiInternalUrl = process.env.API_INTERNAL_URL?.trim();
if (process.env.NODE_ENV === "production" && !configuredApiInternalUrl) {
  throw new Error("API_INTERNAL_URL is required for production web builds.");
}

const nextConfig: NextConfig = {
  poweredByHeader: false,
  transpilePackages: ["@pocketorbit/types", "@pocketorbit/ui"],
  async rewrites() {
    const apiInternalUrl = (configuredApiInternalUrl || "http://localhost:8000/api/v1")
      .replace(/\/+$/, "");
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiInternalUrl}/:path*`
      }
    ];
  }
};

export default nextConfig;
