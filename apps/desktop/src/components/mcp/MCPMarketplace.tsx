import { useState, useEffect, useMemo } from "react";
import { Search, Plug, Download, ExternalLink, Star, Package, Filter, X } from "lucide-react";
import { api } from "@/api/client";
import { cn } from "@/lib/utils";

interface MCPServer {
  id: string;
  name: string;
  description: string;
  author: string;
  transport: string;
  category: string;
  tools: string[];
  env_vars: string[];
  homepage: string;
  repository: string;
}

export function MCPMarketplace({ onClose }: { onClose?: () => void }) {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<{ servers: MCPServer[] }>("/api/mcp/registry"),
      api.get<{ categories: string[] }>("/api/mcp/registry/categories"),
    ])
      .then(([serversData, catsData]) => {
        setServers(serversData.servers);
        setCategories(catsData.categories);
      })
      .catch(() => { /* ignore */ })
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let results = servers;
    if (selectedCategory) {
      results = results.filter((s) => s.category === selectedCategory);
    }
    if (query) {
      const q = query.toLowerCase();
      results = results.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.tools.some((t) => t.toLowerCase().includes(q))
      );
    }
    return results;
  }, [servers, selectedCategory, query]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">
        Loading MCP servers…
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3 shrink-0">
        <div className="flex items-center gap-2">
          <Plug className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold">MCP Marketplace</h2>
        </div>
        {onClose && (
          <button onClick={onClose} className="rounded p-1 text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Search & Filter */}
      <div className="flex items-center gap-2 border-b border-border px-4 py-2 shrink-0">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search servers or tools…"
            className="w-full rounded-md border border-input bg-background pl-7 pr-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
        <select
          value={selectedCategory ?? ""}
          onChange={(e) => setSelectedCategory(e.target.value || null)}
          className="rounded-md border border-input bg-background px-2 py-1.5 text-xs focus:outline-none"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
          ))}
        </select>
      </div>

      {/* Server List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {filtered.length === 0 && (
          <p className="py-8 text-center text-xs text-muted-foreground">No MCP servers found.</p>
        )}
        {filtered.map((server) => (
          <button
            key={server.id}
            onClick={() => setSelectedServer(selectedServer?.id === server.id ? null : server)}
            className={cn(
              "w-full text-left rounded-lg border border-border p-3 transition-all hover:border-primary/50",
              selectedServer?.id === server.id && "border-primary bg-accent/50"
            )}
          >
            <div className="flex items-start gap-2">
              <div className="rounded-md bg-primary/10 p-1.5 shrink-0">
                <Package className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold">{server.name}</span>
                  <span className="text-[10px] text-muted-foreground">by {server.author}</span>
                </div>
                <p className="text-[10px] text-muted-foreground mt-0.5 line-clamp-2">{server.description}</p>
                <div className="flex items-center gap-1 mt-1.5 flex-wrap">
                  <span className="rounded bg-muted px-1.5 py-0.5 text-[9px] font-mono text-muted-foreground">
                    {server.transport}
                  </span>
                  {server.tools.slice(0, 3).map((tool) => (
                    <span key={tool} className="rounded bg-muted px-1.5 py-0.5 text-[9px] font-mono text-muted-foreground">
                      {tool}
                    </span>
                  ))}
                  {server.tools.length > 3 && (
                    <span className="text-[9px] text-muted-foreground">+{server.tools.length - 3} more</span>
                  )}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Server Detail Panel */}
      {selectedServer && (
        <div className="border-t border-border p-4 shrink-0 bg-card">
          <h3 className="text-sm font-semibold mb-2">{selectedServer.name}</h3>
          <p className="text-xs text-muted-foreground mb-3">{selectedServer.description}</p>

          {selectedServer.env_vars.length > 0 && (
            <div className="mb-3">
              <p className="text-[10px] font-semibold text-muted-foreground mb-1">Required Environment Variables</p>
              {selectedServer.env_vars.map((env) => (
                <div key={env} className="flex items-center gap-2 text-[10px] font-mono bg-muted rounded px-2 py-1 mb-1">
                  {env}
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs font-medium hover:bg-primary/90 transition-colors">
              <Download className="h-3 w-3" />
              Install
            </button>
            {selectedServer.homepage && (
              <a
                href={selectedServer.homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 rounded-md border border-border px-2.5 py-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <ExternalLink className="h-3 w-3" />
                Docs
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
