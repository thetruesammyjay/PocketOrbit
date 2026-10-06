export function formatCurrency(value: string | number, currency = "USD") {
  const amount = typeof value === "number" ? value : Number(value);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
    minimumFractionDigits: 2
  }).format(Number.isFinite(amount) ? amount : 0);
}

export function formatQuantity(value: string | number, maximumFractionDigits = 6) {
  const amount = typeof value === "number" ? value : Number(value);
  return new Intl.NumberFormat("en-US", { maximumFractionDigits }).format(Number.isFinite(amount) ? amount : 0);
}

export function formatPercent(value: string | number, withSign = false) {
  const amount = typeof value === "number" ? value : Number(value);
  const sign = withSign && amount > 0 ? "+" : "";
  return `${sign}${Number.isFinite(amount) ? amount.toFixed(2) : "0.00"}%`;
}
