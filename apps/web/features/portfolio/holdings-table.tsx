import type { Holding } from "@pocketorbit/types";
import { formatCurrency, formatQuantity, formatPercent } from "@/lib/format";

export function HoldingsTable({ holdings, currency = "USD" }: { holdings: Holding[]; currency?: string }) {
  return (
    <div className="panel table-wrap">
      <table className="data-table">
        <thead><tr><th>Asset</th><th>Quantity</th><th className="numeric">Price</th><th className="numeric">Value</th><th className="numeric">24h</th></tr></thead>
        <tbody>
          {holdings.map((holding) => (
            <tr key={holding.asset.id}>
              <td><div className="asset-cell"><span className="asset-dot">{holding.asset.symbol.slice(0, 3)}</span><span className="asset-name"><strong>{holding.asset.name}</strong><span>{holding.asset.symbol}{holding.asset.network ? ` · ${holding.asset.network}` : ""}</span></span></div></td>
              <td className="tabular">{formatQuantity(holding.quantity)}</td>
              <td className="numeric">{formatCurrency(holding.unitPrice, currency)}</td>
              <td className="numeric"><strong>{formatCurrency(holding.value, currency)}</strong></td>
              <td className="numeric">{formatPercent(holding.change24h ?? 0, true)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
