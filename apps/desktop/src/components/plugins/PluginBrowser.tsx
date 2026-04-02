import { useEffect, useState } from "react";
import { CheckCircle2, Package, Puzzle, RefreshCw, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { listPlugins, reloadPlugins, type Plugin } from "@/api/plugins";

export function PluginBrowser() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [reloading, setReloading] = useState(false);

  useEffect(() => {
    listPlugins()
      .then(setPlugins)
      .finally(() => setLoading(false));
  }, []);

  async function handleReload() {
    setReloading(true);
    try {
      const updated = await reloadPlugins();
      setPlugins(updated);
    } finally {
      setReloading(false);
    }
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Puzzle className="h-5 w-5 text-primary" />
          <h2 className="text-base font-semibold">Plugins</h2>
        </div>
        <button
          onClick={handleReload}
          disabled={reloading}
          className="flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-sm hover:bg-muted disabled:opacity-50"
        >
          <RefreshCw className={cn("h-3.5 w-3.5", reloading && "animate-spin")} />
          Reload Plugins
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col gap-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      ) : plugins.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-border py-12 text-center">
          <Package className="h-10 w-10 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            No plugins installed. Install a NeuralFlow plugin package and click Reload.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {plugins.map((plugin) => (
            <PluginCard key={plugin.name} plugin={plugin} />
          ))}
        </div>
      )}

      <div className="rounded-lg border border-border bg-card p-4">
        <p className="mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Installing Plugins
        </p>
        <pre className="rounded bg-muted px-3 py-2 text-xs font-mono text-foreground">
          pip install my-neuralflow-plugin
        </pre>
        <p className="mt-2 text-xs text-muted-foreground">
          Any package that exposes a <code className="rounded bg-muted px-1">neuralflow_plugins</code> entry point will appear here after reload.
        </p>
      </div>
    </div>
  );
}

function PluginCard({ plugin }: { plugin: Plugin }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          {plugin.loaded ? (
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-500" />
          ) : (
            <XCircle
              className="mt-0.5 h-4 w-4 shrink-0 text-red-500"
            />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{plugin.name}</span>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                v{plugin.version}
              </span>
            </div>
            {plugin.author && (
              <p className="text-xs text-muted-foreground">by {plugin.author}</p>
            )}
          </div>
        </div>
      </div>

      {plugin.description && (
        <p className="mt-2 text-sm text-muted-foreground">{plugin.description}</p>
      )}

      {plugin.error && !plugin.loaded && (
        <p className="mt-2 rounded bg-red-500/10 px-2 py-1 text-xs text-red-500">
          {plugin.error}
        </p>
      )}

      <div className="mt-3 flex flex-wrap gap-3">
        {plugin.node_types.length > 0 && (
          <div className="flex flex-wrap items-center gap-1">
            <span className="text-xs text-muted-foreground">Nodes:</span>
            {plugin.node_types.map((n) => (
              <span key={n} className="rounded bg-primary/10 px-1.5 py-0.5 text-xs text-primary">
                {n}
              </span>
            ))}
          </div>
        )}
        {plugin.tool_names.length > 0 && (
          <div className="flex flex-wrap items-center gap-1">
            <span className="text-xs text-muted-foreground">Tools:</span>
            {plugin.tool_names.map((t) => (
              <span key={t} className="rounded bg-muted px-1.5 py-0.5 text-xs text-foreground">
                {t}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
