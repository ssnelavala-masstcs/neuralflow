import { useEffect, useRef, useState } from "react";
import { BarChart2, Download, DollarSign, RefreshCw, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { getCostAnalytics, exportCostsAsCSV, type CostAnalytics } from "@/api/analytics";

type SortKey = "model" | "call_count" | "input_tokens" | "output_tokens" | "cost_usd";
type SortDir = "asc" | "desc";

const DAY_OPTIONS = [7, 14, 30, 90] as const;

function fmt(n: number, decimals = 4) {
  return n.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function fmtInt(n: number) {
  return n.toLocaleString();
}

function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded bg-muted", className)} />;
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-border bg-card p-4">
      <div className="mt-0.5 text-primary">{icon}</div>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-lg font-semibold tabular-nums">{value}</p>
      </div>
    </div>
  );
}

function DailyBarChart({ data }: { data: CostAnalytics["per_day"] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(600);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setWidth(el.clientWidth));
    ro.observe(el);
    setWidth(el.clientWidth);
    return () => ro.disconnect();
  }, []);

  if (!data.length) return <p className="text-xs text-muted-foreground py-4">No data</p>;

  const PAD_LEFT = 52;
  const PAD_RIGHT = 8;
  const PAD_TOP = 8;
  const PAD_BOTTOM = 28;
  const HEIGHT = 120;
  const chartW = Math.max(width - PAD_LEFT - PAD_RIGHT, 1);
  const chartH = HEIGHT - PAD_TOP - PAD_BOTTOM;

  const maxCost = Math.max(...data.map((d) => d.cost_usd), 0.000001);
  const barW = Math.max(chartW / data.length - 2, 2);
  const step = Math.max(1, Math.ceil(data.length / Math.floor(chartW / 50)));

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((t) => ({
    y: PAD_TOP + chartH - t * chartH,
    label: `$${fmt(t * maxCost, 3)}`,
  }));

  return (
    <div ref={containerRef} className="w-full">
      <svg width={width} height={HEIGHT} className="overflow-visible">
        {/* Y-axis ticks */}
        {yTicks.map((t, i) => (
          <g key={i}>
            <line
              x1={PAD_LEFT}
              x2={PAD_LEFT + chartW}
              y1={t.y}
              y2={t.y}
              stroke="hsl(var(--border))"
              strokeWidth={0.5}
            />
            <text
              x={PAD_LEFT - 4}
              y={t.y + 4}
              textAnchor="end"
              fontSize={9}
              fill="hsl(var(--muted-foreground))"
            >
              {t.label}
            </text>
          </g>
        ))}
        {/* Bars */}
        {data.map((d, i) => {
          const bh = Math.max((d.cost_usd / maxCost) * chartH, 1);
          const x = PAD_LEFT + (i / data.length) * chartW + 1;
          const y = PAD_TOP + chartH - bh;
          return (
            <g key={d.date}>
              <rect
                x={x}
                y={y}
                width={barW}
                height={bh}
                fill="hsl(var(--primary))"
                opacity={0.85}
                rx={2}
              />
              {i % step === 0 && (
                <text
                  x={x + barW / 2}
                  y={HEIGHT - 4}
                  textAnchor="middle"
                  fontSize={9}
                  fill="hsl(var(--muted-foreground))"
                >
                  {d.date.slice(5)}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function ModelBarChart({ data }: { data: CostAnalytics["per_model"] }) {
  if (!data.length) return <p className="text-xs text-muted-foreground py-4">No data</p>;

  const maxCost = Math.max(...data.map((d) => d.cost_usd), 0.000001);
  const ROW_H = 24;
  const LABEL_W = 140;
  const BAR_MAX = 200;
  const PAD_RIGHT = 60;
  const totalH = data.length * ROW_H + 8;

  return (
    <svg width={LABEL_W + BAR_MAX + PAD_RIGHT} height={totalH} className="overflow-visible">
      {data.map((d, i) => {
        const bw = (d.cost_usd / maxCost) * BAR_MAX;
        const y = i * ROW_H + 4;
        return (
          <g key={d.model}>
            <text
              x={LABEL_W - 6}
              y={y + ROW_H / 2 + 4}
              textAnchor="end"
              fontSize={10}
              fill="hsl(var(--foreground))"
            >
              {d.model.length > 18 ? d.model.slice(0, 17) + "…" : d.model}
            </text>
            <rect
              x={LABEL_W}
              y={y + 4}
              width={Math.max(bw, 2)}
              height={ROW_H - 10}
              fill="hsl(var(--primary))"
              opacity={0.8}
              rx={2}
            />
            <text
              x={LABEL_W + Math.max(bw, 2) + 4}
              y={y + ROW_H / 2 + 4}
              fontSize={9}
              fill="hsl(var(--muted-foreground))"
            >
              ${fmt(d.cost_usd, 4)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function ModelTable({ data }: { data: CostAnalytics["per_model"] }) {
  const [sortKey, setSortKey] = useState<SortKey>("cost_usd");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  function handleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  const sorted = [...data].sort((a, b) => {
    const av = sortKey === "model" ? a.model : a[sortKey];
    const bv = sortKey === "model" ? b.model : b[sortKey];
    if (typeof av === "string") return sortDir === "asc" ? av.localeCompare(bv as string) : (bv as string).localeCompare(av);
    return sortDir === "asc" ? (av as number) - (bv as number) : (bv as number) - (av as number);
  });

  const cols: Array<{ key: SortKey; label: string }> = [
    { key: "model", label: "Model" },
    { key: "call_count", label: "Calls" },
    { key: "input_tokens", label: "Input tokens" },
    { key: "output_tokens", label: "Output tokens" },
    { key: "cost_usd", label: "Cost (USD)" },
  ];

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/40">
            {cols.map((c) => (
              <th
                key={c.key}
                onClick={() => handleSort(c.key)}
                className="cursor-pointer select-none px-3 py-2 text-left text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                {c.label}
                {sortKey === c.key && (
                  <span className="ml-1">{sortDir === "asc" ? "↑" : "↓"}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={row.model} className="border-b border-border last:border-0 hover:bg-muted/20 transition-colors">
              <td className="px-3 py-2 font-mono text-xs">{row.model}</td>
              <td className="px-3 py-2 tabular-nums">{fmtInt(row.call_count)}</td>
              <td className="px-3 py-2 tabular-nums">{fmtInt(row.input_tokens)}</td>
              <td className="px-3 py-2 tabular-nums">{fmtInt(row.output_tokens)}</td>
              <td className="px-3 py-2 tabular-nums">${fmt(row.cost_usd)}</td>
            </tr>
          ))}
          {sorted.length === 0 && (
            <tr>
              <td colSpan={5} className="px-3 py-6 text-center text-xs text-muted-foreground">
                No model data
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export function CostDashboard() {
  const [days, setDays] = useState<(typeof DAY_OPTIONS)[number]>(30);
  const [data, setData] = useState<CostAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const result = await getCostAnalytics(undefined, days);
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [days]);

  return (
    <div className="flex flex-col gap-6 p-6 overflow-y-auto h-full bg-background">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart2 className="h-5 w-5 text-primary" />
          <h1 className="text-base font-semibold">Cost Analytics</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            disabled={loading}
            className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
          </button>
          <button
            onClick={() => data && exportCostsAsCSV(data)}
            disabled={!data}
            className="flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors disabled:opacity-50"
          >
            <Download className="h-3.5 w-3.5" />
            Export CSV
          </button>
          {/* Days selector */}
          <div className="flex items-center rounded-md border border-border bg-card">
            {DAY_OPTIONS.map((d, i) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium transition-colors",
                  i !== 0 && "border-l border-border",
                  i === 0 && "rounded-l-md",
                  i === DAY_OPTIONS.length - 1 && "rounded-r-md",
                  days === d
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                )}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Stat cards */}
      {loading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : data ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard
            icon={<DollarSign className="h-4 w-4" />}
            label="Total Cost"
            value={`$${fmt(data.totals.cost_usd)}`}
          />
          <StatCard
            icon={<Zap className="h-4 w-4" />}
            label="Total Tokens"
            value={fmtInt(data.totals.input_tokens + data.totals.output_tokens)}
          />
          <StatCard
            icon={<BarChart2 className="h-4 w-4" />}
            label="Total Runs"
            value={fmtInt(data.totals.run_count)}
          />
          <StatCard
            icon={<DollarSign className="h-4 w-4" />}
            label="Avg Cost / Run"
            value={`$${data.totals.run_count ? fmt(data.totals.cost_usd / data.totals.run_count) : "0.0000"}`}
          />
        </div>
      ) : null}

      {/* Daily cost chart */}
      <div className="rounded-lg border border-border bg-card p-4">
        <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wide">Cost per day</p>
        {loading ? (
          <Skeleton className="h-28 w-full" />
        ) : data ? (
          <DailyBarChart data={data.per_day} />
        ) : null}
      </div>

      {/* Model table */}
      <div className="rounded-lg border border-border bg-card p-4">
        <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wide">Cost per model</p>
        {loading ? (
          <Skeleton className="h-40 w-full" />
        ) : data ? (
          <ModelTable data={data.per_model} />
        ) : null}
      </div>

      {/* Model bar chart */}
      <div className="rounded-lg border border-border bg-card p-4">
        <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wide">Cost by model</p>
        {loading ? (
          <Skeleton className="h-32 w-full" />
        ) : data ? (
          <ModelBarChart data={data.per_model} />
        ) : null}
      </div>
    </div>
  );
}
