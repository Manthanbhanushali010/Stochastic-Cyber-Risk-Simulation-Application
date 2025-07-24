import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { io, Socket } from 'socket.io-client';
import { SimulationParameters, EventParameters, PolicyTerms, Distribution } from '../types';
import apiService from '../services/api';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { useNotificationStore } from '../store/notificationStore';

const SimulationContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const FormContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const MainForm = styled.form`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const SidePanel = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  height: fit-content;
  position: sticky;
  top: 2rem;
`;

const Section = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  
  &:last-child {
    border-bottom: none;
  }
`;

const SectionTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
`;

const Input = styled.input<{ hasError?: boolean }>`
  padding: 0.75rem;
  border: 1px solid ${({ hasError }) => hasError ? '#f56565' : '#d1d5db'};
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Select = styled.select<{ hasError?: boolean }>`
  padding: 0.75rem;
  border: 1px solid ${({ hasError }) => hasError ? '#f56565' : '#d1d5db'};
  border-radius: 0.5rem;
  font-size: 1rem;
  background: white;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Textarea = styled.textarea<{ hasError?: boolean }>`
  padding: 0.75rem;
  border: 1px solid ${({ hasError }) => hasError ? '#f56565' : '#d1d5db'};
  border-radius: 0.5rem;
  font-size: 1rem;
  min-height: 80px;
  resize: vertical;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const ErrorText = styled.span`
  color: #f56565;
  font-size: 0.875rem;
`;

const HelpText = styled.span`
  color: #718096;
  font-size: 0.75rem;
  line-height: 1.4;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary'; disabled?: boolean }>`
  background: ${({ variant }) => variant === 'secondary' ? 'white' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: ${({ variant }) => variant === 'secondary' ? '#667eea' : 'white'};
  border: 1px solid ${({ variant }) => variant === 'secondary' ? '#667eea' : 'transparent'};
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: ${({ disabled }) => disabled ? '0.6' : '1'};
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
`;

const ActionBar = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem;
  background: #f8fafc;
`;

const ProgressContainer = styled.div`
  margin-bottom: 1.5rem;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
`;

const ProgressFill = styled.div<{ progress: number }>`
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: ${({ progress }) => progress}%;
  transition: width 0.3s ease;
`;

const ProgressText = styled.div`
  font-size: 0.875rem;
  color: #718096;
  text-align: center;
`;

const PresetButton = styled.button`
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  color: #4a5568;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #edf2f7;
    border-color: #cbd5e0;
  }
`;

const PresetGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const distributionTypes = [
  { value: 'poisson', label: 'Poisson' },
  { value: 'lognormal', label: 'Log-Normal' },
  { value: 'pareto', label: 'Pareto' },
  { value: 'gamma', label: 'Gamma' },
  { value: 'exponential', label: 'Exponential' },
  { value: 'weibull', label: 'Weibull' },
  { value: 'negative_binomial', label: 'Negative Binomial' },
  { value: 'binomial', label: 'Binomial' }
];

const presetScenarios = {
  cyber_breach: {
    name: '🔐 Cyber Breach',
    frequency: { distribution: 'poisson', lambda: 2.5 },
    severity: { distribution: 'lognormal', mean: 500000, std: 1000000 },
    description: 'Typical cyber security breach scenario'
  },
  ransomware: {
    name: '🦠 Ransomware',
    frequency: { distribution: 'poisson', lambda: 1.2 },
    severity: { distribution: 'pareto', scale: 100000, shape: 1.5 },
    description: 'Ransomware attack with heavy-tail losses'
  },
  data_loss: {
    name: '📊 Data Loss',
    frequency: { distribution: 'negative_binomial', n: 10, p: 0.8 },
    severity: { distribution: 'gamma', shape: 2, scale: 250000 },
    description: 'Data breach and privacy violations'
  }
};

interface FormData {
  name: string;
  description: string;
  iterations: number;
  random_seed: number;
  confidence_levels: number[];
  frequency_distribution: string;
  frequency_params: Record<string, number>;
  severity_distribution: string;
  severity_params: Record<string, number>;
  portfolio_value: number;
  policy_limit: number;
  deductible: number;
  coinsurance: number;
}

interface FormErrors {
  [key: string]: string;
}

const SimulationPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showSuccess, showError, showInfo } = useNotificationStore();
  
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    iterations: 10000,
    random_seed: 42,
    confidence_levels: [90, 95, 99],
    frequency_distribution: 'poisson',
    frequency_params: { lambda: 2.0 },
    severity_distribution: 'lognormal',
    severity_params: { mean: 500000, std: 1000000 },
    portfolio_value: 10000000,
    policy_limit: 5000000,
    deductible: 50000,
    coinsurance: 0.2
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [simulationProgress, setSimulationProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [socket, setSocket] = useState<Socket | null>(null);
  const [availableDistributions, setAvailableDistributions] = useState<Distribution[]>([]);

  useEffect(() => {
    fetchAvailableDistributions();
    
    // Check if cloning from existing simulation
    const cloneId = searchParams.get('clone');
    if (cloneId) {
      cloneSimulation(cloneId);
    }
  }, [searchParams]);

  const fetchAvailableDistributions = async () => {
    try {
      const distributions = await apiService.getAvailableDistributions();
      setAvailableDistributions(distributions);
    } catch (error) {
      console.warn('Could not fetch distributions, using defaults');
    }
  };

  const cloneSimulation = async (simulationId: string) => {
    try {
      const simulation = await apiService.getSimulation(simulationId);
      if (simulation.parameters) {
        // Populate form with existing simulation parameters
        setFormData(prev => ({
          ...prev,
          name: `${simulation.name} (Copy)`,
          description: simulation.description || '',
          // Map simulation parameters to form data
          ...simulation.parameters
        }));
        showInfo('Simulation Cloned', 'Parameters loaded from previous simulation');
      }
    } catch (error) {
      showError('Clone Error', 'Could not load simulation parameters');
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Simulation name is required';
    }

    if (formData.iterations < 1000 || formData.iterations > 100000) {
      newErrors.iterations = 'Iterations must be between 1,000 and 100,000';
    }

    if (formData.portfolio_value <= 0) {
      newErrors.portfolio_value = 'Portfolio value must be positive';
    }

    if (formData.policy_limit <= 0) {
      newErrors.policy_limit = 'Policy limit must be positive';
    }

    if (formData.deductible < 0) {
      newErrors.deductible = 'Deductible cannot be negative';
    }

    if (formData.coinsurance < 0 || formData.coinsurance > 1) {
      newErrors.coinsurance = 'Coinsurance must be between 0 and 1';
    }

    // Validate distribution parameters
    if (formData.frequency_distribution === 'poisson' && formData.frequency_params.lambda <= 0) {
      newErrors.frequency_lambda = 'Lambda must be positive';
    }

    if (formData.severity_distribution === 'lognormal') {
      if (formData.severity_params.mean <= 0) {
        newErrors.severity_mean = 'Mean must be positive';
      }
      if (formData.severity_params.std <= 0) {
        newErrors.severity_std = 'Standard deviation must be positive';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      showError('Validation Error', 'Please fix the form errors before submitting');
      return;
    }

    setIsSubmitting(true);
    setSimulationProgress(0);
    setProgressMessage('Initializing simulation...');

    try {
      // Initialize WebSocket connection for progress updates
      const newSocket = io('/simulation', {
        auth: {
          token: localStorage.getItem('access_token')
        }
      });

      newSocket.on('simulation_progress', (data) => {
        setSimulationProgress(data.progress);
        setProgressMessage(data.message);
      });

      newSocket.on('simulation_complete', (data) => {
        showSuccess('Simulation Complete', 'Your Monte Carlo simulation has finished successfully');
        navigate(`/results/${data.simulation_id}`);
      });

      newSocket.on('simulation_error', (data) => {
        showError('Simulation Error', data.message);
        setIsSubmitting(false);
        setSimulationProgress(0);
      });

      setSocket(newSocket);

      // Submit simulation request
      const simulationParams: SimulationParameters = {
        name: formData.name,
        description: formData.description,
        iterations: formData.iterations,
        random_seed: formData.random_seed,
        confidence_levels: formData.confidence_levels,
        event_parameters: {
          frequency_distribution: {
            type: formData.frequency_distribution,
            parameters: formData.frequency_params
          },
          severity_distribution: {
            type: formData.severity_distribution,
            parameters: formData.severity_params
          }
        },
        portfolio: {
          total_value: formData.portfolio_value,
          policies: [{
            id: 'default',
            limit: formData.policy_limit,
            deductible: formData.deductible,
            coinsurance: formData.coinsurance,
            premium: formData.policy_limit * 0.02 // 2% of limit as default premium
          }]
        }
      };

      await apiService.runSimulation(simulationParams);
      
    } catch (error: any) {
      showError('Submission Error', error.message || 'Failed to start simulation');
      setIsSubmitting(false);
      setSimulationProgress(0);
      if (socket) {
        socket.disconnect();
        setSocket(null);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (name.includes('.')) {
      // Handle nested parameters (e.g., frequency_params.lambda)
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent as keyof FormData] as any,
          [child]: type === 'number' ? parseFloat(value) || 0 : value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'number' ? parseFloat(value) || 0 : value
      }));
    }

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const applyPreset = (presetKey: string) => {
    const preset = presetScenarios[presetKey as keyof typeof presetScenarios];
    if (preset) {
      setFormData(prev => ({
        ...prev,
        name: prev.name || preset.name,
        description: preset.description,
        frequency_distribution: preset.frequency.distribution,
        frequency_params: preset.frequency,
        severity_distribution: preset.severity.distribution,
        severity_params: preset.severity
      }));
      showInfo('Preset Applied', `${preset.name} parameters loaded`);
    }
  };

  const renderDistributionParams = (distributionType: string, paramPrefix: string) => {
    const params = formData[`${paramPrefix}_params` as keyof FormData] as Record<string, number>;
    
    switch (distributionType) {
      case 'poisson':
        return (
          <FormGroup>
            <Label>Lambda (Rate Parameter)</Label>
            <Input
              type="number"
              step="0.1"
              min="0.1"
              name={`${paramPrefix}_params.lambda`}
              value={params.lambda || ''}
              onChange={handleChange}
              hasError={!!errors[`${paramPrefix}_lambda`]}
            />
            {errors[`${paramPrefix}_lambda`] && <ErrorText>{errors[`${paramPrefix}_lambda`]}</ErrorText>}
            <HelpText>Average number of events per time period</HelpText>
          </FormGroup>
        );
        
      case 'lognormal':
        return (
          <>
            <FormGroup>
              <Label>Mean</Label>
              <Input
                type="number"
                step="1000"
                min="0"
                name={`${paramPrefix}_params.mean`}
                value={params.mean || ''}
                onChange={handleChange}
                hasError={!!errors[`${paramPrefix}_mean`]}
              />
              {errors[`${paramPrefix}_mean`] && <ErrorText>{errors[`${paramPrefix}_mean`]}</ErrorText>}
            </FormGroup>
            <FormGroup>
              <Label>Standard Deviation</Label>
              <Input
                type="number"
                step="1000"
                min="0"
                name={`${paramPrefix}_params.std`}
                value={params.std || ''}
                onChange={handleChange}
                hasError={!!errors[`${paramPrefix}_std`]}
              />
              {errors[`${paramPrefix}_std`] && <ErrorText>{errors[`${paramPrefix}_std`]}</ErrorText>}
            </FormGroup>
          </>
        );
        
      case 'pareto':
        return (
          <>
            <FormGroup>
              <Label>Scale Parameter</Label>
              <Input
                type="number"
                step="1000"
                min="0"
                name={`${paramPrefix}_params.scale`}
                value={params.scale || ''}
                onChange={handleChange}
              />
            </FormGroup>
            <FormGroup>
              <Label>Shape Parameter</Label>
              <Input
                type="number"
                step="0.1"
                min="0.1"
                name={`${paramPrefix}_params.shape`}
                value={params.shape || ''}
                onChange={handleChange}
              />
            </FormGroup>
          </>
        );
        
      case 'gamma':
        return (
          <>
            <FormGroup>
              <Label>Shape Parameter</Label>
              <Input
                type="number"
                step="0.1"
                min="0.1"
                name={`${paramPrefix}_params.shape`}
                value={params.shape || ''}
                onChange={handleChange}
              />
            </FormGroup>
            <FormGroup>
              <Label>Scale Parameter</Label>
              <Input
                type="number"
                step="1000"
                min="0"
                name={`${paramPrefix}_params.scale`}
                value={params.scale || ''}
                onChange={handleChange}
              />
            </FormGroup>
          </>
        );
        
      default:
        return null;
    }
  };

  return (
    <SimulationContainer>
      <Header>
        <Title>
          🎯 Configure Monte Carlo Simulation
        </Title>
      </Header>

      <FormContainer>
        <MainForm onSubmit={handleSubmit}>
          {/* Basic Information */}
          <Section>
            <SectionTitle>📋 Basic Information</SectionTitle>
            <FormGrid>
              <FormGroup>
                <Label>Simulation Name *</Label>
                <Input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g., Q4 Cyber Risk Assessment"
                  hasError={!!errors.name}
                />
                {errors.name && <ErrorText>{errors.name}</ErrorText>}
              </FormGroup>
              
              <FormGroup>
                <Label>Random Seed</Label>
                <Input
                  type="number"
                  name="random_seed"
                  value={formData.random_seed}
                  onChange={handleChange}
                  placeholder="42"
                />
                <HelpText>For reproducible results</HelpText>
              </FormGroup>
            </FormGrid>

            <FormGroup>
              <Label>Description</Label>
              <Textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe the purpose and scope of this simulation..."
              />
            </FormGroup>
          </Section>

          {/* Monte Carlo Settings */}
          <Section>
            <SectionTitle>⚙️ Monte Carlo Settings</SectionTitle>
            <FormGrid>
              <FormGroup>
                <Label>Number of Iterations *</Label>
                <Input
                  type="number"
                  name="iterations"
                  value={formData.iterations}
                  onChange={handleChange}
                  min="1000"
                  max="100000"
                  step="1000"
                  hasError={!!errors.iterations}
                />
                {errors.iterations && <ErrorText>{errors.iterations}</ErrorText>}
                <HelpText>Recommended: 10,000 for good accuracy</HelpText>
              </FormGroup>
            </FormGrid>
          </Section>

          {/* Frequency Distribution */}
          <Section>
            <SectionTitle>📊 Frequency Distribution</SectionTitle>
            <FormGrid>
              <FormGroup>
                <Label>Distribution Type</Label>
                <Select
                  name="frequency_distribution"
                  value={formData.frequency_distribution}
                  onChange={handleChange}
                >
                  {distributionTypes.map(dist => (
                    <option key={dist.value} value={dist.value}>
                      {dist.label}
                    </option>
                  ))}
                </Select>
              </FormGroup>
            </FormGrid>
            
            <FormGrid style={{ marginTop: '1rem' }}>
              {renderDistributionParams(formData.frequency_distribution, 'frequency')}
            </FormGrid>
          </Section>

          {/* Severity Distribution */}
          <Section>
            <SectionTitle>💰 Severity Distribution</SectionTitle>
            <FormGrid>
              <FormGroup>
                <Label>Distribution Type</Label>
                <Select
                  name="severity_distribution"
                  value={formData.severity_distribution}
                  onChange={handleChange}
                >
                  {distributionTypes.map(dist => (
                    <option key={dist.value} value={dist.value}>
                      {dist.label}
                    </option>
                  ))}
                </Select>
              </FormGroup>
            </FormGrid>
            
            <FormGrid style={{ marginTop: '1rem' }}>
              {renderDistributionParams(formData.severity_distribution, 'severity')}
            </FormGrid>
          </Section>

          {/* Portfolio & Policy Settings */}
          <Section>
            <SectionTitle>🏢 Portfolio & Policy Settings</SectionTitle>
            <FormGrid>
              <FormGroup>
                <Label>Portfolio Value *</Label>
                <Input
                  type="number"
                  name="portfolio_value"
                  value={formData.portfolio_value}
                  onChange={handleChange}
                  min="0"
                  step="100000"
                  hasError={!!errors.portfolio_value}
                />
                {errors.portfolio_value && <ErrorText>{errors.portfolio_value}</ErrorText>}
              </FormGroup>

              <FormGroup>
                <Label>Policy Limit *</Label>
                <Input
                  type="number"
                  name="policy_limit"
                  value={formData.policy_limit}
                  onChange={handleChange}
                  min="0"
                  step="100000"
                  hasError={!!errors.policy_limit}
                />
                {errors.policy_limit && <ErrorText>{errors.policy_limit}</ErrorText>}
              </FormGroup>

              <FormGroup>
                <Label>Deductible</Label>
                <Input
                  type="number"
                  name="deductible"
                  value={formData.deductible}
                  onChange={handleChange}
                  min="0"
                  step="10000"
                  hasError={!!errors.deductible}
                />
                {errors.deductible && <ErrorText>{errors.deductible}</ErrorText>}
              </FormGroup>

              <FormGroup>
                <Label>Coinsurance Rate</Label>
                <Input
                  type="number"
                  name="coinsurance"
                  value={formData.coinsurance}
                  onChange={handleChange}
                  min="0"
                  max="1"
                  step="0.05"
                  hasError={!!errors.coinsurance}
                />
                {errors.coinsurance && <ErrorText>{errors.coinsurance}</ErrorText>}
                <HelpText>Proportion of loss retained (0.0 = 0%, 1.0 = 100%)</HelpText>
              </FormGroup>
            </FormGrid>
          </Section>

          {/* Progress Section */}
          {isSubmitting && (
            <Section>
              <SectionTitle>⏳ Simulation Progress</SectionTitle>
              <ProgressContainer>
                <ProgressBar>
                  <ProgressFill progress={simulationProgress} />
                </ProgressBar>
                <ProgressText>
                  {simulationProgress.toFixed(1)}% - {progressMessage}
                </ProgressText>
              </ProgressContainer>
            </Section>
          )}

          {/* Action Bar */}
          <ActionBar>
            <Button 
              type="button" 
              variant="secondary" 
              onClick={() => navigate('/dashboard')}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="sm" color="currentColor" />
                  Running Simulation...
                </>
              ) : (
                '🚀 Run Simulation'
              )}
            </Button>
          </ActionBar>
        </MainForm>

        {/* Side Panel */}
        <SidePanel>
          <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>🎲 Quick Presets</h3>
          <PresetGrid>
            {Object.entries(presetScenarios).map(([key, preset]) => (
              <PresetButton
                key={key}
                type="button"
                onClick={() => applyPreset(key)}
                disabled={isSubmitting}
              >
                {preset.name}
              </PresetButton>
            ))}
          </PresetGrid>

          <div style={{ marginTop: '2rem' }}>
            <h4 style={{ marginBottom: '0.5rem', color: '#4a5568' }}>💡 Tips</h4>
            <ul style={{ fontSize: '0.875rem', color: '#718096', lineHeight: '1.5', paddingLeft: '1rem' }}>
              <li>Start with 10,000 iterations for good accuracy</li>
              <li>Use log-normal distribution for cyber loss severity</li>
              <li>Poisson distribution works well for attack frequency</li>
              <li>Higher iterations = more accurate results but slower runtime</li>
            </ul>
          </div>

          <div style={{ marginTop: '2rem', padding: '1rem', background: '#f7fafc', borderRadius: '0.5rem' }}>
            <h4 style={{ marginBottom: '0.5rem', color: '#4a5568', fontSize: '0.875rem' }}>📊 Expected Results</h4>
            <div style={{ fontSize: '0.75rem', color: '#718096', lineHeight: '1.4' }}>
              <div>• Risk metrics (VaR, TVaR)</div>
              <div>• Loss distribution charts</div>
              <div>• Exceedance curves</div>
              <div>• Statistical summary</div>
            </div>
          </div>
        </SidePanel>
      </FormContainer>
    </SimulationContainer>
  );
};

export default SimulationPage; 