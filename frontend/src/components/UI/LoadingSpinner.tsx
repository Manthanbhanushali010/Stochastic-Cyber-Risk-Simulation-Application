import React from 'react';
import styled, { keyframes } from 'styled-components';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
}

const spin = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SpinnerContainer = styled.div<{ size: string; color: string }>`
  display: inline-block;
  position: relative;
  width: ${({ size }) => {
    switch (size) {
      case 'sm': return '16px';
      case 'md': return '24px';
      case 'lg': return '32px';
      case 'xl': return '48px';
      default: return '24px';
    }
  }};
  height: ${({ size }) => {
    switch (size) {
      case 'sm': return '16px';
      case 'md': return '24px';
      case 'lg': return '32px';
      case 'xl': return '48px';
      default: return '24px';
    }
  }};
`;

const Spinner = styled.div<{ color: string }>`
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px solid transparent;
  border-top: 2px solid ${({ color }) => color};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

const LoadingText = styled.span<{ size: string; color: string }>`
  margin-left: ${({ size }) => {
    switch (size) {
      case 'sm': return '8px';
      case 'md': return '12px';
      case 'lg': return '16px';
      case 'xl': return '20px';
      default: return '12px';
    }
  }};
  font-size: ${({ size }) => {
    switch (size) {
      case 'sm': return '0.75rem';
      case 'md': return '0.875rem';
      case 'lg': return '1rem';
      case 'xl': return '1.125rem';
      default: return '0.875rem';
    }
  }};
  color: ${({ color }) => color};
  font-weight: 500;
`;

const LoadingContainer = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;

const LoadingSpinner: React.FC<LoadingSpinnerProps & { text?: string }> = ({
  size = 'md',
  color = '#667eea',
  className,
  text,
  ...props
}) => {
  return (
    <LoadingContainer className={className} {...props}>
      <SpinnerContainer size={size} color={color}>
        <Spinner color={color} />
      </SpinnerContainer>
      {text && (
        <LoadingText size={size} color={color}>
          {text}
        </LoadingText>
      )}
    </LoadingContainer>
  );
};

// Full page loading component
export const FullPageLoader: React.FC<{ message?: string }> = ({ 
  message = 'Loading...' 
}) => {
  const Container = styled.div`
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(4px);
    z-index: 1000;
  `;

  const Message = styled.div`
    margin-top: 16px;
    font-size: 1rem;
    color: #4a5568;
    font-weight: 500;
  `;

  return (
    <Container>
      <LoadingSpinner size="xl" />
      <Message>{message}</Message>
    </Container>
  );
};

// Inline loading component for buttons
export const ButtonLoader: React.FC<{ size?: 'sm' | 'md' }> = ({ 
  size = 'sm' 
}) => {
  return <LoadingSpinner size={size} color="currentColor" />;
};

export default LoadingSpinner; 