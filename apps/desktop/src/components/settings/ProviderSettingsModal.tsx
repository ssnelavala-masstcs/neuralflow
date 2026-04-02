import { useState, useEffect } from "react";
import { X, Plus, Trash2, CheckCircle, XCircle, Loader2, Eye, EyeOff, Key } from "lucide-react";
import { cn } from "@/lib/utils";
import { useProviderStore } from "@/stores/providerStore";
import { providersApi } from "@/api/providers";
import type { Provider, ProviderType } from "@/types/provider";

const PROVIDER_TYPES: { value: ProviderType; label: string; color: string }[] = [
  { value: "openai", label: "OpenAI", color: "text-green-500" },
  { value: "anthropic", label: "Anthropic", color: "text-purple-500" },
  { value: "groq", label: "Groq", color: "text-yellow-500" },
  { value: "mistral", label: "Mistral", color: "text-orange-500" },
  { value: "deepseek", label: "DeepSeek", color: "text-blue-500" },
  { value: "google", label: "Google", color: "text-red-500" },
  { value: "ollama", label: "Ollama", color: "text-cyan-500" },
  { value: "lm_studio", label: "LM Studio", color: "text-pink-500" },
  { value: "azure", label: "Azure OpenAI", color: "text-sky-500" },
  { value: "bedrock", label: "AWS Bedrock", color: "text-amber-500" },
  { value: "custom", label: "Custom", color: "text-slate-500" },
];

interface ProviderSettingsModalProps {
  open: boolean;
  onClose: () => void;
}

export function ProviderSettingsModal({ open, onClose }: ProviderSettingsModalProps) {
  const { providers, connectionStatus, load, addProvider, removeProvider, testProvider } = useProviderStore();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState<Record<string, boolean>>({});

  // Form state for adding a new provider
  const [formName, setFormName] = useState("");
  const [formType, setFormType] = useState<ProviderType>("openai");
  const [formBaseUrl, setFormBaseUrl] = useState("");
  const [formApiKey, setFormApiKey] = useState("");
  const [formDefaultModel, setFormDefaultModel] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (open) load();
  }, [open]);

  const resetForm = () => {
    setFormName("");
    setFormType("openai");
    setFormBaseUrl("");
    setFormApiKey("");
    setFormDefaultModel("");
    setShowAddForm(false);
    setError("");
  };

  const handleAdd = async () => {
    if (!formName.trim()) { setError("Name is required"); return; }
    setSaving(true);
    setError("");
    try {
      await addProvider({
        name: formName.trim(),
        provider_type: formType,
        base_url: formBaseUrl || null,
        api_key_ref: formApiKey || null,
        default_model: formDefaultModel || null,
      });
      resetForm();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to add provider");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remove this provider? This does not delete the API key from your keychain.")) return;
    await removeProvider(id);
  };

  const handleTest = async (id: string) => {
    await testProvider(id);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-2xl max-h-[85vh] flex flex-col rounded-xl border border-border bg-card shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border shrink-0">
          <div className="flex items-center gap-2">
            <Key className="h-5 w-5 text-primary" />
            <h2 className="text-base font-semibold">Model Providers</h2>
          </div>
          <button onClick={onClose} className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-0">
          {/* Existing providers */}
          {providers.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Configured Providers</h3>
              {providers.map((p) => (
                <ProviderCard
                  key={p.id}
                  provider={p}
                  status={connectionStatus[p.id] ?? "untested"}
                  showKey={showApiKey[p.id] ?? false}
                  onToggleKey={() => setShowApiKey((s) => ({ ...s, [p.id]: !s[p.id] }))}
                  onTest={() => handleTest(p.id)}
                  onDelete={() => handleDelete(p.id)}
                  onEdit={() => setEditingId(editingId === p.id ? null : p.id)}
                  isEditing={editingId === p.id}
                />
              ))}
            </div>
          )}

          {/* Add new provider form */}
          {showAddForm ? (
            <div className="rounded-lg border border-border bg-muted/50 p-4 space-y-3">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Add Provider</h3>
              {error && (
                <div className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">{error}</div>
              )}

              <div>
                <label className="text-xs font-medium text-foreground mb-1 block">Name *</label>
                <input className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={formName} onChange={(e) => setFormName(e.target.value)} placeholder="My OpenAI Account" />
              </div>

              <div>
                <label className="text-xs font-medium text-foreground mb-1 block">Provider Type</label>
                <select className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={formType} onChange={(e) => setFormType(e.target.value as ProviderType)}>
                  {PROVIDER_TYPES.map((pt) => (
                    <option key={pt.value} value={pt.value}>{pt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-foreground mb-1 block">Base URL <span className="text-muted-foreground">(optional)</span></label>
                <input className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={formBaseUrl} onChange={(e) => setFormBaseUrl(e.target.value)} placeholder="https://api.openai.com/v1" />
              </div>

              <div>
                <label className="text-xs font-medium text-foreground mb-1 block">API Key <span className="text-muted-foreground">(stored in OS keychain)</span></label>
                <input className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={formApiKey} onChange={(e) => setFormApiKey(e.target.value)} placeholder="sk-..." />
              </div>

              <div>
                <label className="text-xs font-medium text-foreground mb-1 block">Default Model <span className="text-muted-foreground">(optional)</span></label>
                <input className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={formDefaultModel} onChange={(e) => setFormDefaultModel(e.target.value)} placeholder="gpt-4o" />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button onClick={resetForm} className="rounded-md px-4 py-1.5 text-xs border border-border hover:bg-accent transition-colors">Cancel</button>
                <button onClick={handleAdd} disabled={saving} className="rounded-md px-4 py-1.5 text-xs bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors font-medium flex items-center gap-1.5">
                  {saving && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  Add Provider
                </button>
              </div>
            </div>
          ) : (
            <button onClick={() => setShowAddForm(true)} className="w-full rounded-lg border-2 border-dashed border-border p-4 text-sm text-muted-foreground hover:text-foreground hover:border-primary/50 transition-colors flex items-center justify-center gap-2">
              <Plus className="h-4 w-4" />
              Add Provider
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Provider Card ─── */

function ProviderCard({
  provider, status, showKey, onToggleKey, onTest, onDelete, onEdit, isEditing,
}: {
  provider: Provider;
  status: "ok" | "error" | "untested" | "testing";
  showKey: boolean;
  onToggleKey: () => void;
  onTest: () => void;
  onDelete: () => void;
  onEdit: () => void;
  isEditing: boolean;
}) {
  const pt = PROVIDER_TYPES.find((p) => p.value === provider.provider_type);
  const [testLoading, setTestLoading] = useState(false);

  const handleTest = async () => {
    setTestLoading(true);
    await onTest();
    setTestLoading(false);
  };

  return (
    <div className={cn("rounded-lg border border-border bg-card p-3 transition-all", isEditing && "ring-1 ring-primary")}>
      <div className="flex items-center gap-3">
        {/* Status indicator */}
        <div className="shrink-0">
          {status === "ok" && <CheckCircle className="h-4 w-4 text-green-500" />}
          {status === "error" && <XCircle className="h-4 w-4 text-red-500" />}
          {status === "testing" && <Loader2 className="h-4 w-4 text-yellow-500 animate-spin" />}
          {status === "untested" && <div className="h-4 w-4 rounded-full bg-muted" />}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn("text-xs font-semibold", pt?.color ?? "text-slate-500")}>{pt?.label ?? provider.provider_type}</span>
            <span className="text-xs text-muted-foreground truncate">{provider.name}</span>
          </div>
          <div className="text-[10px] text-muted-foreground mt-0.5 space-x-2">
            {provider.default_model && <span>Model: {provider.default_model}</span>}
            {provider.base_url && <span>URL: {provider.base_url}</span>}
            {provider.api_key_ref && <span className="flex items-center gap-0.5 inline"><Key className="h-2.5 w-2.5" /> Key stored</span>}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 shrink-0">
          <button onClick={handleTest} disabled={testLoading} className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors disabled:opacity-50" title="Test connection">
            {testLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CheckCircle className="h-3.5 w-3.5" />}
          </button>
          <button onClick={onDelete} className="rounded-md p-1.5 text-muted-foreground hover:text-destructive hover:bg-accent transition-colors" title="Remove">
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
