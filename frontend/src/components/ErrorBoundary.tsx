import { Component, ReactNode } from "react";

type ErrorBoundaryState = { hasError: boolean };

export class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.error(error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="page page-section">
          <div className="status-box error">
            <strong>Something went wrong.</strong>
            <p>Please try again.</p>
            <button className="button button-small" type="button" onClick={() => window.location.reload()}>Try again</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
