import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  RadarController,
  RadialLinearScale,
} from 'chart.js';
import { Bar, Line, Radar } from 'react-chartjs-2';
import { Scenario, ScenarioComparison } from '../types';
import apiService from '../services/api';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { useNotificationStore } from '../store/notificationStore';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  RadarController,
  RadialLinearScale
);

const ScenariosContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
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

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'danger'; disabled?: boolean }>`
  background: ${({ variant, disabled }) => {
    if (disabled) return '#e2e8f0';
    switch (variant) {
      case 'secondary': return 'white';
      case 'danger': return '#ef4444';
      default: return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
  }};
  color: ${({ variant, disabled }) => {
    if (disabled) return '#a0aec0';
    return variant === 'secondary' ? '#667eea' : 'white';
  }};
  border: 1px solid ${({ variant }) => variant === 'secondary' ? '#667eea' : 'transparent'};
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const SidePanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const CardHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
`;

const CardContent = styled.div`
  padding: 1.5rem;
`;

const ScenarioGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
`;

const ScenarioCard = styled.div<{ isActive?: boolean; isSelected?: boolean }>`
  border: 2px solid ${({ isActive, isSelected }) => {
    if (isSelected) return '#667eea';
    if (isActive) return '#10b981';
    return '#e2e8f0';
  }};
  border-radius: 12px;
  padding: 1.5rem;
  background: ${({ isSelected }) => isSelected ? '#f7fafc' : 'white'};
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  
  &:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  }
`;

const ScenarioBadge = styled.div<{ type: 'active' | 'template' | 'custom' }>`
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: ${({ type }) => {
    switch (type) {
      case 'active': return '#10b981';
      case 'template': return '#f59e0b';
      default: return '#667eea';
    }
  }};
  color: white;
`;

const ScenarioName = styled.h4`
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
  padding-right: 4rem;
`;

const ScenarioDescription = styled.p`
  color: #718096;
  font-size: 0.875rem;
  line-height: 1.4;
  margin-bottom: 1rem;
`;

const ScenarioStats = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
`;

const StatLabel = styled.div`
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
`;

const ScenarioActions = styled.div`
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  color: #718096;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f7fafc;
    color: #4a5568;
  }
`;

const Modal = styled.div<{ isOpen: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: ${({ isOpen }) => isOpen ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const ModalTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #718096;
  
  &:hover {
    color: #4a5568;
  }
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

const ComparisonSection = styled.div`
  margin-top: 2rem;
`;

const ComparisonGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
`;

const ChartContainer = styled.div`
  height: 300px;
  margin-top: 1rem;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 4rem 2rem;
  color: #718096;
`;

const EmptyIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 1rem;
`;

const EmptyTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
`;

const EmptyText = styled.p`
  margin-bottom: 2rem;
  line-height: 1.5;
`;

const TemplateGrid = styled.div`
  display: grid;
  gap: 0.75rem;
`;

const TemplateCard = styled.div`
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f7fafc;
  }
`;

const TemplateTitle = styled.div`
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
`;

const TemplateDescription = styled.div`
  font-size: 0.875rem;
  color: #718096;
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 0.5rem;
`;

const CheckboxItem = styled.label`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #4a5568;
`;

const Checkbox = styled.input`
  width: 1rem;
  height: 1rem;
`;

const scenarioTemplates = [
  {
    id: 'cyber_breach',
    name: '🔐 Cyber Data Breach',
    description: 'Typical data breach scenario with regulatory fines',
    frequency: { distribution: 'poisson', lambda: 2.5 },
    severity: { distribution: 'lognormal', mean: 750000, std: 1500000 },
    threat_level: 'high',
    industry_focus: ['technology', 'healthcare', 'finance']
  },
  {
    id: 'ransomware',
    name: '🦠 Ransomware Attack',
    description: 'Ransomware with business interruption and recovery costs',
    frequency: { distribution: 'poisson', lambda: 1.8 },
    severity: { distribution: 'pareto', scale: 200000, shape: 1.3 },
    threat_level: 'high',
    industry_focus: ['all']
  },
  {
    id: 'insider_threat',
    name: '👤 Insider Threat',
    description: 'Malicious or negligent insider causing data loss',
    frequency: { distribution: 'negative_binomial', n: 8, p: 0.7 },
    severity: { distribution: 'gamma', shape: 1.5, scale: 300000 },
    threat_level: 'medium',
    industry_focus: ['finance', 'government', 'technology']
  },
  {
    id: 'supply_chain',
    name: '🔗 Supply Chain Attack',
    description: 'Third-party vendor compromise affecting multiple clients',
    frequency: { distribution: 'poisson', lambda: 0.8 },
    severity: { distribution: 'lognormal', mean: 2000000, std: 4000000 },
    threat_level: 'high',
    industry_focus: ['technology', 'manufacturing']
  },
  {
    id: 'ddos_attack',
    name: '⚡ DDoS Attack',
    description: 'Distributed denial of service causing business interruption',
    frequency: { distribution: 'poisson', lambda: 4.2 },
    severity: { distribution: 'exponential', rate: 0.000008 },
    threat_level: 'medium',
    industry_focus: ['technology', 'ecommerce', 'gaming']
  },
  {
    id: 'phishing',
    name: '🎣 Phishing Campaign',
    description: 'Large-scale phishing leading to credential theft',
    frequency: { distribution: 'poisson', lambda: 6.5 },
    severity: { distribution: 'gamma', shape: 2, scale: 50000 },
    threat_level: 'medium',
    industry_focus: ['all']
  }
];

interface ScenarioFormData {
  name: string;
  description: string;
  threat_level: string;
  frequency_distribution: string;
  frequency_params: Record<string, number>;
  severity_distribution: string;
  severity_params: Record<string, number>;
  industry_focus: string[];
}

const ScenariosPage: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess, showError, showInfo } = useNotificationStore();
  
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);
  const [comparison, setComparison] = useState<ScenarioComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [editingScenario, setEditingScenario] = useState<Scenario | null>(null);
  
  const [formData, setFormData] = useState<ScenarioFormData>({
    name: '',
    description: '',
    threat_level: 'medium',
    frequency_distribution: 'poisson',
    frequency_params: { lambda: 2.0 },
    severity_distribution: 'lognormal',
    severity_params: { mean: 500000, std: 1000000 },
    industry_focus: []
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    try {
      setLoading(true);
      const data = await apiService.getScenarios();
      setScenarios(data);
    } catch (error) {
      showError('Error', 'Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScenario = () => {
    setEditingScenario(null);
    setFormData({
      name: '',
      description: '',
      threat_level: 'medium',
      frequency_distribution: 'poisson',
      frequency_params: { lambda: 2.0 },
      severity_distribution: 'lognormal',
      severity_params: { mean: 500000, std: 1000000 },
      industry_focus: []
    });
    setErrors({});
    setShowModal(true);
  };

  const handleEditScenario = (scenario: Scenario) => {
    setEditingScenario(scenario);
    setFormData({
      name: scenario.name,
      description: scenario.description || '',
      threat_level: scenario.threat_level || 'medium',
      frequency_distribution: scenario.frequency_distribution?.type || 'poisson',
      frequency_params: scenario.frequency_distribution?.parameters || { lambda: 2.0 },
      severity_distribution: scenario.severity_distribution?.type || 'lognormal',
      severity_params: scenario.severity_distribution?.parameters || { mean: 500000, std: 1000000 },
      industry_focus: scenario.industry_focus || []
    });
    setErrors({});
    setShowModal(true);
  };

  const handleDeleteScenario = async (scenario: Scenario) => {
    if (!window.confirm(`Delete scenario "${scenario.name}"? This cannot be undone.`)) {
      return;
    }

    try {
      await apiService.deleteScenario(scenario.id);
      showSuccess('Success', 'Scenario deleted successfully');
      await fetchScenarios();
    } catch (error: any) {
      showError('Error', error.message || 'Failed to delete scenario');
    }
  };

  const handleActivateScenario = async (scenario: Scenario) => {
    try {
      await apiService.activateScenario(scenario.id);
      showSuccess('Success', `Scenario "${scenario.name}" activated`);
      await fetchScenarios();
    } catch (error: any) {
      showError('Error', error.message || 'Failed to activate scenario');
    }
  };

  const handleDeactivateScenario = async (scenario: Scenario) => {
    try {
      await apiService.deactivateScenario(scenario.id);
      showSuccess('Success', `Scenario "${scenario.name}" deactivated`);
      await fetchScenarios();
    } catch (error: any) {
      showError('Error', error.message || 'Failed to deactivate scenario');
    }
  };

  const handleDuplicateScenario = async (scenario: Scenario) => {
    try {
      await apiService.duplicateScenario(scenario.id);
      showSuccess('Success', `Scenario "${scenario.name}" duplicated`);
      await fetchScenarios();
    } catch (error: any) {
      showError('Error', error.message || 'Failed to duplicate scenario');
    }
  };

  const handleSaveScenario = async () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Scenario name is required';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      const scenarioData = {
        name: formData.name,
        description: formData.description,
        threat_level: formData.threat_level,
        frequency_distribution: {
          type: formData.frequency_distribution,
          parameters: formData.frequency_params
        },
        severity_distribution: {
          type: formData.severity_distribution,
          parameters: formData.severity_params
        },
        industry_focus: formData.industry_focus
      };

      if (editingScenario) {
        await apiService.updateScenario(editingScenario.id, scenarioData);
        showSuccess('Success', 'Scenario updated successfully');
      } else {
        await apiService.createScenario(scenarioData);
        showSuccess('Success', 'Scenario created successfully');
      }
      
      setShowModal(false);
      await fetchScenarios();
    } catch (error: any) {
      showError('Error', error.message || 'Failed to save scenario');
    }
  };

  const handleCompareScenarios = async () => {
    if (selectedScenarios.length < 2) {
      showError('Selection Error', 'Please select at least 2 scenarios to compare');
      return;
    }

    try {
      const comparisonData = await apiService.compareScenarios(selectedScenarios);
      setComparison(comparisonData);
      setShowComparison(true);
    } catch (error: any) {
      showError('Error', error.message || 'Failed to compare scenarios');
    }
  };

  const handleSelectScenario = (scenarioId: string) => {
    setSelectedScenarios(prev => {
      if (prev.includes(scenarioId)) {
        return prev.filter(id => id !== scenarioId);
      } else {
        return [...prev, scenarioId];
      }
    });
  };

  const handleRunSimulation = (scenario: Scenario) => {
    navigate(`/simulation?scenario=${scenario.id}`);
  };

  const applyTemplate = (template: any) => {
    setFormData(prev => ({
      ...prev,
      name: template.name,
      description: template.description,
      threat_level: template.threat_level,
      frequency_distribution: template.frequency.distribution,
      frequency_params: template.frequency,
      severity_distribution: template.severity.distribution,
      severity_params: template.severity,
      industry_focus: template.industry_focus
    }));
    showInfo('Template Applied', `${template.name} parameters loaded`);
  };

  const formatThreatLevel = (level: string): { color: string; emoji: string } => {
    switch (level) {
      case 'high': return { color: '#ef4444', emoji: '🔴' };
      case 'medium': return { color: '#f59e0b', emoji: '🟡' };
      case 'low': return { color: '#10b981', emoji: '🟢' };
      default: return { color: '#6b7280', emoji: '⚪' };
    }
  };

  // Mock comparison chart data
  const comparisonChartData = {
    labels: selectedScenarios.slice(0, 5).map(id => {
      const scenario = scenarios.find(s => s.id === id);
      return scenario?.name || 'Unknown';
    }),
    datasets: [
      {
        label: 'Expected Loss',
        data: selectedScenarios.slice(0, 5).map(() => Math.random() * 2000000 + 500000),
        backgroundColor: 'rgba(102, 126, 234, 0.6)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 1,
      },
      {
        label: 'VaR 95%',
        data: selectedScenarios.slice(0, 5).map(() => Math.random() * 5000000 + 1000000),
        backgroundColor: 'rgba(239, 68, 68, 0.6)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1,
      },
    ],
  };

  const riskProfileData = {
    labels: ['Frequency', 'Severity', 'Impact', 'Recovery Time', 'Detection Rate'],
    datasets: selectedScenarios.slice(0, 3).map((id, index) => {
      const scenario = scenarios.find(s => s.id === id);
      const colors = ['#667eea', '#ef4444', '#10b981'];
      return {
        label: scenario?.name || 'Unknown',
        data: [
          Math.random() * 10 + 1,
          Math.random() * 10 + 1,
          Math.random() * 10 + 1,
          Math.random() * 10 + 1,
          Math.random() * 10 + 1,
        ],
        backgroundColor: `${colors[index]}20`,
        borderColor: colors[index],
        pointBackgroundColor: colors[index],
        pointBorderColor: colors[index],
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: colors[index],
      };
    }),
  };

  if (loading) {
    return (
      <ScenariosContainer>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
          <LoadingSpinner size="lg" text="Loading scenarios..." />
        </div>
      </ScenariosContainer>
    );
  }

  return (
    <ScenariosContainer>
      <Header>
        <Title>📋 Scenario Analysis</Title>
        <ActionButtons>
          <Button 
            variant="secondary" 
            onClick={handleCompareScenarios}
            disabled={selectedScenarios.length < 2}
          >
            📊 Compare Selected ({selectedScenarios.length})
          </Button>
          <Button onClick={handleCreateScenario}>
            ➕ New Scenario
          </Button>
        </ActionButtons>
      </Header>

      <ContentGrid>
        <MainContent>
          <Card>
            <CardHeader>
              <CardTitle>Risk Scenarios</CardTitle>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: '#718096' }}>
                  {selectedScenarios.length} selected
                </span>
                {selectedScenarios.length > 0 && (
                  <Button 
                    variant="secondary" 
                    onClick={() => setSelectedScenarios([])}
                    style={{ padding: '0.5rem', fontSize: '0.75rem' }}
                  >
                    Clear
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {scenarios.length === 0 ? (
                <EmptyState>
                  <EmptyIcon>📋</EmptyIcon>
                  <EmptyTitle>No Scenarios Yet</EmptyTitle>
                  <EmptyText>
                    Create risk scenarios to analyze different cyber threat patterns and compare their potential impact.
                  </EmptyText>
                  <Button onClick={handleCreateScenario}>
                    ➕ Create First Scenario
                  </Button>
                </EmptyState>
              ) : (
                <ScenarioGrid>
                  {scenarios.map((scenario) => {
                    const threatFormat = formatThreatLevel(scenario.threat_level || 'medium');
                    const isSelected = selectedScenarios.includes(scenario.id);
                    
                    return (
                      <ScenarioCard
                        key={scenario.id}
                        isActive={scenario.is_active}
                        isSelected={isSelected}
                        onClick={() => handleSelectScenario(scenario.id)}
                      >
                        <ScenarioBadge type={scenario.is_template ? 'template' : scenario.is_active ? 'active' : 'custom'}>
                          {scenario.is_active ? 'Active' : scenario.is_template ? 'Template' : 'Custom'}
                        </ScenarioBadge>

                        <ScenarioName>{scenario.name}</ScenarioName>
                        <ScenarioDescription>
                          {scenario.description || 'No description provided'}
                        </ScenarioDescription>

                        <ScenarioStats>
                          <StatItem>
                            <StatValue>{threatFormat.emoji}</StatValue>
                            <StatLabel>Threat Level</StatLabel>
                          </StatItem>
                          <StatItem>
                            <StatValue style={{ color: threatFormat.color }}>
                              {(scenario.threat_level || 'medium').toUpperCase()}
                            </StatValue>
                            <StatLabel>Risk Rating</StatLabel>
                          </StatItem>
                        </ScenarioStats>

                        <ScenarioActions onClick={e => e.stopPropagation()}>
                          <IconButton
                            onClick={() => handleRunSimulation(scenario)}
                            title="Run Simulation"
                          >
                            🎯
                          </IconButton>
                          <IconButton
                            onClick={() => handleEditScenario(scenario)}
                            title="Edit Scenario"
                          >
                            ✏️
                          </IconButton>
                          <IconButton
                            onClick={() => handleDuplicateScenario(scenario)}
                            title="Duplicate Scenario"
                          >
                            📋
                          </IconButton>
                          {scenario.is_active ? (
                            <IconButton
                              onClick={() => handleDeactivateScenario(scenario)}
                              title="Deactivate Scenario"
                            >
                              ⏸️
                            </IconButton>
                          ) : (
                            <IconButton
                              onClick={() => handleActivateScenario(scenario)}
                              title="Activate Scenario"
                            >
                              ▶️
                            </IconButton>
                          )}
                          <IconButton
                            onClick={() => handleDeleteScenario(scenario)}
                            title="Delete Scenario"
                          >
                            🗑️
                          </IconButton>
                        </ScenarioActions>
                      </ScenarioCard>
                    );
                  })}
                </ScenarioGrid>
              )}
            </CardContent>
          </Card>

          {showComparison && selectedScenarios.length >= 2 && (
            <ComparisonSection>
              <Card>
                <CardHeader>
                  <CardTitle>Scenario Comparison</CardTitle>
                  <Button variant="secondary" onClick={() => setShowComparison(false)}>
                    Close
                  </Button>
                </CardHeader>
                <CardContent>
                  <ComparisonGrid>
                    <div>
                      <h4 style={{ marginBottom: '1rem' }}>Risk Metrics Comparison</h4>
                      <ChartContainer>
                        <Bar data={comparisonChartData} options={{ responsive: true, maintainAspectRatio: false }} />
                      </ChartContainer>
                    </div>
                    <div>
                      <h4 style={{ marginBottom: '1rem' }}>Risk Profile Radar</h4>
                      <ChartContainer>
                        <Radar data={riskProfileData} options={{ responsive: true, maintainAspectRatio: false }} />
                      </ChartContainer>
                    </div>
                  </ComparisonGrid>
                </CardContent>
              </Card>
            </ComparisonSection>
          )}
        </MainContent>

        <SidePanel>
          <Card>
            <CardHeader>
              <CardTitle>Quick Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <StatItem style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <span style={{ color: '#718096', fontSize: '0.875rem' }}>Total Scenarios</span>
                  <span style={{ fontWeight: 600, color: '#2d3748' }}>{scenarios.length}</span>
                </StatItem>
                <StatItem style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <span style={{ color: '#718096', fontSize: '0.875rem' }}>Active Scenarios</span>
                  <span style={{ fontWeight: 600, color: '#10b981' }}>
                    {scenarios.filter(s => s.is_active).length}
                  </span>
                </StatItem>
                <StatItem style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <span style={{ color: '#718096', fontSize: '0.875rem' }}>High Risk</span>
                  <span style={{ fontWeight: 600, color: '#ef4444' }}>
                    {scenarios.filter(s => s.threat_level === 'high').length}
                  </span>
                </StatItem>
                <StatItem style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <span style={{ color: '#718096', fontSize: '0.875rem' }}>Selected</span>
                  <span style={{ fontWeight: 600, color: '#667eea' }}>{selectedScenarios.length}</span>
                </StatItem>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Scenario Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <TemplateGrid>
                {scenarioTemplates.slice(0, 4).map((template) => (
                  <TemplateCard key={template.id} onClick={() => applyTemplate(template)}>
                    <TemplateTitle>{template.name}</TemplateTitle>
                    <TemplateDescription>{template.description}</TemplateDescription>
                  </TemplateCard>
                ))}
              </TemplateGrid>
              <Button 
                variant="secondary" 
                onClick={handleCreateScenario}
                style={{ width: '100%', marginTop: '1rem' }}
              >
                View All Templates
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <Button 
                  variant="secondary" 
                  onClick={() => navigate('/simulation')}
                  style={{ justifyContent: 'flex-start' }}
                >
                  🎯 Run Simulation
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={handleCreateScenario}
                  style={{ justifyContent: 'flex-start' }}
                >
                  ➕ Create Scenario
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={() => showInfo('Export', 'Export functionality coming soon')}
                  style={{ justifyContent: 'flex-start' }}
                >
                  📄 Export Scenarios
                </Button>
              </div>
            </CardContent>
          </Card>
        </SidePanel>
      </ContentGrid>

      {/* Scenario Creation/Edit Modal */}
      <Modal isOpen={showModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>
              {editingScenario ? 'Edit Scenario' : 'Create New Scenario'}
            </ModalTitle>
            <CloseButton onClick={() => setShowModal(false)}>×</CloseButton>
          </ModalHeader>

          <FormGrid>
            <FormGroup>
              <Label>Scenario Name *</Label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Advanced Persistent Threat"
                hasError={!!errors.name}
              />
              {errors.name && <ErrorText>{errors.name}</ErrorText>}
            </FormGroup>

            <FormGroup>
              <Label>Threat Level</Label>
              <Select
                value={formData.threat_level}
                onChange={(e) => setFormData(prev => ({ ...prev, threat_level: e.target.value }))}
              >
                <option value="low">🟢 Low</option>
                <option value="medium">🟡 Medium</option>
                <option value="high">🔴 High</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>Frequency Distribution</Label>
              <Select
                value={formData.frequency_distribution}
                onChange={(e) => setFormData(prev => ({ ...prev, frequency_distribution: e.target.value }))}
              >
                <option value="poisson">Poisson</option>
                <option value="negative_binomial">Negative Binomial</option>
                <option value="binomial">Binomial</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>Severity Distribution</Label>
              <Select
                value={formData.severity_distribution}
                onChange={(e) => setFormData(prev => ({ ...prev, severity_distribution: e.target.value }))}
              >
                <option value="lognormal">Log-Normal</option>
                <option value="pareto">Pareto</option>
                <option value="gamma">Gamma</option>
                <option value="exponential">Exponential</option>
                <option value="weibull">Weibull</option>
              </Select>
            </FormGroup>
          </FormGrid>

          <FormGroup style={{ marginTop: '1rem' }}>
            <Label>Description</Label>
            <Textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe this risk scenario..."
            />
          </FormGroup>

          <FormGroup style={{ marginTop: '1rem' }}>
            <Label>Industry Focus</Label>
            <CheckboxGroup>
              {['technology', 'healthcare', 'finance', 'manufacturing', 'retail', 'government', 'education'].map(industry => (
                <CheckboxItem key={industry}>
                  <Checkbox
                    type="checkbox"
                    checked={formData.industry_focus.includes(industry)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData(prev => ({
                          ...prev,
                          industry_focus: [...prev.industry_focus, industry]
                        }));
                      } else {
                        setFormData(prev => ({
                          ...prev,
                          industry_focus: prev.industry_focus.filter(i => i !== industry)
                        }));
                      }
                    }}
                  />
                  {industry.charAt(0).toUpperCase() + industry.slice(1)}
                </CheckboxItem>
              ))}
            </CheckboxGroup>
          </FormGroup>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveScenario}>
              {editingScenario ? 'Update Scenario' : 'Create Scenario'}
            </Button>
          </div>
        </ModalContent>
      </Modal>
    </ScenariosContainer>
  );
};

export default ScenariosPage; 