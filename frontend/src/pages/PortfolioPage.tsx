import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { Portfolio, Policy, PortfolioSummary } from '../types';
import apiService from '../services/api';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { useNotificationStore } from '../store/notificationStore';

const PortfolioContainer = styled.div`
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
  grid-template-columns: 1fr 350px;
  gap: 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const MainContent = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const SidePanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const StatsPanel = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
`;

const StatItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f7fafc;
  
  &:last-child {
    border-bottom: none;
  }
`;

const StatLabel = styled.span`
  color: #718096;
  font-size: 0.875rem;
`;

const StatValue = styled.span<{ color?: string }>`
  font-weight: 600;
  color: ${({ color }) => color || '#2d3748'};
`;

const TabsContainer = styled.div`
  border-bottom: 1px solid #e2e8f0;
`;

const TabsList = styled.div`
  display: flex;
  gap: 2rem;
  padding: 0 1.5rem;
`;

const Tab = styled.button<{ active: boolean }>`
  background: none;
  border: none;
  padding: 1rem 0;
  font-weight: 600;
  color: ${({ active }) => active ? '#667eea' : '#718096'};
  border-bottom: 2px solid ${({ active }) => active ? '#667eea' : 'transparent'};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    color: #667eea;
  }
`;

const TabContent = styled.div`
  padding: 1.5rem;
`;

const PortfolioGrid = styled.div`
  display: grid;
  gap: 1rem;
`;

const PortfolioCard = styled.div`
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s ease;
  cursor: pointer;
  
  &:hover {
    border-color: #667eea;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  }
`;

const PortfolioHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
`;

const PortfolioName = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
`;

const PortfolioDescription = styled.p`
  color: #718096;
  font-size: 0.875rem;
  line-height: 1.4;
`;

const PortfolioActions = styled.div`
  display: flex;
  gap: 0.5rem;
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

const PortfolioStats = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const StatBox = styled.div`
  background: #f7fafc;
  padding: 0.75rem;
  border-radius: 0.5rem;
  text-align: center;
`;

const StatNumber = styled.div`
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
`;

const StatText = styled.div`
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
`;

const PolicyTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.th`
  text-align: left;
  padding: 0.75rem;
  background: #f7fafc;
  color: #4a5568;
  font-weight: 600;
  font-size: 0.875rem;
  border-bottom: 1px solid #e2e8f0;
`;

const TableRow = styled.tr`
  border-bottom: 1px solid #f7fafc;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: #f7fafc;
  }
`;

const TableCell = styled.td`
  padding: 0.75rem;
  color: #4a5568;
  font-size: 0.875rem;
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

interface PortfolioFormData {
  name: string;
  description: string;
  industry: string;
  total_value: number;
}

interface PolicyFormData {
  name: string;
  limit: number;
  deductible: number;
  premium: number;
  coverage_type: string;
  inception_date: string;
  expiry_date: string;
}

const PortfolioPage: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess, showError, showInfo } = useNotificationStore();
  
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('portfolios');
  
  // Modal states
  const [showPortfolioModal, setShowPortfolioModal] = useState(false);
  const [showPolicyModal, setShowPolicyModal] = useState(false);
  const [editingPortfolio, setEditingPortfolio] = useState<Portfolio | null>(null);
  const [editingPolicy, setEditingPolicy] = useState<Policy | null>(null);
  
  // Form states
  const [portfolioForm, setPortfolioForm] = useState<PortfolioFormData>({
    name: '',
    description: '',
    industry: '',
    total_value: 0
  });
  
  const [policyForm, setPolicyForm] = useState<PolicyFormData>({
    name: '',
    limit: 0,
    deductible: 0,
    premium: 0,
    coverage_type: 'cyber',
    inception_date: '',
    expiry_date: ''
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchPortfolios();
  }, []);

  useEffect(() => {
    if (selectedPortfolio) {
      fetchPortfolioPolicies(selectedPortfolio.id);
      fetchPortfolioSummary(selectedPortfolio.id);
    }
  }, [selectedPortfolio]);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPortfolios();
      setPortfolios(data);
      if (data.length > 0 && !selectedPortfolio) {
        setSelectedPortfolio(data[0]);
      }
    } catch (error) {
      showError('Error', 'Failed to load portfolios');
    } finally {
      setLoading(false);
    }
  };

  const fetchPortfolioPolicies = async (portfolioId: string) => {
    try {
      const data = await apiService.getPortfolioPolicies(portfolioId);
      setPolicies(data);
    } catch (error) {
      showError('Error', 'Failed to load portfolio policies');
    }
  };

  const fetchPortfolioSummary = async (portfolioId: string) => {
    try {
      const data = await apiService.getPortfolioSummary(portfolioId);
      setSummary(data);
    } catch (error) {
      console.warn('Could not fetch portfolio summary');
    }
  };

  const handleCreatePortfolio = () => {
    setEditingPortfolio(null);
    setPortfolioForm({
      name: '',
      description: '',
      industry: '',
      total_value: 0
    });
    setErrors({});
    setShowPortfolioModal(true);
  };

  const handleEditPortfolio = (portfolio: Portfolio) => {
    setEditingPortfolio(portfolio);
    setPortfolioForm({
      name: portfolio.name,
      description: portfolio.description || '',
      industry: portfolio.industry || '',
      total_value: portfolio.total_value
    });
    setErrors({});
    setShowPortfolioModal(true);
  };

  const handleDeletePortfolio = async (portfolio: Portfolio) => {
    if (!window.confirm(`Delete portfolio "${portfolio.name}"? This cannot be undone.`)) {
      return;
    }

    try {
      await apiService.deletePortfolio(portfolio.id);
      showSuccess('Success', 'Portfolio deleted successfully');
      await fetchPortfolios();
      if (selectedPortfolio?.id === portfolio.id) {
        setSelectedPortfolio(portfolios[0] || null);
      }
    } catch (error: any) {
      showError('Error', error.message || 'Failed to delete portfolio');
    }
  };

  const handleSavePortfolio = async () => {
    const newErrors: Record<string, string> = {};

    if (!portfolioForm.name.trim()) {
      newErrors.name = 'Portfolio name is required';
    }

    if (portfolioForm.total_value <= 0) {
      newErrors.total_value = 'Total value must be positive';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      if (editingPortfolio) {
        await apiService.updatePortfolio(editingPortfolio.id, portfolioForm);
        showSuccess('Success', 'Portfolio updated successfully');
      } else {
        await apiService.createPortfolio(portfolioForm);
        showSuccess('Success', 'Portfolio created successfully');
      }
      
      setShowPortfolioModal(false);
      await fetchPortfolios();
    } catch (error: any) {
      showError('Error', error.message || 'Failed to save portfolio');
    }
  };

  const handleCreatePolicy = () => {
    if (!selectedPortfolio) return;
    
    setEditingPolicy(null);
    setPolicyForm({
      name: '',
      limit: 0,
      deductible: 0,
      premium: 0,
      coverage_type: 'cyber',
      inception_date: new Date().toISOString().split('T')[0],
      expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    });
    setErrors({});
    setShowPolicyModal(true);
  };

  const handleEditPolicy = (policy: Policy) => {
    setEditingPolicy(policy);
    setPolicyForm({
      name: policy.name,
      limit: policy.limit,
      deductible: policy.deductible,
      premium: policy.premium,
      coverage_type: policy.coverage_type,
      inception_date: policy.inception_date.split('T')[0],
      expiry_date: policy.expiry_date.split('T')[0]
    });
    setErrors({});
    setShowPolicyModal(true);
  };

  const handleDeletePolicy = async (policy: Policy) => {
    if (!window.confirm(`Delete policy "${policy.name}"? This cannot be undone.`)) {
      return;
    }

    try {
      await apiService.deletePolicy(selectedPortfolio!.id, policy.id);
      showSuccess('Success', 'Policy deleted successfully');
      await fetchPortfolioPolicies(selectedPortfolio!.id);
      await fetchPortfolioSummary(selectedPortfolio!.id);
    } catch (error: any) {
      showError('Error', error.message || 'Failed to delete policy');
    }
  };

  const handleSavePolicy = async () => {
    if (!selectedPortfolio) return;

    const newErrors: Record<string, string> = {};

    if (!policyForm.name.trim()) {
      newErrors.name = 'Policy name is required';
    }

    if (policyForm.limit <= 0) {
      newErrors.limit = 'Policy limit must be positive';
    }

    if (policyForm.deductible < 0) {
      newErrors.deductible = 'Deductible cannot be negative';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      const policyData = {
        ...policyForm,
        portfolio_id: selectedPortfolio.id
      };

      if (editingPolicy) {
        await apiService.updatePolicy(selectedPortfolio.id, editingPolicy.id, policyData);
        showSuccess('Success', 'Policy updated successfully');
      } else {
        await apiService.createPolicy(selectedPortfolio.id, policyData);
        showSuccess('Success', 'Policy created successfully');
      }
      
      setShowPolicyModal(false);
      await fetchPortfolioPolicies(selectedPortfolio.id);
      await fetchPortfolioSummary(selectedPortfolio.id);
    } catch (error: any) {
      showError('Error', error.message || 'Failed to save policy');
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <PortfolioContainer>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
          <LoadingSpinner size="lg" text="Loading portfolios..." />
        </div>
      </PortfolioContainer>
    );
  }

  return (
    <PortfolioContainer>
      <Header>
        <Title>💼 Portfolio Management</Title>
        <ActionButtons>
          <Button variant="secondary" onClick={() => navigate('/simulation')}>
            🎯 Run Simulation
          </Button>
          <Button onClick={handleCreatePortfolio}>
            ➕ New Portfolio
          </Button>
        </ActionButtons>
      </Header>

      <ContentGrid>
        <MainContent>
          <TabsContainer>
            <TabsList>
              <Tab active={activeTab === 'portfolios'} onClick={() => setActiveTab('portfolios')}>
                📁 Portfolios ({portfolios.length})
              </Tab>
              <Tab 
                active={activeTab === 'policies'} 
                onClick={() => setActiveTab('policies')}
                disabled={!selectedPortfolio}
              >
                📋 Policies ({policies.length})
              </Tab>
            </TabsList>
          </TabsContainer>

          <TabContent>
            {activeTab === 'portfolios' && (
              <div>
                {portfolios.length === 0 ? (
                  <EmptyState>
                    <EmptyIcon>📁</EmptyIcon>
                    <EmptyTitle>No Portfolios Yet</EmptyTitle>
                    <EmptyText>
                      Create your first portfolio to start managing your cyber risk policies and run simulations.
                    </EmptyText>
                    <Button onClick={handleCreatePortfolio}>
                      ➕ Create First Portfolio
                    </Button>
                  </EmptyState>
                ) : (
                  <PortfolioGrid>
                    {portfolios.map((portfolio) => (
                      <PortfolioCard
                        key={portfolio.id}
                        onClick={() => setSelectedPortfolio(portfolio)}
                        style={{
                          borderColor: selectedPortfolio?.id === portfolio.id ? '#667eea' : undefined,
                          backgroundColor: selectedPortfolio?.id === portfolio.id ? '#f7fafc' : undefined
                        }}
                      >
                        <PortfolioHeader>
                          <div>
                            <PortfolioName>{portfolio.name}</PortfolioName>
                            <PortfolioDescription>
                              {portfolio.description || 'No description provided'}
                            </PortfolioDescription>
                          </div>
                          <PortfolioActions>
                            <IconButton onClick={(e) => { e.stopPropagation(); handleEditPortfolio(portfolio); }}>
                              ✏️
                            </IconButton>
                            <IconButton onClick={(e) => { e.stopPropagation(); handleDeletePortfolio(portfolio); }}>
                              🗑️
                            </IconButton>
                          </PortfolioActions>
                        </PortfolioHeader>

                        <PortfolioStats>
                          <StatBox>
                            <StatNumber>{formatCurrency(portfolio.total_value)}</StatNumber>
                            <StatText>Total Value</StatText>
                          </StatBox>
                          <StatBox>
                            <StatNumber>{portfolio.policy_count || 0}</StatNumber>
                            <StatText>Policies</StatText>
                          </StatBox>
                          <StatBox>
                            <StatNumber>{portfolio.industry || 'General'}</StatNumber>
                            <StatText>Industry</StatText>
                          </StatBox>
                        </PortfolioStats>
                      </PortfolioCard>
                    ))}
                  </PortfolioGrid>
                )}
              </div>
            )}

            {activeTab === 'policies' && selectedPortfolio && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h3 style={{ color: '#2d3748', margin: 0 }}>
                    Policies for {selectedPortfolio.name}
                  </h3>
                  <Button onClick={handleCreatePolicy}>
                    ➕ Add Policy
                  </Button>
                </div>

                {policies.length === 0 ? (
                  <EmptyState>
                    <EmptyIcon>📋</EmptyIcon>
                    <EmptyTitle>No Policies Yet</EmptyTitle>
                    <EmptyText>
                      Add policies to this portfolio to define coverage limits and deductibles for your simulations.
                    </EmptyText>
                    <Button onClick={handleCreatePolicy}>
                      ➕ Add First Policy
                    </Button>
                  </EmptyState>
                ) : (
                  <PolicyTable>
                    <thead>
                      <tr>
                        <TableHeader>Policy Name</TableHeader>
                        <TableHeader>Coverage Type</TableHeader>
                        <TableHeader>Limit</TableHeader>
                        <TableHeader>Deductible</TableHeader>
                        <TableHeader>Premium</TableHeader>
                        <TableHeader>Period</TableHeader>
                        <TableHeader>Actions</TableHeader>
                      </tr>
                    </thead>
                    <tbody>
                      {policies.map((policy) => (
                        <TableRow key={policy.id}>
                          <TableCell style={{ fontWeight: 600 }}>{policy.name}</TableCell>
                          <TableCell style={{ textTransform: 'capitalize' }}>{policy.coverage_type}</TableCell>
                          <TableCell>{formatCurrency(policy.limit)}</TableCell>
                          <TableCell>{formatCurrency(policy.deductible)}</TableCell>
                          <TableCell>{formatCurrency(policy.premium)}</TableCell>
                          <TableCell>
                            {formatDate(policy.inception_date)} - {formatDate(policy.expiry_date)}
                          </TableCell>
                          <TableCell>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                              <IconButton onClick={() => handleEditPolicy(policy)}>✏️</IconButton>
                              <IconButton onClick={() => handleDeletePolicy(policy)}>🗑️</IconButton>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </tbody>
                  </PolicyTable>
                )}
              </div>
            )}
          </TabContent>
        </MainContent>

        <SidePanel>
          {selectedPortfolio && (
            <StatsPanel>
              <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>Portfolio Summary</h3>
              <StatItem>
                <StatLabel>Total Value</StatLabel>
                <StatValue color="#667eea">
                  {formatCurrency(selectedPortfolio.total_value)}
                </StatValue>
              </StatItem>
              <StatItem>
                <StatLabel>Active Policies</StatLabel>
                <StatValue>{policies.length}</StatValue>
              </StatItem>
              <StatItem>
                <StatLabel>Total Premium</StatLabel>
                <StatValue color="#10b981">
                  {formatCurrency(policies.reduce((sum, p) => sum + p.premium, 0))}
                </StatValue>
              </StatItem>
              <StatItem>
                <StatLabel>Total Coverage</StatLabel>
                <StatValue color="#f59e0b">
                  {formatCurrency(policies.reduce((sum, p) => sum + p.limit, 0))}
                </StatValue>
              </StatItem>
              {summary && (
                <>
                  <StatItem>
                    <StatLabel>Avg Deductible</StatLabel>
                    <StatValue>{formatCurrency(summary.average_deductible)}</StatValue>
                  </StatItem>
                  <StatItem>
                    <StatLabel>Risk Score</StatLabel>
                    <StatValue color="#ef4444">{summary.risk_score?.toFixed(1) || 'N/A'}</StatValue>
                  </StatItem>
                </>
              )}
            </StatsPanel>
          )}

          <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', padding: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>Quick Actions</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <Button 
                variant="secondary" 
                onClick={() => navigate('/simulation')}
                disabled={!selectedPortfolio}
                style={{ justifyContent: 'flex-start' }}
              >
                🎯 Run Simulation
              </Button>
              <Button 
                variant="secondary" 
                onClick={() => selectedPortfolio && navigate(`/results?portfolio=${selectedPortfolio.id}`)}
                disabled={!selectedPortfolio}
                style={{ justifyContent: 'flex-start' }}
              >
                📊 View Results
              </Button>
              <Button 
                variant="secondary" 
                onClick={() => showInfo('Export', 'Export functionality coming soon')}
                disabled={!selectedPortfolio}
                style={{ justifyContent: 'flex-start' }}
              >
                📄 Export Data
              </Button>
            </div>
          </div>
        </SidePanel>
      </ContentGrid>

      {/* Portfolio Modal */}
      <Modal isOpen={showPortfolioModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>
              {editingPortfolio ? 'Edit Portfolio' : 'Create New Portfolio'}
            </ModalTitle>
            <CloseButton onClick={() => setShowPortfolioModal(false)}>×</CloseButton>
          </ModalHeader>

          <FormGrid>
            <FormGroup>
              <Label>Portfolio Name *</Label>
              <Input
                type="text"
                value={portfolioForm.name}
                onChange={(e) => setPortfolioForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Tech Company Portfolio"
                hasError={!!errors.name}
              />
              {errors.name && <ErrorText>{errors.name}</ErrorText>}
            </FormGroup>

            <FormGroup>
              <Label>Industry</Label>
              <Input
                type="text"
                value={portfolioForm.industry}
                onChange={(e) => setPortfolioForm(prev => ({ ...prev, industry: e.target.value }))}
                placeholder="e.g., Technology, Healthcare"
              />
            </FormGroup>

            <FormGroup>
              <Label>Total Value *</Label>
              <Input
                type="number"
                value={portfolioForm.total_value}
                onChange={(e) => setPortfolioForm(prev => ({ ...prev, total_value: parseFloat(e.target.value) || 0 }))}
                placeholder="10000000"
                min="0"
                step="100000"
                hasError={!!errors.total_value}
              />
              {errors.total_value && <ErrorText>{errors.total_value}</ErrorText>}
            </FormGroup>
          </FormGrid>

          <FormGroup style={{ marginTop: '1rem' }}>
            <Label>Description</Label>
            <Textarea
              value={portfolioForm.description}
              onChange={(e) => setPortfolioForm(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe this portfolio..."
            />
          </FormGroup>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
            <Button variant="secondary" onClick={() => setShowPortfolioModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleSavePortfolio}>
              {editingPortfolio ? 'Update Portfolio' : 'Create Portfolio'}
            </Button>
          </div>
        </ModalContent>
      </Modal>

      {/* Policy Modal */}
      <Modal isOpen={showPolicyModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>
              {editingPolicy ? 'Edit Policy' : 'Add New Policy'}
            </ModalTitle>
            <CloseButton onClick={() => setShowPolicyModal(false)}>×</CloseButton>
          </ModalHeader>

          <FormGrid>
            <FormGroup>
              <Label>Policy Name *</Label>
              <Input
                type="text"
                value={policyForm.name}
                onChange={(e) => setPolicyForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Cyber Liability Policy"
                hasError={!!errors.name}
              />
              {errors.name && <ErrorText>{errors.name}</ErrorText>}
            </FormGroup>

            <FormGroup>
              <Label>Coverage Type</Label>
              <select
                value={policyForm.coverage_type}
                onChange={(e) => setPolicyForm(prev => ({ ...prev, coverage_type: e.target.value }))}
                style={{ padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', fontSize: '1rem' }}
              >
                <option value="cyber">Cyber Liability</option>
                <option value="data_breach">Data Breach</option>
                <option value="errors_omissions">Errors & Omissions</option>
                <option value="general_liability">General Liability</option>
                <option value="other">Other</option>
              </select>
            </FormGroup>

            <FormGroup>
              <Label>Policy Limit *</Label>
              <Input
                type="number"
                value={policyForm.limit}
                onChange={(e) => setPolicyForm(prev => ({ ...prev, limit: parseFloat(e.target.value) || 0 }))}
                placeholder="5000000"
                min="0"
                step="100000"
                hasError={!!errors.limit}
              />
              {errors.limit && <ErrorText>{errors.limit}</ErrorText>}
            </FormGroup>

            <FormGroup>
              <Label>Deductible</Label>
              <Input
                type="number"
                value={policyForm.deductible}
                onChange={(e) => setPolicyForm(prev => ({ ...prev, deductible: parseFloat(e.target.value) || 0 }))}
                placeholder="50000"
                min="0"
                step="10000"
                hasError={!!errors.deductible}
              />
              {errors.deductible && <ErrorText>{errors.deductible}</ErrorText>}
            </FormGroup>

            <FormGroup>
              <Label>Annual Premium</Label>
              <Input
                type="number"
                value={policyForm.premium}
                onChange={(e) => setPolicyForm(prev => ({ ...prev, premium: parseFloat(e.target.value) || 0 }))}
                placeholder="100000"
                min="0"
                step="1000"
              />
            </FormGroup>

            <FormGroup>
              <Label>Inception Date</Label>
              <Input
                type="date"
                value={policyForm.inception_date}
                onChange={(e) => setPolicyForm(prev => ({ ...prev, inception_date: e.target.value }))}
              />
            </FormGroup>

            <FormGroup>
              <Label>Expiry Date</Label>
              <Input
                type="date"
                value={policyForm.expiry_date}
                onChange={(e) => setPolicyForm(prev => ({ ...prev, expiry_date: e.target.value }))}
              />
            </FormGroup>
          </FormGrid>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
            <Button variant="secondary" onClick={() => setShowPolicyModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleSavePolicy}>
              {editingPolicy ? 'Update Policy' : 'Add Policy'}
            </Button>
          </div>
        </ModalContent>
      </Modal>
    </PortfolioContainer>
  );
};

export default PortfolioPage; 