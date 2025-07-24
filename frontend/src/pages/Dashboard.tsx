import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import apiService from '../services/api';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const DashboardContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const WelcomeSection = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const WelcomeTitle = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
`;

const WelcomeSubtitle = styled.p`
  font-size: 1.125rem;
  opacity: 0.9;
  margin-bottom: 1.5rem;
`;

const QuickActions = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const StatIcon = styled.div<{ color: string }>`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: ${({ color }) => color};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 1rem;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.25rem;
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: #718096;
  font-weight: 500;
`;

const StatChange = styled.div<{ positive: boolean }>`
  font-size: 0.75rem;
  color: ${({ positive }) => positive ? '#48bb78' : '#f56565'};
  margin-top: 0.5rem;
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const CardTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
`;

const RecentActivity = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f7fafc;
  
  &:last-child {
    border-bottom: none;
  }
`;

const ActivityIcon = styled.div<{ type: string }>`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background-color: ${({ type }) => {
    switch (type) {
      case 'simulation': return '#e6fffa';
      case 'portfolio': return '#fef5e7';
      case 'scenario': return '#f0fff4';
      default: return '#f7fafc';
    }
  }};
  color: ${({ type }) => {
    switch (type) {
      case 'simulation': return '#319795';
      case 'portfolio': return '#d69e2e';
      case 'scenario': return '#38a169';
      default: return '#718096';
    }
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
`;

const ActivityContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const ActivityTitle = styled.div`
  font-weight: 500;
  color: #2d3748;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
`;

const ActivityTime = styled.div`
  font-size: 0.75rem;
  color: #718096;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem 2rem;
  color: #718096;
`;

const EmptyIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
`;

const EmptyText = styled.p`
  font-size: 1rem;
  margin-bottom: 1.5rem;
`;

interface DashboardStats {
  totalSimulations: number;
  totalPortfolios: number;
  totalPolicies: number;
  averageRisk: number;
}

interface ActivityItem {
  id: string;
  type: 'simulation' | 'portfolio' | 'scenario';
  title: string;
  time: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { showError } = useNotificationStore();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch user stats
      const userStats = await apiService.getUserStats();
      
      // Mock stats for now (replace with actual API data)
      setStats({
        totalSimulations: userStats?.simulations_count || 0,
        totalPortfolios: userStats?.portfolios_count || 0,
        totalPolicies: userStats?.policies_count || 0,
        averageRisk: userStats?.average_risk_score || 0,
      });

      // Mock recent activity (replace with actual API data)
      setRecentActivity([
        {
          id: '1',
          type: 'simulation',
          title: 'Monte Carlo Simulation completed',
          time: '2 hours ago'
        },
        {
          id: '2',
          type: 'portfolio',
          title: 'Portfolio "Tech Companies" updated',
          time: '4 hours ago'
        },
        {
          id: '3',
          type: 'scenario',
          title: 'Scenario "High Frequency Attack" created',
          time: '1 day ago'
        }
      ]);

    } catch (error: any) {
      showError('Failed to load dashboard', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getActivityIcon = (type: string): string => {
    switch (type) {
      case 'simulation': return '🎯';
      case 'portfolio': return '💼';
      case 'scenario': return '📋';
      default: return '📊';
    }
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat().format(num);
  };

  if (isLoading) {
    return (
      <DashboardContainer>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
          <LoadingSpinner size="lg" text="Loading dashboard..." />
        </div>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <WelcomeSection>
        <WelcomeTitle>
          Welcome back, {user?.first_name || user?.username || 'User'}! 👋
        </WelcomeTitle>
        <WelcomeSubtitle>
          Ready to analyze cyber risk? Start by running a simulation or exploring your portfolios.
        </WelcomeSubtitle>
        <QuickActions>
          <ActionButton onClick={() => navigate('/simulation')}>
            🎯 New Simulation
          </ActionButton>
          <ActionButton onClick={() => navigate('/portfolio')}>
            💼 Manage Portfolio
          </ActionButton>
          <ActionButton onClick={() => navigate('/scenarios')}>
            📋 Create Scenario
          </ActionButton>
        </QuickActions>
      </WelcomeSection>

      <StatsGrid>
        <StatCard>
          <StatIcon color="#e6fffa">📊</StatIcon>
          <StatValue>{formatNumber(stats?.totalSimulations || 0)}</StatValue>
          <StatLabel>Total Simulations</StatLabel>
          <StatChange positive={true}>+12% from last month</StatChange>
        </StatCard>

        <StatCard>
          <StatIcon color="#fef5e7">💼</StatIcon>
          <StatValue>{formatNumber(stats?.totalPortfolios || 0)}</StatValue>
          <StatLabel>Active Portfolios</StatLabel>
          <StatChange positive={true}>+3 new this week</StatChange>
        </StatCard>

        <StatCard>
          <StatIcon color="#f0fff4">🏢</StatIcon>
          <StatValue>{formatNumber(stats?.totalPolicies || 0)}</StatValue>
          <StatLabel>Insurance Policies</StatLabel>
          <StatChange positive={false}>-2% from last month</StatChange>
        </StatCard>

        <StatCard>
          <StatIcon color="#fed7d7">⚠️</StatIcon>
          <StatValue>{stats?.averageRisk?.toFixed(1) || '0.0'}</StatValue>
          <StatLabel>Average Risk Score</StatLabel>
          <StatChange positive={false}>+0.3 from last week</StatChange>
        </StatCard>
      </StatsGrid>

      <ContentGrid>
        <ChartCard>
          <CardTitle>Risk Trend Analysis</CardTitle>
          <EmptyState>
            <EmptyIcon>📈</EmptyIcon>
            <EmptyText>
              Risk trend charts will appear here once you run simulations.
            </EmptyText>
            <ActionButton onClick={() => navigate('/simulation')}>
              Run Your First Simulation
            </ActionButton>
          </EmptyState>
        </ChartCard>

        <RecentActivity>
          <CardTitle>Recent Activity</CardTitle>
          {recentActivity.length > 0 ? (
            recentActivity.map((activity) => (
              <ActivityItem key={activity.id}>
                <ActivityIcon type={activity.type}>
                  {getActivityIcon(activity.type)}
                </ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>{activity.title}</ActivityTitle>
                  <ActivityTime>{activity.time}</ActivityTime>
                </ActivityContent>
              </ActivityItem>
            ))
          ) : (
            <EmptyState>
              <EmptyIcon>📝</EmptyIcon>
              <EmptyText>No recent activity</EmptyText>
            </EmptyState>
          )}
        </RecentActivity>
      </ContentGrid>
    </DashboardContainer>
  );
};

export default Dashboard; 