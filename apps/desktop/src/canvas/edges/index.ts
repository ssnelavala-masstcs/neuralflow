import { BaseEdge, EdgeLabelRenderer, getBezierPath, type EdgeProps } from "@xyflow/react";

function DataEdge({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style }: EdgeProps) {
  const [edgePath] = getBezierPath({ sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition });
  return <BaseEdge id={id} path={edgePath} style={{ stroke: "hsl(var(--primary))", strokeWidth: 2, ...style }} />;
}

function ControlEdge({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style }: EdgeProps) {
  const [edgePath] = getBezierPath({ sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition });
  return <BaseEdge id={id} path={edgePath} style={{ stroke: "hsl(var(--muted-foreground))", strokeWidth: 1.5, strokeDasharray: "5 3", ...style }} />;
}

function ConditionalEdge({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, label, style }: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({ sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition });
  return (
    <>
      <BaseEdge id={id} path={edgePath} style={{ stroke: "hsl(var(--node-router))", strokeWidth: 2, ...style }} />
      {label && (
        <EdgeLabelRenderer>
          <div style={{ position: "absolute", transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`, pointerEvents: "all" }}
            className="rounded bg-background border border-border px-1.5 py-0.5 text-xs text-foreground shadow-sm">
            {label as string}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

export const edgeTypes = {
  data: DataEdge,
  control: ControlEdge,
  conditional: ConditionalEdge,
};
