import type { Holding } from "@pocketorbit/types";
import { formatCurrency, formatQuantity } from "@/lib/format";

export function HoldingsTable({ holdings, currency = "USD" }: { holdings: Holding[]; currency?: string }) {
  return (
    <div className="panel table-wrap">
      <table className="data-table">
        <thead><tr><th>Asset and source</th><th>Quantity</th><th className="numeric">Price</th><th className="numeric">Value</th><th>Status</th></tr></thead>
        <tbody>
          {holdings.map((holding) => (
            <tr key={holding.asset.id}>
              <td>
                <div className="asset-cell">
                  <span className="asset-dot">{holding.asset.symbol.slice(0, 3)}</span>
                  <span className="asset-name">
                    <strong>{holding.asset.name}</strong>
                    <span>{holding.asset.symbol}{holding.asset.network ? ` · ${holding.asset.network}` : ""}</span>
                    <details className="provenance-details">
                      <summary>Source and update</summary>
                      <span>
                        Balance: {holding.provenance?.balanceSources.join(", ") || "Not available"} · {holding.provenance?.balanceRetrievedAt ? new Date(holding.provenance.balanceRetrievedAt).toLocaleString() : "time unavailable"}<br />
                        Price: {holding.provenance?.priceProvider ?? "Not available"}
                        {" · provider updated "}
                        {holding.provenance?.priceProviderUpdatedAt ? new Date(holding.provenance.priceProviderUpdatedAt).toLocaleString() : "time unavailable"}
                        {" · checked "}
                        {holding.provenance?.priceRetrievedAt ? new Date(holding.provenance.priceRetrievedAt).toLocaleString() : "time unavailable"}
                      </span>
                    </details>
                  </span>
                </div>
              </td>
              <td className="tabular">{formatQuantity(holding.quantity)}</td>
              <td className="numeric">{formatCurrency(holding.unitPrice, currency)}</td>
              <td className="numeric"><strong>{formatCurrency(holding.value, currency)}</strong></td>
              <td>{holding.provenance?.quality?.replaceAll("_", " ") ?? "Needs review"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
