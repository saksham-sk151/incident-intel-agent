// A small, dependency-free SVG bar chart. No charting library needed for a
// single ranked bar chart, and it keeps the bundle (and the amount of code
// you need to be able to explain in an interview) honest and minimal.
export default function RiskBarChart({ data }) {
  if (!data || data.length === 0) return null;

  const width = 640;
  const barHeight = 30;
  const gap = 14;
  const leftLabelWidth = 190;
  const height = data.length * (barHeight + gap);
  const maxScore = 100;
  const barMaxWidth = width - leftLabelWidth - 70;

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Top recurring risk categories">
      {data.map((row, i) => {
        const barWidth = (row.priority_score / maxScore) * barMaxWidth;
        const y = i * (barHeight + gap);
        return (
          <g key={row.category}>
            <text x={0} y={y + barHeight / 2 + 5} fontSize="12.5" fill="var(--text)" fontWeight="500">
              {row.category_label}
            </text>
            {/* track */}
            <rect
              x={leftLabelWidth}
              y={y}
              width={barMaxWidth}
              height={barHeight}
              rx={6}
              fill="var(--accent-soft)"
            />
            {/* value bar, animated in on mount */}
            <rect
              className="chart-bar"
              x={leftLabelWidth}
              y={y}
              width={Math.max(barWidth, 3)}
              height={barHeight}
              rx={6}
              fill="var(--accent)"
              style={{ animationDelay: `${i * 60}ms` }}
            />
            <text
              x={leftLabelWidth + barMaxWidth + 8}
              y={y + barHeight / 2 + 5}
              fontSize="11.5"
              fill="var(--text-secondary)"
            >
              {row.priority_score}
            </text>
            <text
              x={leftLabelWidth + 8}
              y={y + barHeight / 2 + 5}
              fontSize="10.5"
              fill="var(--on-accent)"
              fontWeight="600"
              opacity={barWidth > 60 ? 1 : 0}
            >
              {row.confidence} · n={row.count}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
