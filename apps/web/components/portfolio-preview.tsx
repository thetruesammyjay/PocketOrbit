import { CryptoAssetIcon } from "@/components/crypto-asset-icon";

const assets = [
  { symbol: "BTC", name: "Bitcoin", percent: "31.4%" },
  { symbol: "ETH", name: "Ethereum", percent: "21.9%" },
  { symbol: "SOL", name: "Solana", percent: "20.1%" }
] as const;

export function PortfolioPreview() {
  return (
    <div className="marketing-preview-window" aria-label="Illustrative PocketOrbit portfolio preview">
      <div className="marketing-preview-toolbar">
        <span className="marketing-preview-title"><span className="marketing-preview-orbit" aria-hidden="true" />My portfolio</span>
        <span className="marketing-preview-sample">Sample values · no wallet connected</span>
      </div>
      <div className="marketing-preview-content">
        <section className="marketing-preview-summary" aria-label="Sample portfolio value">
          <span className="marketing-preview-label">Portfolio value · USD</span>
          <strong className="marketing-preview-value">$31,686.37</strong>
          <p>Illustrative snapshot across three sample sources</p>
          <svg className="marketing-preview-chart" viewBox="0 0 590 145" preserveAspectRatio="none" aria-hidden="true">
            <path d="M0 132H590M0 79H590M0 26H590" stroke="#E9EAE6" strokeWidth="1"/>
            <path className="marketing-preview-chart-line" d="M0 121 48 105 96 110 144 91 190 100 238 80 284 86 334 65 383 71 432 49 482 52 532 30 590 17" pathLength={1} fill="none" stroke="#6C5CE7" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="590" cy="17" r="7" fill="#FFFFFF" stroke="#6C5CE7" strokeWidth="4"/>
          </svg>
          <div className="marketing-preview-assets" aria-label="Sample assets">
            {assets.map((asset) => (
              <div className="marketing-preview-asset" key={asset.symbol}>
                <CryptoAssetIcon symbol={asset.symbol} />
                <span><strong>{asset.symbol}</strong><small>{asset.name}</small></span>
                <b>{asset.percent}</b>
              </div>
            ))}
          </div>
        </section>
        <aside className="marketing-preview-provenance" aria-label="Details behind this sample value">
          <span className="marketing-preview-label">Behind this number</span>
          <h3>Context you can check.</h3>
          <dl>
            <div><dt>Sources</dt><dd>3 sample records</dd></div>
            <div><dt>Updated</dt><dd>Sample snapshot</dd></div>
            <div><dt>Quality</dt><dd><span className="marketing-quality-dot" />Estimated</dd></div>
          </dl>
          <p>Every source and quality label here is illustrative. Live connections are still being built.</p>
        </aside>
      </div>
    </div>
  );
}
