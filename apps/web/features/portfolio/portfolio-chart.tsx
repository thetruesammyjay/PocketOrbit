export function PortfolioChart({ values }: { values: number[] }) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = max - min || 1;
  const points = values.map((value, index) => {
    const x = 8 + (index / Math.max(values.length - 1, 1)) * 384;
    const y = 104 - ((value - min) / spread) * 78;
    return `${x},${y}`;
  });
  const last = points[points.length - 1]?.split(",") ?? ["392", "26"];

  return (
    <svg className="portfolio-chart" viewBox="0 0 400 118" role="img" aria-label="Illustrative sample portfolio value trend">
      <title>Illustrative sample portfolio value trend</title>
      {[24, 63, 103].map((y) => <line className="chart-grid" key={y} x1="0" x2="400" y1={y} y2={y} />)}
      <polyline className="chart-line" points={points.join(" ")} />
      <circle className="chart-point" cx={last[0]} cy={last[1]} r="4.5" />
    </svg>
  );
}
