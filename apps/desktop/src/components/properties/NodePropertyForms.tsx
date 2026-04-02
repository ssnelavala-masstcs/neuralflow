import { Field } from "./PropertyFields";

interface Props {
  data: Record<string, unknown>;
  update: (u: Record<string, unknown>) => void;
}

export function TaskPropertiesForm({ data, update }: Props) {
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Task name" />
      </Field>
      <Field label="Description">
        <textarea className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs resize-none h-24 focus:outline-none focus:ring-1 focus:ring-ring" value={(data.description as string) || ""} onChange={(e) => update({ description: e.target.value })} placeholder="Describe what this task does…" />
      </Field>
      <Field label="Expected Output">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.expectedOutput as string) || ""} onChange={(e) => update({ expectedOutput: e.target.value })} placeholder="Expected output format" />
      </Field>
    </>
  );
}

export function ToolPropertiesForm({ data, update }: Props) {
  const builtInTools = ["web_search", "file_read", "file_write", "file_list", "http_request", "calculator"];
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Tool name" />
      </Field>
      <Field label="Tool">
        <select className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.toolName as string) || ""} onChange={(e) => update({ toolName: e.target.value })}>
          <option value="">Select a tool…</option>
          {builtInTools.map((t) => (<option key={t} value={t}>{t}</option>))}
        </select>
      </Field>
    </>
  );
}

export function TriggerPropertiesForm({ data, update }: Props) {
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Trigger name" />
      </Field>
      <Field label="Trigger Type">
        <select className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.triggerType as string) || "manual"} onChange={(e) => update({ triggerType: e.target.value })}>
          <option value="manual">Manual</option>
          <option value="cron">Cron Schedule</option>
          <option value="webhook">Webhook</option>
          <option value="file_watch">File Watch</option>
        </select>
      </Field>
      {data.triggerType === "cron" && (
        <Field label="Cron Expression">
          <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.cronExpression as string) || ""} onChange={(e) => update({ cronExpression: e.target.value })} placeholder="e.g. 0 9 * * 1-5" />
        </Field>
      )}
      {data.triggerType === "webhook" && (
        <Field label="Webhook Path">
          <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.webhookPath as string) || ""} onChange={(e) => update({ webhookPath: e.target.value })} placeholder="e.g. /webhooks/my-trigger" />
        </Field>
      )}
    </>
  );
}

export function RouterPropertiesForm({ data, update }: Props) {
  const conditions = (data.conditions as Array<{ expression: string; targetLabel: string }>) || [];
  const addCondition = () => update({ conditions: [...conditions, { expression: "", targetLabel: "" }] });
  const updateCondition = (index: number, field: string, value: string) => {
    const updated = conditions.map((c, i) => (i === index ? { ...c, [field]: value } : c));
    update({ conditions: updated });
  };
  const removeCondition = (index: number) => update({ conditions: conditions.filter((_, i) => i !== index) });

  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Router name" />
      </Field>
      <Field label="Conditions">
        <div className="space-y-2 mt-1">
          {conditions.map((c, i) => (
            <div key={i} className="flex gap-1 items-start">
              <input className="flex-1 rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" placeholder="Expression" value={c.expression} onChange={(e) => updateCondition(i, "expression", e.target.value)} />
              <input className="flex-1 rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" placeholder="Target" value={c.targetLabel} onChange={(e) => updateCondition(i, "targetLabel", e.target.value)} />
              <button onClick={() => removeCondition(i)} className="text-destructive hover:text-destructive/80 p-1 text-xs">✕</button>
            </div>
          ))}
          <button onClick={addCondition} className="text-xs text-primary hover:text-primary/80">+ Add condition</button>
        </div>
      </Field>
    </>
  );
}

export function MemoryPropertiesForm({ data, update }: Props) {
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Memory name" />
      </Field>
      <Field label="Store Type">
        <select className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.storeType as string) || "vector"} onChange={(e) => update({ storeType: e.target.value })}>
          <option value="vector">Vector Search</option>
          <option value="kv">Key-Value</option>
          <option value="conversation">Conversation History</option>
        </select>
      </Field>
      {(data.storeType === "vector") && (
        <Field label="Embedding Model">
          <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.embeddingModel as string) || ""} onChange={(e) => update({ embeddingModel: e.target.value })} placeholder="e.g. text-embedding-3-small" />
        </Field>
      )}
    </>
  );
}

export function HumanPropertiesForm({ data, update }: Props) {
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Checkpoint name" />
      </Field>
      <Field label="Prompt to Human">
        <textarea className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs resize-none h-24 focus:outline-none focus:ring-1 focus:ring-ring" value={(data.prompt as string) || ""} onChange={(e) => update({ prompt: e.target.value })} placeholder="What should the human review or approve?" />
      </Field>
    </>
  );
}

export function AggregatorPropertiesForm({ data, update }: Props) {
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Aggregator name" />
      </Field>
      <Field label="Merge Strategy">
        <select className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.strategy as string) || "concat"} onChange={(e) => update({ strategy: e.target.value })}>
          <option value="concat">Concatenate</option>
          <option value="json_merge">JSON Merge</option>
          <option value="last">Last Value</option>
        </select>
      </Field>
    </>
  );
}

export function OutputPropertiesForm({ data, update }: Props) {
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Output name" />
      </Field>
      <Field label="Output Format">
        <select className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.outputFormat as string) || "markdown"} onChange={(e) => update({ outputFormat: e.target.value })}>
          <option value="markdown">Markdown</option>
          <option value="json">JSON</option>
          <option value="text">Plain Text</option>
        </select>
      </Field>
    </>
  );
}

export function SubflowPropertiesForm({ data, update }: Props) {
  return (
    <>
      <Field label="Label">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.label as string) || ""} onChange={(e) => update({ label: e.target.value })} placeholder="Subflow name" />
      </Field>
      <Field label="Subflow ID">
        <input className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring" value={(data.subflowId as string) || ""} onChange={(e) => update({ subflowId: e.target.value })} placeholder="Workflow ID to embed" />
      </Field>
    </>
  );
}
