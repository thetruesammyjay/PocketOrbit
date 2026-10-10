import { useId } from "react";

export type CryptoAssetSymbol = "BTC" | "ETH" | "SOL";

export function CryptoAssetIcon({ symbol }: { symbol: CryptoAssetSymbol }) {
  const gradientId = `solana-gradient-${useId().replace(/:/g, "")}`;

  return (
    <span className={`marketing-preview-asset-mark marketing-preview-asset-mark--${symbol.toLowerCase()}`} aria-hidden="true">
      <svg viewBox="0 0 40 40" focusable="false">
        {symbol === "BTC" && (
          <>
            <circle cx="20" cy="20" r="20" fill="#F7931A" />
            <path d="M14 7h8.2c5 0 7.8 2.2 7.8 6 0 2.4-1.2 4.1-3.4 5 2.8.8 4.3 2.6 4.3 5.4 0 4.2-3.3 6.6-8.6 6.6H14V7Z" fill="#fff" />
            <path d="M18 11h4.1c2.4 0 3.7.8 3.7 2.3s-1.3 2.4-3.7 2.4H18v-4.7Zm0 9.8h4.5c2.7 0 4.1.9 4.1 2.6s-1.4 2.6-4.1 2.6H18v-5.2Z" fill="#F7931A" />
            <path d="M16.5 5.5v4M21 5.5v4M16.5 30.5v4M21 30.5v4" fill="none" stroke="#fff" strokeLinecap="round" strokeWidth="1.5" />
          </>
        )}
        {symbol === "ETH" && (
          <>
            <circle cx="20" cy="20" r="20" fill="#F1F2F7" />
            <path d="M20 5 10.8 20.1 20 25.5l9.2-5.4L20 5Z" fill="#8B93B4" />
            <path d="M20 5v20.5l9.2-5.4L20 5Z" fill="#62698D" />
            <path d="m10.8 22.4 9.2 12.1 9.2-12.1-9.2 5.4-9.2-5.4Z" fill="#8B93B4" />
            <path d="M20 27.8v6.7l9.2-12.1-9.2 5.4Z" fill="#62698D" />
          </>
        )}
        {symbol === "SOL" && (
          <>
            <defs>
              <linearGradient id={gradientId} x1="0" x2="1" y1="0" y2="0">
                <stop stopColor="#9945FF" />
                <stop offset="1" stopColor="#14F195" />
              </linearGradient>
            </defs>
            <circle cx="20" cy="20" r="20" fill="#F0FBF6" />
            <path d="M10.2 8h20.5a1.8 1.8 0 0 1 1.3 3.1l-3.4 3.4a1.8 1.8 0 0 1-1.3.5H6.8a1.8 1.8 0 0 1-1.3-3.1l3.4-3.4a1.8 1.8 0 0 1 1.3-.5Z" fill={`url(#${gradientId})`} />
            <path d="M11.2 17.1h22a1.8 1.8 0 0 1 1.3 3.1l-3.4 3.4a1.8 1.8 0 0 1-1.3.5H7.8a1.8 1.8 0 0 1-1.3-3.1l3.4-3.4a1.8 1.8 0 0 1 1.3-.5Z" fill={`url(#${gradientId})`} />
            <path d="M10.2 26.2h20.5a1.8 1.8 0 0 1 1.3 3.1l-3.4 3.4a1.8 1.8 0 0 1-1.3.5H6.8a1.8 1.8 0 0 1-1.3-3.1l3.4-3.4a1.8 1.8 0 0 1 1.3-.5Z" fill={`url(#${gradientId})`} />
          </>
        )}
      </svg>
    </span>
  );
}
