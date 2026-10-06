import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  transpilePackages: ["@pocketorbit/types", "@pocketorbit/ui"]
};

export default nextConfig;
