import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import "@fontsource-variable/inter";
import "@fontsource-variable/space-grotesk";
import "./globals.css";
import "./marketing.css";

export const metadata: Metadata = {
  title: {
    default: "PocketOrbit — Your crypto, in one clear view",
    template: "%s · PocketOrbit"
  },
  description:
    "Bring public wallets and exchange records into one read-only crypto portfolio view. See what you own and where the numbers came from.",
  icons: {
    icon: "/brand/PocketOrbit-Favico.png"
  }
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  interactiveWidget: "resizes-content",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f7f7f4" },
    { media: "(prefers-color-scheme: dark)", color: "#f7f7f4" }
  ]
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
