import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { useAuthStore } from './store/authStore';

// Components
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import SimulationPage from './pages/SimulationPage';
import SimulationResults from './pages/SimulationResults';
import PortfolioPage from './pages/PortfolioPage';
import ScenariosPage from './pages/ScenariosPage';
import ProfilePage from './pages/ProfilePage';
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ErrorBoundary from './components/UI/ErrorBoundary';
import NotificationContainer from './components/UI/NotificationContainer';

// Theme
const theme = {
  colors: {
    primary: '#667eea',
    primaryHover: '#5a67d8',
    secondary: '#764ba2',
    success: '#48bb78',
    error: '#f56565',
    warning: '#ed8936',
    info: '#4299e1',
    background: '#f7fafc',
    surface: '#ffffff',
    text: '#2d3748',
    textLight: '#718096',
    border: '#e2e8f0',
    shadow: 'rgba(0, 0, 0, 0.1)',
  },
  fonts: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    mono: "'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace",
  },
  sizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  },
  borderRadius: {
    sm: '0.125rem',
    md: '0.25rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    full: '9999px',
  },
};

// Global Styles
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html {
    font-size: 16px;
    line-height: 1.5;
  }

  body {
    font-family: ${({ theme }) => theme.fonts.primary};
    background-color: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.text};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  #root {
    min-height: 100vh;
  }

  /* Scrollbar Styling */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.colors.background};
  }

  ::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.colors.border};
    border-radius: ${({ theme }) => theme.borderRadius.full};
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${({ theme }) => theme.colors.textLight};
  }

  /* Focus styles */
  button:focus,
  input:focus,
  textarea:focus,
  select:focus {
    outline: 2px solid ${({ theme }) => theme.colors.primary};
    outline-offset: 2px;
  }

  /* Loading animation */
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Fade in animation */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .fade-in {
    animation: fadeIn 0.3s ease-out;
  }
`;

// Styled Components
const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary} 0%, ${({ theme }) => theme.colors.secondary} 100%);
`;

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAuth = true 
}) => {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <LoadingContainer>
        <LoadingSpinner size="lg" color="white" />
      </LoadingContainer>
    );
  }

  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!requireAuth && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// Main App Component
const App: React.FC = () => {
  const { checkAuthStatus, isLoading } = useAuthStore();

  useEffect(() => {
    // Check authentication status on app start
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Show loading screen while checking auth status
  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <LoadingContainer>
          <LoadingSpinner size="lg" color="white" />
        </LoadingContainer>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <ErrorBoundary>
        <Router>
          <AppContainer>
            <MainContent>
              <Routes>
                {/* Public routes */}
                <Route 
                  path="/login" 
                  element={
                    <ProtectedRoute requireAuth={false}>
                      <LoginPage />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/register" 
                  element={
                    <ProtectedRoute requireAuth={false}>
                      <RegisterPage />
                    </ProtectedRoute>
                  } 
                />

                {/* Protected routes */}
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <Dashboard />
                      </Layout>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/simulation" 
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <SimulationPage />
                      </Layout>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/simulation/:simulationId/results" 
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <SimulationResults />
                      </Layout>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/portfolio" 
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <PortfolioPage />
                      </Layout>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/scenarios" 
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <ScenariosPage />
                      </Layout>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/profile" 
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <ProfilePage />
                      </Layout>
                    </ProtectedRoute>
                  } 
                />

                {/* Default redirect */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                {/* 404 fallback */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </MainContent>
            
            {/* Global notifications */}
            <NotificationContainer />
          </AppContainer>
        </Router>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

export default App; 