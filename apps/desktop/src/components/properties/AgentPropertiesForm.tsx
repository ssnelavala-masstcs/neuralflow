import { Field, SliderField, ToggleField } from "./PropertyFields";

const ALL_TOOLS = ["web_search", "file_read", "file_write", "file_list", "http_request", "calculator"];

interface Props {
  data: Record<string, unknown>;
  update: (u: Record<string, unknown>) => void;
}

export function AgentPropertiesForm({ data, update }: Props) {
  const tools = (data.tools as string[]) || [];

  const toggleTool = (tool: string) => {
    const current = tools.includes(tool) ? tools.filter((t) => t !== tool) : [...tools, tool];
    update({ tools: current });
  };

  return (
    <>
      <Field label="Label">
        <input
          className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
          value={(data.label as string) || ""}
          onChange={(e) => update({ label: e.target.value })}
          placeholder="Agent name"
        />
      </Field>

      <Field label="Model">
        <input
          className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
          value={(data.model as string) || ""}
          onChange={(e) => update({ model: e.target.value })}
          placeholder="e.g. gpt-4o, claude-sonnet-4-20250514"
        />
      </Field>

      <Field label="Role">
        <input
          className="w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
          value={(data.role as string) || ""}
          onChange={(e) => update({ role: e.target.value })}
          placeholder="e.g. Researcher, Writer, Planner"
        />
      </Field>

      <Field label="System Prompt">
        <textarea
          className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs resize-none h-28 focus:outline-none focus:ring-1 focus:ring-ring"
          value={(data.systemPrompt as string) || ""}
          onChange={(e) => update({ systemPrompt: e.target.value })}
          placeholder="Enter the system prompt for this agent…"
        />
      </Field>

      <SliderField label="Temperature" value={(data.temperature as number) ?? 0.7} min={0} max={2} step={0.1} onChange={(v: number) => update({ temperature: v })} />
      <SliderField label="Max Tokens" value={(data.maxTokens as number) ?? 4096} min={256} max={32768} step={256} onChange={(v: number) => update({ maxTokens: v })} />
      <SliderField label="Max Iterations" value={(data.maxIterations as number) ?? 10} min={1} max={50} step={1} onChange={(v: number) => update({ maxIterations: v })} />

      <Field label="Tools">
        <div className="space-y-1 mt-1">
          {ALL_TOOLS.map((tool) => (
            <label key={tool} className="flex items-center gap-2 text-xs cursor-pointer">
              <input type="checkbox" checked={tools.includes(tool)} onChange={() => toggleTool(tool)} className="rounded border-input" />
              <span className="text-foreground">{tool}</span>
            </label>
          ))}
        </div>
      </Field>

      <ToggleField label="Allow Delegation" description="Can this agent spawn sub-agents?" checked={(data.allowDelegation as boolean) ?? false} onChange={(v: boolean) => update({ allowDelegation: v })} />
      <ToggleField label="Verbose Mode" description="Stream all inner thoughts to run log" checked={(data.verbose as boolean) ?? false} onChange={(v: boolean) => update({ verbose: v })} />
    </>
  );
}
