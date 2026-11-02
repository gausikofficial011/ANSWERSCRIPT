import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error inside components tree:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          backgroundColor: '#16171d',
          color: '#f3f4f6',
          fontFamily: 'system-ui, sans-serif',
          textAlign: 'center'
        }}>
          <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#ef4444' }}>Something went wrong</h2>
          <p style={{ color: '#9ca3af', marginBottom: '1.5rem', maxWidth: '500px' }}>
            An unexpected client-side error occurred. Please try reloading the page or contact support if the issue persists.
          </p>
          {this.state.error && (
            <pre style={{
              backgroundColor: '#1f2028',
              padding: '1rem',
              borderRadius: '6px',
              color: '#f87171',
              maxWidth: '90%',
              overflowX: 'auto',
              fontSize: '0.9rem',
              textAlign: 'left',
              marginBottom: '1.5rem'
            }}>
              {this.state.error.toString()}
            </pre>
          )}
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#aa3bff',
              border: 'none',
              borderRadius: '6px',
              color: '#fff',
              fontSize: '1rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#c084fc'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#aa3bff'}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
