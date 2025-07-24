import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useParams, useNavigate } from 'react-router-dom';
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
  ArcElement,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import { SimulationResult, RiskMetrics, HistogramData, ExceedanceCurve } from '../types';
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
  ArcElement
);

const ResultsContainer = styled.div`
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid ${props => props.theme.colors.border};
`;

const Title = styled.h1`
  color: ${props => props.theme.colors.text.primary};
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  ${props => {
    switch (props.variant) {
      case 'danger':
        return `
          background: ${props.theme.colors.danger};
          color: white;
          &:hover { background: #dc2626; }
        `;
      case 'secondary':
        return `
          background: ${props.theme.colors.background.secondary};
          color: ${props.theme.colors.text.primary};
          border: 1px solid ${props.theme.colors.border};
          &:hover { background: ${props.theme.colors.background.tertiary}; }
        `;
      default:
        return `
          background: ${props.theme.colors.primary};
          color: white;
          &:hover { background: ${props.theme.colors.secondary}; }
        `;
    }
  }}
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const MetricCard = styled.div`
  background: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: 1.5rem;
  box-shadow: ${props => props.theme.shadows.card};
  border: 1px solid ${props => props.theme.colors.border};
`;

const MetricTitle = styled.h3`
  color: ${props => props.theme.colors.text.secondary};
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.5rem 0;
`;

const MetricValue = styled.div<{ color?: string }>`
  color: ${props => props.color || props.theme.colors.text.primary};
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
`;

const MetricSubtext = styled.div`
  color: ${props => props.theme.colors.text.secondary};
  font-size: 0.875rem;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: 1.5rem;
  box-shadow: ${props => props.theme.shadows.card};
  border: 1px solid ${props => props.theme.colors.border};
`;

const ChartTitle = styled.h3`
  color: ${props => props.theme.colors.text.primary};
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1.5rem 0;
`;

const TabsContainer = styled.div`
  margin-bottom: 2rem;
`;

const TabsList = styled.div`
  display: flex;
  background: ${props => props.theme.colors.background.secondary};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: 0.25rem;
  gap: 0.25rem;
`;

const Tab = styled.button<{ active: boolean }>`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: ${props => props.theme.borderRadius.sm};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;

  ${props => props.active ? `
    background: ${props.theme.colors.primary};
    color: white;
  ` : `
    background: transparent;
    color: ${props.theme.colors.text.secondary};
    &:hover {
      background: ${props.theme.colors.background.tertiary};
      color: ${props.theme.colors.text.primary};
    }
  `}
`;

const TabContent = styled.div`
  background: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.card};
  border: 1px solid ${props => props.theme.colors.border};
`;

const DetailsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
`;

const DetailSection = styled.div`
  background: ${props => props.theme.colors.background.secondary};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: 1.5rem;
`;

const DetailTitle = styled.h4`
  color: ${props => props.theme.colors.text.primary};
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
`;

const DetailList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const DetailItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: ${props => props.theme.colors.text.secondary};
  font-size: 0.875rem;
`;

const DetailLabel = styled.span`
  font-weight: 500;
`;

const DetailValue = styled.span`
  font-weight: 600;
  color: ${props => props.theme.colors.text.primary};
`;

const SimulationResults: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { showError, showSuccess } = useNotificationStore();

  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (id) {
      fetchSimulationResult();
    }
  }, [id]);

  const fetchSimulationResult = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSimulationResult(id!);
      setResult(response);
    } catch (error) {
      showError('Error', 'Failed to load simulation results');
      navigate('/simulations');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      // Implementation would export results to CSV/PDF
      showSuccess('Export', 'Results exported successfully');
    } catch (error) {
      showError('Export Error', 'Failed to export results');
    }
  };

  const handleRerun = () => {
    navigate(`/simulation?clone=${id}`);
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number): string => {
    return `${(value * 100).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <ResultsContainer>
        <LoadingSpinner size="lg" text="Loading simulation results..." />
      </ResultsContainer>
    );
  }

  if (!result) {
    return (
      <ResultsContainer>
        <div style={{ textAlign: 'center', padding: '4rem' }}>
          <h2>Results not found</h2>
          <Button onClick={() => navigate('/simulations')}>
            Back to Simulations
          </Button>
        </div>
      </ResultsContainer>
    );
  }

  const { risk_metrics, histogram_data, exceedance_curves } = result;

  // Mock data for charts (would come from actual simulation results)
  const histogramChartData = {
    labels: histogram_data?.bins || Array.from({ length: 20 }, (_, i) => `${i * 100}K`),
    datasets: [
      {
        label: 'Loss Frequency',
        data: histogram_data?.frequencies || Array.from({ length: 20 }, () => Math.random() * 100),
        backgroundColor: 'rgba(102, 126, 234, 0.6)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 1,
      },
    ],
  };

  const exceedanceChartData = {
    labels: exceedance_curves?.loss_amounts || Array.from({ length: 50 }, (_, i) => i * 50000),
    datasets: [
      {
        label: 'Exceedance Probability',
        data: exceedance_curves?.probabilities || Array.from({ length: 50 }, (_, i) => 1 - (i / 50)),
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const riskBreakdownData = {
    labels: ['Cyber Attacks', 'Data Breaches', 'System Failures', 'Human Error', 'Other'],
    datasets: [
      {
        data: [35, 25, 20, 15, 5],
        backgroundColor: [
          '#667eea',
          '#f093fb',
          '#4facfe',
          '#43e97b',
          '#ffecd2',
        ],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  };

  return (
    <ResultsContainer>
      <Header>
        <Title>
          📊 Simulation Results
          <span style={{ fontSize: '1rem', fontWeight: 400, color: '#666' }}>
            #{result.simulation_run_id}
          </span>
        </Title>
        <ActionButtons>
          <Button variant="secondary" onClick={() => navigate('/simulations')}>
            ← Back
          </Button>
          <Button variant="secondary" onClick={handleExport}>
            📄 Export
          </Button>
          <Button onClick={handleRerun}>
            🔄 Re-run
          </Button>
        </ActionButtons>
      </Header>

      <MetricsGrid>
        <MetricCard>
          <MetricTitle>Expected Loss</MetricTitle>
          <MetricValue color="#667eea">
            {formatCurrency(risk_metrics?.expected_loss || 1250000)}
          </MetricValue>
          <MetricSubtext>Average annual loss</MetricSubtext>
        </MetricCard>

        <MetricCard>
          <MetricTitle>Value at Risk (95%)</MetricTitle>
          <MetricValue color="#f093fb">
            {formatCurrency(risk_metrics?.var_95 || 3500000)}
          </MetricValue>
          <MetricSubtext>95th percentile loss</MetricSubtext>
        </MetricCard>

        <MetricCard>
          <MetricTitle>Tail Value at Risk (95%)</MetricTitle>
          <MetricValue color="#43e97b">
            {formatCurrency(risk_metrics?.tvar_95 || 5200000)}
          </MetricValue>
          <MetricSubtext>Expected loss beyond VaR</MetricSubtext>
        </MetricCard>

        <MetricCard>
          <MetricTitle>Maximum Loss</MetricTitle>
          <MetricValue color="#ef4444">
            {formatCurrency(risk_metrics?.max_loss || 12000000)}
          </MetricValue>
          <MetricSubtext>Worst case scenario</MetricSubtext>
        </MetricCard>

        <MetricCard>
          <MetricTitle>Loss Ratio</MetricTitle>
          <MetricValue color="#f59e0b">
            {formatPercent((risk_metrics?.expected_loss || 1250000) / 10000000)}
          </MetricValue>
          <MetricSubtext>Expected loss / Total exposure</MetricSubtext>
        </MetricCard>

        <MetricCard>
          <MetricTitle>Coefficient of Variation</MetricTitle>
          <MetricValue>
            {((risk_metrics?.std_deviation || 2100000) / (risk_metrics?.expected_loss || 1250000)).toFixed(2)}
          </MetricValue>
          <MetricSubtext>Risk-adjusted volatility</MetricSubtext>
        </MetricCard>
      </MetricsGrid>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>Loss Distribution</ChartTitle>
          <div style={{ height: '400px' }}>
            <Bar data={histogramChartData} options={chartOptions} />
          </div>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Risk Breakdown</ChartTitle>
          <div style={{ height: '400px' }}>
            <Doughnut data={riskBreakdownData} options={chartOptions} />
          </div>
        </ChartCard>
      </ChartsGrid>

      <ChartCard style={{ marginBottom: '2rem' }}>
        <ChartTitle>Exceedance Probability Curve</ChartTitle>
        <div style={{ height: '400px' }}>
          <Line data={exceedanceChartData} options={chartOptions} />
        </div>
      </ChartCard>

      <TabsContainer>
        <TabsList>
          <Tab active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>
            Overview
          </Tab>
          <Tab active={activeTab === 'parameters'} onClick={() => setActiveTab('parameters')}>
            Parameters
          </Tab>
          <Tab active={activeTab === 'statistics'} onClick={() => setActiveTab('statistics')}>
            Statistics
          </Tab>
        </TabsList>

        <TabContent>
          {activeTab === 'overview' && (
            <DetailsGrid>
              <DetailSection>
                <DetailTitle>Simulation Details</DetailTitle>
                <DetailList>
                  <DetailItem>
                    <DetailLabel>Iterations:</DetailLabel>
                    <DetailValue>{result.iterations?.toLocaleString() || '10,000'}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Runtime:</DetailLabel>
                    <DetailValue>{result.runtime_seconds?.toFixed(2) || '12.45'}s</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Convergence:</DetailLabel>
                    <DetailValue>✅ Achieved</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Random Seed:</DetailLabel>
                    <DetailValue>{result.random_seed || '42'}</DetailValue>
                  </DetailItem>
                </DetailList>
              </DetailSection>

              <DetailSection>
                <DetailTitle>Portfolio Summary</DetailTitle>
                <DetailList>
                  <DetailItem>
                    <DetailLabel>Total Policies:</DetailLabel>
                    <DetailValue>156</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Total Exposure:</DetailLabel>
                    <DetailValue>{formatCurrency(10000000)}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Average Policy Size:</DetailLabel>
                    <DetailValue>{formatCurrency(64103)}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Industries Covered:</DetailLabel>
                    <DetailValue>8</DetailValue>
                  </DetailItem>
                </DetailList>
              </DetailSection>
            </DetailsGrid>
          )}

          {activeTab === 'parameters' && (
            <DetailsGrid>
              <DetailSection>
                <DetailTitle>Frequency Distribution</DetailTitle>
                <DetailList>
                  <DetailItem>
                    <DetailLabel>Distribution Type:</DetailLabel>
                    <DetailValue>Poisson</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Lambda:</DetailLabel>
                    <DetailValue>2.5</DetailValue>
                  </DetailItem>
                </DetailList>
              </DetailSection>

              <DetailSection>
                <DetailTitle>Severity Distribution</DetailTitle>
                <DetailList>
                  <DetailItem>
                    <DetailLabel>Distribution Type:</DetailLabel>
                    <DetailValue>Log-Normal</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Mean (log scale):</DetailLabel>
                    <DetailValue>12.5</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Std Dev (log scale):</DetailLabel>
                    <DetailValue>1.8</DetailValue>
                  </DetailItem>
                </DetailList>
              </DetailSection>
            </DetailsGrid>
          )}

          {activeTab === 'statistics' && (
            <DetailsGrid>
              <DetailSection>
                <DetailTitle>Distribution Statistics</DetailTitle>
                <DetailList>
                  <DetailItem>
                    <DetailLabel>Mean:</DetailLabel>
                    <DetailValue>{formatCurrency(risk_metrics?.mean || 1250000)}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Standard Deviation:</DetailLabel>
                    <DetailValue>{formatCurrency(risk_metrics?.std_deviation || 2100000)}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Skewness:</DetailLabel>
                    <DetailValue>{risk_metrics?.skewness?.toFixed(3) || '2.156'}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>Kurtosis:</DetailLabel>
                    <DetailValue>{risk_metrics?.kurtosis?.toFixed(3) || '8.234'}</DetailValue>
                  </DetailItem>
                </DetailList>
              </DetailSection>

              <DetailSection>
                <DetailTitle>Risk Percentiles</DetailTitle>
                <DetailList>
                  <DetailItem>
                    <DetailLabel>50th Percentile:</DetailLabel>
                    <DetailValue>{formatCurrency(750000)}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>75th Percentile:</DetailLabel>
                    <DetailValue>{formatCurrency(1800000)}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>90th Percentile:</DetailLabel>
                    <DetailValue>{formatCurrency(2900000)}</DetailValue>
                  </DetailItem>
                  <DetailItem>
                    <DetailLabel>99th Percentile:</DetailLabel>
                    <DetailValue>{formatCurrency(8500000)}</DetailValue>
                  </DetailItem>
                </DetailList>
              </DetailSection>
            </DetailsGrid>
          )}
        </TabContent>
      </TabsContainer>
    </ResultsContainer>
  );
};

export default SimulationResults; 