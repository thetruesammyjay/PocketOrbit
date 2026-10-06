import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

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

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
