import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, info: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("[ErrorBoundary]", error, info);
    this.props.onError?.(error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
            <div className="rounded-md bg-destructive/10 px-4 py-3 max-w-md">
              <p className="text-sm font-medium text-destructive">Something went wrong</p>
              <p className="mt-1 text-xs text-muted-foreground font-mono break-all">
                {this.state.error?.message ?? "Unknown error"}
              </p>
            </div>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="rounded-md bg-primary text-primary-foreground px-4 py-2 text-xs font-medium hover:bg-primary/90 transition-colors"
            >
              Try Again
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
