import { useEffect, useState } from "react";
import {
  X,
  Share2,
  Github,
  Link,
  Globe,
  Download,
  ExternalLink,
  Copy,
  Check,
} from "lucide-react";
import {
  exportToGist,
  importFromUrl,
  getCommunityTemplates,
  type CommunityTemplate,
} from "@/api/sharing";
import { useWorkflowStore } from "@/stores/workflowStore";
import type { Workflow } from "@/types/workflow";

type Tab = "export" | "import" | "community";

interface ShareModalProps {
  workflowId: string;
  onClose: () => void;
}

export function ShareModal({ workflowId, onClose }: ShareModalProps) {
  const [tab, setTab] = useState<Tab>("export");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-xl border border-border bg-card shadow-2xl">
        {/* Header */}
        <div className="flex items-center gap-2 border-b border-border px-5 py-3">
          <Share2 className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold">Share Workflow</span>
          <button
            onClick={onClose}
            className="ml-auto rounded-md p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border px-5">
          {(
            [
              { id: "export", label: "Export to Gist", icon: Github },
              { id: "import", label: "Import from URL", icon: Link },
              { id: "community", label: "Community", icon: Globe },
            ] as { id: Tab; label: string; icon: React.FC<{ className?: string }> }[]
          ).map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-1.5 border-b-2 px-3 py-2.5 text-xs font-medium transition-colors ${
                tab === id
                  ? "border-primary text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="p-5">
          {tab === "export" && <ExportTab workflowId={workflowId} />}
          {tab === "import" && <ImportTab onClose={onClose} />}
          {tab === "community" && <CommunityTab onClose={onClose} />}
        </div>
      </div>
    </div>
  );
}

function ExportTab({ workflowId }: { workflowId: string }) {
  const [token, setToken] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ gist_url: string; gist_id: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleExport = async () => {
    if (!token.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await exportToGist(workflowId, token.trim(), isPublic);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Export failed");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.gist_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
          GitHub Token
        </label>
        <input
          type="password"
          placeholder="ghp_..."
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <p className="mt-1 text-xs text-muted-foreground">
          Needs the <code className="font-mono">gist</code> scope.
        </p>
      </div>

      <div className="flex items-center gap-2">
        <button
          role="switch"
          aria-checked={isPublic}
          onClick={() => setIsPublic((v) => !v)}
          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
            isPublic ? "bg-primary" : "bg-muted"
          }`}
        >
          <span
            className={`inline-block h-3.5 w-3.5 rounded-full bg-white shadow transition-transform ${
              isPublic ? "translate-x-4" : "translate-x-1"
            }`}
          />
        </button>
        <span className="text-sm">Public gist</span>
      </div>

      {error && (
        <p className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">{error}</p>
      )}

      {result && (
        <div className="rounded-md border border-border bg-muted/30 px-3 py-2.5">
          <p className="mb-1.5 text-xs font-medium text-muted-foreground">Gist created</p>
          <div className="flex items-center gap-2">
            <a
              href={result.gist_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex min-w-0 flex-1 items-center gap-1 text-xs text-primary hover:underline"
            >
              <ExternalLink className="h-3 w-3 shrink-0" />
              <span className="truncate">{result.gist_url}</span>
            </a>
            <button
              onClick={handleCopy}
              className="shrink-0 rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              title="Copy URL"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={handleExport}
          disabled={!token.trim() || loading}
          className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          <Github className="h-3.5 w-3.5" />
          {loading ? "Exporting…" : "Export"}
        </button>
      </div>
    </div>
  );
}

function ImportTab({ onClose }: { onClose: () => void }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [imported, setImported] = useState<Workflow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { workflows, setActiveWorkflow, loadWorkflows } = useWorkflowStore();

  const workspaceId = workflows[0]?.workspace_id ?? "default";

  const handleImport = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const wf = await importFromUrl(url.trim(), workspaceId);
      setImported(wf);
      await loadWorkflows(workspaceId);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Import failed");
    } finally {
      setLoading(false);
    }
  };

  const handleOpen = () => {
    if (imported) {
      setActiveWorkflow(imported.id);
      onClose();
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
          Gist or raw JSON URL
        </label>
        <input
          type="url"
          placeholder="https://gist.github.com/... or https://raw.githubusercontent.com/..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      {error && (
        <p className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">{error}</p>
      )}

      {imported && (
        <div className="flex items-center justify-between rounded-md border border-border bg-muted/30 px-3 py-2.5">
          <div>
            <p className="text-xs font-medium">{imported.name}</p>
            <p className="text-xs text-muted-foreground">Imported successfully</p>
          </div>
          <button
            onClick={handleOpen}
            className="flex items-center gap-1 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Open
          </button>
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={handleImport}
          disabled={!url.trim() || loading}
          className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          <Download className="h-3.5 w-3.5" />
          {loading ? "Importing…" : "Import"}
        </button>
      </div>
    </div>
  );
}

function CommunityTab({ onClose }: { onClose: () => void }) {
  const [templates, setTemplates] = useState<CommunityTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { workflows, setActiveWorkflow, loadWorkflows } = useWorkflowStore();

  const workspaceId = workflows[0]?.workspace_id ?? "default";

  useEffect(() => {
    getCommunityTemplates()
      .then(setTemplates)
      .catch(() => setError("Failed to load community templates"))
      .finally(() => setLoading(false));
  }, []);

  const handleImport = async (tpl: CommunityTemplate) => {
    setImporting(tpl.id);
    try {
      const wf = await importFromUrl(tpl.gist_url, workspaceId);
      await loadWorkflows(workspaceId);
      setActiveWorkflow(wf.id);
      onClose();
    } catch {
      setError(`Failed to import "${tpl.name}"`);
    } finally {
      setImporting(null);
    }
  };

  if (loading) {
    return <p className="py-6 text-center text-sm text-muted-foreground">Loading…</p>;
  }

  return (
    <div className="space-y-3">
      {error && (
        <p className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">{error}</p>
      )}
      {templates.map((tpl) => (
        <div
          key={tpl.id}
          className="flex items-start gap-3 rounded-md border border-border p-3 hover:bg-muted/30 transition-colors"
        >
          <Globe className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium">{tpl.name}</p>
            <p className="mt-0.5 text-xs text-muted-foreground">{tpl.description}</p>
            <div className="mt-2 flex flex-wrap gap-1">
              {tpl.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <button
            onClick={() => handleImport(tpl)}
            disabled={importing === tpl.id}
            className="flex shrink-0 items-center gap-1 rounded-md border border-border px-2.5 py-1.5 text-xs font-medium hover:bg-accent disabled:opacity-50 transition-colors"
          >
            <Download className="h-3 w-3" />
            {importing === tpl.id ? "…" : "Import"}
          </button>
        </div>
      ))}
    </div>
  );
}
