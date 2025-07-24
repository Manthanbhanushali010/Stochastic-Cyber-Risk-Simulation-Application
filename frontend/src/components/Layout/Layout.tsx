import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';

const LayoutContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background-color: #f7fafc;
`;

const Sidebar = styled.aside<{ isCollapsed: boolean }>`
  width: ${({ isCollapsed }) => isCollapsed ? '64px' : '256px'};
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transition: width 0.3s ease;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
`;

const SidebarHeader = styled.div`
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
`;

const Logo = styled.div<{ isCollapsed: boolean }>`
  font-size: 1.25rem;
  font-weight: 700;
  opacity: ${({ isCollapsed }) => isCollapsed ? '0' : '1'};
  transition: opacity 0.3s ease;
  white-space: nowrap;
`;

const CollapseButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

const Navigation = styled.nav`
  padding: 1rem 0;
  flex: 1;
`;

const NavItem = styled.div<{ isActive: boolean; isCollapsed: boolean }>`
  margin: 0.25rem 0;
`;

const NavLink = styled.button<{ isActive: boolean; isCollapsed: boolean }>`
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s ease;
  text-align: left;
  font-size: 0.875rem;
  
  ${({ isActive }) => isActive && `
    background-color: rgba(255, 255, 255, 0.2);
    border-right: 3px solid white;
  `}
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
  
  .icon {
    font-size: 1.25rem;
    margin-right: ${({ isCollapsed }) => isCollapsed ? '0' : '0.75rem'};
    width: 20px;
    text-align: center;
  }
  
  .label {
    opacity: ${({ isCollapsed }) => isCollapsed ? '0' : '1'};
    transition: opacity 0.3s ease;
    white-space: nowrap;
  }
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
`;

const TopBar = styled.header`
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 1.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const PageTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
`;

const UserName = styled.span`
  font-weight: 500;
  color: #4a5568;
`;

const LogoutButton = styled.button`
  background: none;
  border: 1px solid #e2e8f0;
  color: #4a5568;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: #f7fafc;
    border-color: #cbd5e0;
  }
`;

const ContentArea = styled.div`
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
`;

interface NavItemData {
  path: string;
  label: string;
  icon: string;
}

const navigationItems: NavItemData[] = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/simulation', label: 'Simulation', icon: '🎯' },
  { path: '/portfolio', label: 'Portfolio', icon: '💼' },
  { path: '/scenarios', label: 'Scenarios', icon: '📋' },
  { path: '/profile', label: 'Profile', icon: '👤' },
];

const getPageTitle = (pathname: string): string => {
  const item = navigationItems.find(item => item.path === pathname);
  return item ? item.label : 'Cyber Risk Platform';
};

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { showSuccess } = useNotificationStore();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const handleLogout = async () => {
    try {
      await logout();
      showSuccess('Logged out successfully');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const getUserInitials = (user: any) => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    }
    if (user?.email) {
      return user.email.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  return (
    <LayoutContainer>
      <Sidebar isCollapsed={isCollapsed}>
        <SidebarHeader>
          <Logo isCollapsed={isCollapsed}>
            Cyber Risk
          </Logo>
          <CollapseButton onClick={toggleSidebar}>
            {isCollapsed ? '→' : '←'}
          </CollapseButton>
        </SidebarHeader>
        
        <Navigation>
          {navigationItems.map((item) => (
            <NavItem key={item.path} isCollapsed={isCollapsed} isActive={location.pathname === item.path}>
              <NavLink
                isActive={location.pathname === item.path}
                isCollapsed={isCollapsed}
                onClick={() => handleNavigation(item.path)}
                title={isCollapsed ? item.label : undefined}
              >
                <span className="icon">{item.icon}</span>
                <span className="label">{item.label}</span>
              </NavLink>
            </NavItem>
          ))}
        </Navigation>
      </Sidebar>

      <MainContent>
        <TopBar>
          <PageTitle>{getPageTitle(location.pathname)}</PageTitle>
          
          <UserSection>
            <UserInfo>
              <UserAvatar>
                {getUserInitials(user)}
              </UserAvatar>
              <UserName>
                {user?.full_name || user?.username || user?.email}
              </UserName>
            </UserInfo>
            
            <LogoutButton onClick={handleLogout}>
              Logout
            </LogoutButton>
          </UserSection>
        </TopBar>

        <ContentArea>
          {children}
        </ContentArea>
      </MainContent>
    </LayoutContainer>
  );
};

export default Layout; 