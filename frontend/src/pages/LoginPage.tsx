import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const LoginContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
`;

const LoginCard = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 3rem;
  width: 100%;
  max-width: 400px;
`;

const LoginHeader = styled.div`
  text-align: center;
  margin-bottom: 2rem;
`;

const LoginLogo = styled.div`
  font-size: 2rem;
  margin-bottom: 1rem;
`;

const LoginTitle = styled.h1`
  font-size: 1.875rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
`;

const LoginSubtitle = styled.p`
  color: #718096;
  font-size: 1rem;
`;

const LoginForm = styled.form`
  space-y: 1.5rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const FormLabel = styled.label`
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
`;

const FormInput = styled.input<{ hasError?: boolean }>`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid ${({ hasError }) => hasError ? '#f56565' : '#d1d5db'};
  border-radius: 0.5rem;
  background-color: white;
  color: #111827;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #9ca3af;
  }
`;

const FormError = styled.div`
  color: #f56565;
  font-size: 0.875rem;
  margin-top: 0.5rem;
`;

const LoginButton = styled.button<{ isLoading?: boolean }>`
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: ${({ isLoading }) => isLoading ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: ${({ isLoading }) => isLoading ? '0.7' : '1'};
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }
  
  &:disabled {
    cursor: not-allowed;
  }
`;

const DividerContainer = styled.div`
  display: flex;
  align-items: center;
  margin: 2rem 0;
`;

const Divider = styled.div`
  flex: 1;
  height: 1px;
  background-color: #e5e7eb;
`;

const DividerText = styled.span`
  background-color: white;
  color: #6b7280;
  padding: 0 1rem;
  font-size: 0.875rem;
`;

const SignupLink = styled.div`
  text-align: center;
  margin-top: 2rem;
`;

const SignupText = styled.span`
  color: #6b7280;
  font-size: 0.875rem;
`;

const SignupLinkText = styled(Link)`
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
  
  &:hover {
    color: #5a67d8;
    text-decoration: underline;
  }
`;

const DemoCredentials = styled.div`
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
`;

const DemoTitle = styled.div`
  font-weight: 600;
  color: #4a5568;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
`;

const DemoInfo = styled.div`
  font-size: 0.75rem;
  color: #718096;
  line-height: 1.4;
`;

interface LoginFormData {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const { showSuccess, showError } = useNotificationStore();

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
      showSuccess('Welcome back!', 'You have been successfully logged in.');
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Login failed';
      showError('Login Failed', errorMessage);
      setErrors({ general: errorMessage });
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear field error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const fillDemoCredentials = () => {
    setFormData({
      email: 'demo@cyberrisk.com',
      password: 'demo123'
    });
    setErrors({});
  };

  return (
    <LoginContainer>
      <LoginCard>
        <LoginHeader>
          <LoginLogo>🛡️</LoginLogo>
          <LoginTitle>Welcome Back</LoginTitle>
          <LoginSubtitle>Sign in to your Cyber Risk account</LoginSubtitle>
        </LoginHeader>

        <DemoCredentials>
          <DemoTitle>Demo Account</DemoTitle>
          <DemoInfo>
            Use the demo credentials to explore the application without registration.
            <br />
            <button
              type="button"
              onClick={fillDemoCredentials}
              style={{
                background: 'none',
                border: 'none',
                color: '#667eea',
                textDecoration: 'underline',
                cursor: 'pointer',
                padding: 0,
                fontSize: 'inherit',
                marginTop: '0.5rem'
              }}
            >
              Click here to fill demo credentials
            </button>
          </DemoInfo>
        </DemoCredentials>

        <LoginForm onSubmit={handleSubmit}>
          <FormGroup>
            <FormLabel htmlFor="email">Email Address</FormLabel>
            <FormInput
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              hasError={!!errors.email}
              autoComplete="email"
            />
            {errors.email && <FormError>{errors.email}</FormError>}
          </FormGroup>

          <FormGroup>
            <FormLabel htmlFor="password">Password</FormLabel>
            <FormInput
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              hasError={!!errors.password}
              autoComplete="current-password"
            />
            {errors.password && <FormError>{errors.password}</FormError>}
          </FormGroup>

          {errors.general && (
            <FormError style={{ textAlign: 'center', marginBottom: '1rem' }}>
              {errors.general}
            </FormError>
          )}

          <LoginButton type="submit" disabled={isLoading} isLoading={isLoading}>
            {isLoading ? (
              <>
                <LoadingSpinner size="sm" color="currentColor" />
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </LoginButton>
        </LoginForm>

        <DividerContainer>
          <Divider />
          <DividerText>or</DividerText>
          <Divider />
        </DividerContainer>

        <SignupLink>
          <SignupText>
            Don't have an account?{' '}
            <SignupLinkText to="/register">
              Sign up now
            </SignupLinkText>
          </SignupText>
        </SignupLink>
      </LoginCard>
    </LoginContainer>
  );
};

export default LoginPage; 