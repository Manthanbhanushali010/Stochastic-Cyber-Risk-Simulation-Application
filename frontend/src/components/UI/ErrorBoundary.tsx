import React, { Component, ErrorInfo, ReactNode } from 'react';
import styled from 'styled-components';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

const ErrorContainer = styled.div`
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 2rem;
`;

const ErrorIcon = styled.div`
  font-size: 4rem;
  color: #f56565;
  margin-bottom: 1rem;
`;

const ErrorTitle = styled.h2`
  color: #2d3748;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
`;

const ErrorMessage = styled.p`
  color: #718096;
  font-size: 1rem;
  margin-bottom: 2rem;
  max-width: 500px;
  line-height: 1.6;
`;

const ErrorActions = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid;
  
  ${({ variant = 'primary' }) => {
    if (variant === 'primary') {
      return `
        background-color: #667eea;
        color: white;
        border-color: #667eea;
        
        &:hover {
          background-color: #5a67d8;
          border-color: #5a67d8;
        }
      `;
    } else {
      return `
        background-color: white;
        color: #4a5568;
        border-color: #e2e8f0;
        
        &:hover {
          background-color: #f7fafc;
          border-color: #cbd5e0;
        }
      `;
    }
  }}
`;

const ErrorDetails = styled.details`
  margin-top: 2rem;
  text-align: left;
  width: 100%;
  max-width: 600px;
`;

const ErrorSummary = styled.summary`
  cursor: pointer;
  color: #718096;
  font-size: 0.875rem;
  padding: 0.5rem;
  
  &:hover {
    color: #4a5568;
  }
`;

const ErrorStack = styled.pre`
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  padding: 1rem;
  font-size: 0.75rem;
  color: #4a5568;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ error, errorInfo });
    
    // You can also log the error to an error reporting service here
    // logErrorToService(error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  private handleTryAgain = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  public render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorContainer>
          <ErrorIcon>⚠️</ErrorIcon>
          <ErrorTitle>Something went wrong</ErrorTitle>
          <ErrorMessage>
            We encountered an unexpected error. This has been logged and we're working to fix it. 
            Please try refreshing the page or go back to the dashboard.
          </ErrorMessage>
          
          <ErrorActions>
            <Button variant="primary" onClick={this.handleTryAgain}>
              Try Again
            </Button>
            <Button variant="secondary" onClick={this.handleReload}>
              Reload Page
            </Button>
            <Button variant="secondary" onClick={this.handleGoHome}>
              Go to Dashboard
            </Button>
          </ErrorActions>

          {process.env.NODE_ENV === 'development' && this.state.error && (
            <ErrorDetails>
              <ErrorSummary>Show error details (development only)</ErrorSummary>
              <ErrorStack>
                <strong>Error:</strong> {this.state.error.message}
                {this.state.error.stack && (
                  <>
                    <br /><br />
                    <strong>Stack trace:</strong>
                    <br />
                    {this.state.error.stack}
                  </>
                )}
                {this.state.errorInfo?.componentStack && (
                  <>
                    <br /><br />
                    <strong>Component stack:</strong>
                    <br />
                    {this.state.errorInfo.componentStack}
                  </>
                )}
              </ErrorStack>
            </ErrorDetails>
          )}
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

// Hook version for functional components
export const useErrorHandler = () => {
  return (error: Error, errorInfo?: any) => {
    console.error('Error caught by error handler:', error, errorInfo);
    // You can implement custom error handling logic here
  };
};

// Simple error fallback component
export const ErrorFallback: React.FC<{ 
  error?: Error; 
  resetError?: () => void;
  message?: string;
}> = ({ 
  error, 
  resetError, 
  message = "Something went wrong" 
}) => {
  return (
    <ErrorContainer>
      <ErrorIcon>❌</ErrorIcon>
      <ErrorTitle>{message}</ErrorTitle>
      <ErrorMessage>
        {error?.message || "An unexpected error occurred. Please try again."}
      </ErrorMessage>
      
      {resetError && (
        <ErrorActions>
          <Button variant="primary" onClick={resetError}>
            Try Again
          </Button>
        </ErrorActions>
      )}
    </ErrorContainer>
  );
};

export default ErrorBoundary; 