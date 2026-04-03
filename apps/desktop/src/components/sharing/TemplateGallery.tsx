import { useState, useEffect, useCallback } from "react";
import { Globe, Download, Search, Tag, Loader2, CheckCircle, XCircle, Plug, Wand2, Puzzle, Share2, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";
import { getCommunityTemplates, importFromUrl, type CommunityTemplate } from "@/api/sharing";
import { useWorkflowStore } from "@/stores/workflowStore";
import { MCPMarketplace } from "@/components/mcp/MCPMarketplace";
import { AIWorkflowBuilder } from "@/components/ai/AIWorkflowBuilder";
import { PluginBrowser } from "@/components/plugins/PluginBrowser";
import { ShareModal } from "@/components/sharing/ShareModal";
import { EvaluationPanel } from "@/components/evaluation/EvaluationPanel";

type GalleryTab = "templates" | "mcp" | "ai-builder" | "plugins" | "sharing" | "evaluation";

const TABS: { id: GalleryTab; label: string; icon: React.ReactNode }[] = [
  { id: "templates", label: "Templates", icon: <Globe className="h-3.5 w-3.5" /> },
  { id: "mcp", label: "MCP Servers", icon: <Plug className="h-3.5 w-3.5" /> },
  { id: "ai-builder", label: "AI Builder", icon: <Wand2 className="h-3.5 w-3.5" /> },
  { id: "plugins", label: "Plugins", icon: <Puzzle className="h-3.5 w-3.5" /> },
  { id: "sharing", label: "Sharing", icon: <Share2 className="h-3.5 w-3.5" /> },
  { id: "evaluation", label: "Evaluation", icon: <BarChart3 className="h-3.5 w-3.5" /> },
];

interface TemplateCard {
  id: string;
  name: string;
  description: string;
  tags: string[];
  gist_url: string;
  thumbnail_url: string | null;
  source: "community" | "local";
}

const LOCAL_TEMPLATES: TemplateCard[] = [
  { id: "local-research", name: "Research Assistant", description: "Web search → structured summary report", tags: ["research", "search"], gist_url: "", thumbnail_url: null, source: "local" },
  { id: "local-content", name: "Content Writer", description: "Outline planner → SEO-optimized blog post", tags: ["content", "writing"], gist_url: "", thumbnail_url: null, source: "local" },
  { id: "local-code-review", name: "Code Reviewer", description: "Parallel security + quality review → consolidated report", tags: ["code-review", "devtools"], gist_url: "", thumbnail_url: null, source: "local" },
  { id: "local-data-analyzer", name: "Data Analyzer", description: "File reader → statistical analysis report", tags: ["data", "analytics"], gist_url: "", thumbnail_url: null, source: "local" },
  { id: "local-web-scraper", name: "Web Scraper", description: "HTTP fetch → content extraction → saved summary", tags: ["web", "scraping"], gist_url: "", thumbnail_url: null, source: "local" },
];

export function TemplateGallery() {
  const [activeTab, setActiveTab] = useState<GalleryTab>("templates");
  const [templates, setTemplates] = useState<TemplateCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState<string | null>(null);
  const [imported, setImported] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const { workflows, setActiveWorkflow, loadWorkflows } = useWorkflowStore();
  const workspaceId = workflows[0]?.workspace_id ?? "default";

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const community = await getCommunityTemplates();
      setTemplates([...community.map((c) => ({ ...c, source: "community" as const })), ...LOCAL_TEMPLATES]);
    } catch {
      setError("Failed to load community templates. Showing local templates.");
      setTemplates(LOCAL_TEMPLATES);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadTemplates(); }, [loadTemplates]);

  const allTags = Array.from(new Set(templates.flatMap((t) => t.tags))).sort();
  const filtered = templates.filter((t) => {
    const matchesSearch = !search || t.name.toLowerCase().includes(search.toLowerCase()) || t.description.toLowerCase().includes(search.toLowerCase());
    const matchesTag = !selectedTag || t.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  const handleImport = async (tpl: TemplateCard) => {
    setImporting(tpl.id);
    try {
      let wf;
      if (tpl.source === "local") {
        const filenameMap: Record<string, string> = {
          "local-research": "research-assistant.json", "local-content": "content-writer.json",
          "local-code-review": "code-reviewer.json", "local-data-analyzer": "data-analyzer.json",
          "local-web-scraper": "web-scraper.json",
        };
        const resp = await fetch(`http://127.0.0.1:7411/api/templates/${filenameMap[tpl.id]}/import?workspace_id=${workspaceId}`, { method: "POST" });
        if (!resp.ok) throw new Error("Failed to import");
        wf = await resp.json();
      } else {
        wf = await importFromUrl(tpl.gist_url, workspaceId);
      }
      await loadWorkflows(workspaceId);
      setActiveWorkflow(wf.id);
      setImported((prev) => new Set(prev).add(tpl.id));
    } catch {
      setError(`Failed to import "${tpl.name}"`);
    } finally {
      setImporting(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Tab bar */}
      <div className="flex items-center gap-1 border-b border-border px-4 py-2 shrink-0 bg-card">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
              activeTab === tab.id ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground hover:bg-accent"
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "templates" && (
          <div className="flex flex-col h-full">
            <div className="border-b border-border px-6 py-4 shrink-0">
              <div className="flex items-center gap-2 mb-3">
                <Globe className="h-5 w-5 text-primary" />
                <h2 className="text-base font-semibold">Template Gallery</h2>
              </div>
              <p className="text-xs text-muted-foreground">Browse and import community and local workflow templates.</p>
            </div>
            <div className="flex items-center gap-3 px-6 py-3 border-b border-border shrink-0">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                <input className="w-full rounded-md border border-input bg-background pl-8 pr-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring" placeholder="Search templates…" value={search} onChange={(e) => setSearch(e.target.value)} />
              </div>
              <div className="flex items-center gap-1 overflow-x-auto">
                <Tag className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <button onClick={() => setSelectedTag(null)} className={cn("px-2 py-0.5 text-xs rounded-full whitespace-nowrap transition-colors", !selectedTag ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:text-foreground")}>All</button>
                {allTags.map((tag) => (
                  <button key={tag} onClick={() => setSelectedTag(selectedTag === tag ? null : tag)} className={cn("px-2 py-0.5 text-xs rounded-full whitespace-nowrap transition-colors capitalize", selectedTag === tag ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:text-foreground")}>{tag}</button>
                ))}
              </div>
            </div>
            {error && (
              <div className="mx-6 mt-3 rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive flex items-center justify-between">
                <span>{error}</span>
                <button onClick={() => setError(null)} className="text-destructive hover:text-destructive/80"><XCircle className="h-3.5 w-3.5" /></button>
              </div>
            )}
            <div className="flex-1 overflow-y-auto p-6 min-h-0">
              {loading ? (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                  <Loader2 className="h-8 w-8 animate-spin mb-2" /><p className="text-sm">Loading templates…</p>
                </div>
              ) : filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                  <Search className="h-8 w-8 mb-2 opacity-50" /><p className="text-sm">No templates match your search.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filtered.map((tpl) => (
                    <div key={tpl.id} className={cn("rounded-lg border border-border bg-card p-4 transition-all hover:shadow-md", imported.has(tpl.id) && "border-green-500/50")}>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium truncate">{tpl.name}</span>
                            {imported.has(tpl.id) && <CheckCircle className="h-3.5 w-3.5 text-green-500 shrink-0" />}
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{tpl.description}</p>
                        </div>
                        <span className={cn("text-[10px] rounded-full px-2 py-0.5 font-medium shrink-0", tpl.source === "community" ? "bg-blue-500/10 text-blue-500" : "bg-muted text-muted-foreground")}>{tpl.source === "community" ? "Community" : "Built-in"}</span>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-3">
                        {tpl.tags.map((tag) => (<span key={tag} className="rounded-full bg-muted px-2 py-0.5 text-[10px] text-muted-foreground capitalize">{tag}</span>))}
                      </div>
                      <button onClick={() => handleImport(tpl)} disabled={importing === tpl.id} className={cn("mt-3 w-full flex items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors", imported.has(tpl.id) ? "bg-green-500/10 text-green-500" : "bg-primary text-primary-foreground hover:bg-primary/90")}>
                        {importing === tpl.id ? <><Loader2 className="h-3.5 w-3.5 animate-spin" />Importing…</> : imported.has(tpl.id) ? <><CheckCircle className="h-3.5 w-3.5" />Imported</> : <><Download className="h-3.5 w-3.5" />Import</>}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
        {activeTab === "mcp" && <MCPMarketplace />}
        {activeTab === "ai-builder" && (
          <div className="p-6 max-w-2xl mx-auto">
            <div className="mb-4">
              <h2 className="text-base font-semibold mb-1">AI Workflow Builder</h2>
              <p className="text-xs text-muted-foreground">Describe your workflow in natural language and get a generated workflow.</p>
            </div>
            <AIWorkflowBuilder />
          </div>
        )}
        {activeTab === "plugins" && <PluginBrowser />}
        {activeTab === "sharing" && <ShareModal workflowId={workflows.find(w => w.id === useWorkflowStore.getState().activeWorkflowId)?.id ?? ""} onClose={() => {}} />}
        {activeTab === "evaluation" && <EvaluationPanel />}
      </div>
    </div>
  );
}
