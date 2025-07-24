import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import LoadingSpinner, { FullPageLoader, ButtonLoader } from '../components/UI/LoadingSpinner';

const mockTheme = {
  colors: {
    primary: '#667eea',
    background: {
      primary: '#ffffff',
      secondary: '#f7fafc',
    },
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.375rem',
  },
  shadows: {
    card: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
  },
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={mockTheme}>
      {component}
    </ThemeProvider>
  );
};

describe('LoadingSpinner', () => {
  it('renders without crashing', () => {
    renderWithTheme(<LoadingSpinner />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays custom text when provided', () => {
    const customText = 'Loading data...';
    renderWithTheme(<LoadingSpinner text={customText} />);
    expect(screen.getByText(customText)).toBeInTheDocument();
  });

  it('applies correct size classes', () => {
    const { rerender } = renderWithTheme(<LoadingSpinner size="sm" />);
    expect(screen.getByRole('status')).toHaveClass('spinner-sm');

    rerender(
      <ThemeProvider theme={mockTheme}>
        <LoadingSpinner size="lg" />
      </ThemeProvider>
    );
    expect(screen.getByRole('status')).toHaveClass('spinner-lg');
  });

  it('applies custom color', () => {
    const customColor = '#ff0000';
    renderWithTheme(<LoadingSpinner color={customColor} />);
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveStyle(`color: ${customColor}`);
  });

  it('applies custom className', () => {
    const customClass = 'custom-spinner';
    renderWithTheme(<LoadingSpinner className={customClass} />);
    expect(screen.getByRole('status')).toHaveClass(customClass);
  });
});

describe('FullPageLoader', () => {
  it('renders full page loader with default message', () => {
    renderWithTheme(<FullPageLoader />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders full page loader with custom message', () => {
    const customMessage = 'Processing your request...';
    renderWithTheme(<FullPageLoader message={customMessage} />);
    expect(screen.getByText(customMessage)).toBeInTheDocument();
  });

  it('has full page styling', () => {
    renderWithTheme(<FullPageLoader />);
    const container = screen.getByRole('status').closest('div');
    expect(container).toHaveStyle('position: fixed');
    expect(container).toHaveStyle('top: 0');
    expect(container).toHaveStyle('left: 0');
    expect(container).toHaveStyle('right: 0');
    expect(container).toHaveStyle('bottom: 0');
  });
});

describe('ButtonLoader', () => {
  it('renders button loader with default size', () => {
    renderWithTheme(<ButtonLoader />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveClass('spinner-sm');
  });

  it('renders button loader with custom size', () => {
    renderWithTheme(<ButtonLoader size="md" />);
    expect(screen.getByRole('status')).toHaveClass('spinner-md');
  });

  it('has appropriate styling for button context', () => {
    renderWithTheme(<ButtonLoader />);
    const container = screen.getByRole('status').closest('div');
    expect(container).toHaveStyle('display: inline-flex');
    expect(container).toHaveStyle('align-items: center');
  });
}); 