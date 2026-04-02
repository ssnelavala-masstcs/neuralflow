import { cn } from "@/lib/utils";

export function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="text-xs font-medium text-foreground mb-1 block">{label}</label>
      {children}
    </div>
  );
}

export function SliderField({ label, value, min, max, step, onChange }: { label: string; value: number; min: number; max: number; step: number; onChange: (v: number) => void }) {
  return (
    <Field label={`${label}: ${value}`}>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(parseFloat(e.target.value))} className="w-full accent-primary" />
    </Field>
  );
}

export function ToggleField({ label, description, checked, onChange }: { label: string; description?: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center justify-between py-1">
      <div>
        <span className="text-xs font-medium text-foreground">{label}</span>
        {description && <p className="text-[10px] text-muted-foreground">{description}</p>}
      </div>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn("relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors", checked ? "bg-primary" : "bg-input")}
      >
        <span className={cn("pointer-events-none inline-block h-4 w-4 translate-y-0 rounded-full bg-white shadow ring-0 transition-transform", checked ? "translate-x-4" : "translate-x-0")} />
      </button>
    </div>
  );
}
