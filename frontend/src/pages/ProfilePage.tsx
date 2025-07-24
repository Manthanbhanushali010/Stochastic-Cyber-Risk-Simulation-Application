import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { User } from '../types';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const ProfileContainer = styled.div`
  max-width: 1200px;
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

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const Sidebar = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  height: fit-content;
  position: sticky;
  top: 2rem;
`;

const ProfilePhoto = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  margin: 0 auto 1rem;
  position: relative;
  cursor: pointer;
`;

const PhotoUpload = styled.input`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
`;

const UserInfo = styled.div`
  text-align: center;
  margin-bottom: 2rem;
`;

const UserName = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
`;

const UserEmail = styled.p`
  color: #718096;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
`;

const UserRole = styled.span`
  background: #edf2f7;
  color: #4a5568;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
`;

const NavList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
`;

const NavItem = styled.button<{ active: boolean }>`
  background: ${({ active }) => active ? '#f7fafc' : 'transparent'};
  border: none;
  color: ${({ active }) => active ? '#667eea' : '#4a5568'};
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: ${({ active }) => active ? '600' : '500'};
  
  &:hover {
    background: #f7fafc;
    color: #667eea;
  }
`;

const MainContent = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ContentHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
`;

const ContentTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
`;

const ContentDescription = styled.p`
  color: #718096;
  font-size: 0.875rem;
`;

const ContentBody = styled.div`
  padding: 1.5rem;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
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
  
  &:disabled {
    background: #f7fafc;
    color: #a0aec0;
    cursor: not-allowed;
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

const ErrorText = styled.span`
  color: #f56565;
  font-size: 0.875rem;
`;

const SuccessText = styled.span`
  color: #10b981;
  font-size: 0.875rem;
`;

const SettingsSection = styled.div`
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
`;

const SettingItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #f7fafc;
  
  &:last-child {
    border-bottom: none;
  }
`;

const SettingInfo = styled.div`
  flex: 1;
`;

const SettingLabel = styled.div`
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 0.25rem;
`;

const SettingDescription = styled.div`
  font-size: 0.875rem;
  color: #718096;
`;

const Toggle = styled.label`
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  margin-left: 1rem;
`;

const ToggleInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
`;

const ToggleSlider = styled.span<{ checked: boolean }>`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${({ checked }) => checked ? '#667eea' : '#cbd5e0'};
  transition: 0.4s;
  border-radius: 24px;
  
  &:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: ${({ checked }) => checked ? '27px' : '3px'};
    bottom: 3px;
    background-color: white;
    transition: 0.4s;
    border-radius: 50%;
  }
`;

const StatCard = styled.div`
  background: #f7fafc;
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
`;

const StatNumber = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: #718096;
  margin-top: 0.25rem;
`;

const ActivityList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const ActivityItem = styled.div`
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 0.5rem;
`;

const ActivityIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityTitle = styled.div`
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
`;

const ActivityDescription = styled.div`
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 0.25rem;
`;

const ActivityTime = styled.div`
  font-size: 0.75rem;
  color: #a0aec0;
`;

const tabs = [
  { id: 'general', label: 'General', icon: '👤' },
  { id: 'security', label: 'Security', icon: '🔒' },
  { id: 'preferences', label: 'Preferences', icon: '⚙️' },
  { id: 'activity', label: 'Activity', icon: '📊' },
];

interface ProfileFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  organization: string;
  title: string;
  bio: string;
  timezone: string;
  language: string;
}

interface SecurityFormData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface PreferencesData {
  email_notifications: boolean;
  push_notifications: boolean;
  marketing_emails: boolean;
  simulation_alerts: boolean;
  weekly_reports: boolean;
  theme: string;
  default_currency: string;
  date_format: string;
}

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, updateProfile, changePassword, isLoading } = useAuthStore();
  const { showSuccess, showError, showInfo } = useNotificationStore();
  
  const [activeTab, setActiveTab] = useState('general');
  const [profileForm, setProfileForm] = useState<ProfileFormData>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    organization: '',
    title: '',
    bio: '',
    timezone: 'UTC',
    language: 'en'
  });
  
  const [securityForm, setSecurityForm] = useState<SecurityFormData>({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const [preferences, setPreferences] = useState<PreferencesData>({
    email_notifications: true,
    push_notifications: true,
    marketing_emails: false,
    simulation_alerts: true,
    weekly_reports: true,
    theme: 'light',
    default_currency: 'USD',
    date_format: 'MM/DD/YYYY'
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setProfileForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
        organization: user.organization || '',
        title: user.title || '',
        bio: user.bio || '',
        timezone: user.timezone || 'UTC',
        language: user.language || 'en'
      });
    }
  }, [user]);

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: Record<string, string> = {};
    
    if (!profileForm.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    
    if (!profileForm.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileForm.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    try {
      setIsSaving(true);
      await updateProfile(profileForm);
      showSuccess('Profile Updated', 'Your profile has been updated successfully');
      setErrors({});
    } catch (error: any) {
      showError('Update Failed', error.message || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: Record<string, string> = {};
    
    if (!securityForm.current_password) {
      newErrors.current_password = 'Current password is required';
    }
    
    if (!securityForm.new_password) {
      newErrors.new_password = 'New password is required';
    } else if (securityForm.new_password.length < 6) {
      newErrors.new_password = 'Password must be at least 6 characters';
    }
    
    if (securityForm.new_password !== securityForm.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    try {
      setIsSaving(true);
      await changePassword(securityForm.current_password, securityForm.new_password);
      showSuccess('Password Changed', 'Your password has been updated successfully');
      setSecurityForm({ current_password: '', new_password: '', confirm_password: '' });
      setErrors({});
    } catch (error: any) {
      showError('Password Change Failed', error.message || 'Failed to change password');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePreferenceChange = (key: keyof PreferencesData, value: any) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
    // Auto-save preferences
    showInfo('Preferences Updated', 'Your preferences have been saved');
  };

  const getUserInitials = (): string => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  const mockActivity = [
    {
      id: '1',
      type: 'simulation',
      title: 'Ran Monte Carlo Simulation',
      description: 'Cyber Breach Scenario - 10,000 iterations',
      time: '2 hours ago',
      icon: '🎯'
    },
    {
      id: '2',
      type: 'portfolio',
      title: 'Updated Portfolio',
      description: 'Modified "Tech Companies" portfolio',
      time: '4 hours ago',
      icon: '💼'
    },
    {
      id: '3',
      type: 'scenario',
      title: 'Created Scenario',
      description: 'New ransomware attack scenario',
      time: '1 day ago',
      icon: '📋'
    },
    {
      id: '4',
      type: 'profile',
      title: 'Profile Updated',
      description: 'Changed notification preferences',
      time: '3 days ago',
      icon: '👤'
    },
    {
      id: '5',
      type: 'export',
      title: 'Exported Results',
      description: 'Downloaded simulation results to CSV',
      time: '1 week ago',
      icon: '📄'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return (
          <form onSubmit={handleProfileSubmit}>
            <FormGrid>
              <FormGroup>
                <Label htmlFor="first_name">First Name *</Label>
                <Input
                  id="first_name"
                  type="text"
                  value={profileForm.first_name}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, first_name: e.target.value }))}
                  hasError={!!errors.first_name}
                />
                {errors.first_name && <ErrorText>{errors.first_name}</ErrorText>}
              </FormGroup>

              <FormGroup>
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  type="text"
                  value={profileForm.last_name}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, last_name: e.target.value }))}
                />
              </FormGroup>

              <FormGroup>
                <Label htmlFor="email">Email Address *</Label>
                <Input
                  id="email"
                  type="email"
                  value={profileForm.email}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, email: e.target.value }))}
                  hasError={!!errors.email}
                />
                {errors.email && <ErrorText>{errors.email}</ErrorText>}
              </FormGroup>

              <FormGroup>
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={profileForm.phone}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, phone: e.target.value }))}
                />
              </FormGroup>

              <FormGroup>
                <Label htmlFor="organization">Organization</Label>
                <Input
                  id="organization"
                  type="text"
                  value={profileForm.organization}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, organization: e.target.value }))}
                />
              </FormGroup>

              <FormGroup>
                <Label htmlFor="title">Job Title</Label>
                <Input
                  id="title"
                  type="text"
                  value={profileForm.title}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, title: e.target.value }))}
                />
              </FormGroup>

              <FormGroup>
                <Label htmlFor="timezone">Timezone</Label>
                <Select
                  id="timezone"
                  value={profileForm.timezone}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, timezone: e.target.value }))}
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time</option>
                  <option value="America/Chicago">Central Time</option>
                  <option value="America/Denver">Mountain Time</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                  <option value="Europe/London">London</option>
                  <option value="Europe/Paris">Paris</option>
                  <option value="Asia/Tokyo">Tokyo</option>
                </Select>
              </FormGroup>

              <FormGroup>
                <Label htmlFor="language">Language</Label>
                <Select
                  id="language"
                  value={profileForm.language}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, language: e.target.value }))}
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="ja">Japanese</option>
                  <option value="zh">Chinese</option>
                </Select>
              </FormGroup>
            </FormGrid>

            <FormGroup>
              <Label htmlFor="bio">Bio</Label>
              <Textarea
                id="bio"
                value={profileForm.bio}
                onChange={(e) => setProfileForm(prev => ({ ...prev, bio: e.target.value }))}
                placeholder="Tell us a bit about yourself..."
              />
            </FormGroup>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
              <Button type="submit" disabled={isSaving}>
                {isSaving ? (
                  <>
                    <LoadingSpinner size="sm" color="currentColor" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </Button>
            </div>
          </form>
        );

      case 'security':
        return (
          <div>
            <SettingsSection>
              <SectionTitle>Change Password</SectionTitle>
              <form onSubmit={handlePasswordSubmit}>
                <FormGrid>
                  <FormGroup>
                    <Label htmlFor="current_password">Current Password *</Label>
                    <Input
                      id="current_password"
                      type="password"
                      value={securityForm.current_password}
                      onChange={(e) => setSecurityForm(prev => ({ ...prev, current_password: e.target.value }))}
                      hasError={!!errors.current_password}
                    />
                    {errors.current_password && <ErrorText>{errors.current_password}</ErrorText>}
                  </FormGroup>

                  <FormGroup>
                    <Label htmlFor="new_password">New Password *</Label>
                    <Input
                      id="new_password"
                      type="password"
                      value={securityForm.new_password}
                      onChange={(e) => setSecurityForm(prev => ({ ...prev, new_password: e.target.value }))}
                      hasError={!!errors.new_password}
                    />
                    {errors.new_password && <ErrorText>{errors.new_password}</ErrorText>}
                  </FormGroup>

                  <FormGroup>
                    <Label htmlFor="confirm_password">Confirm New Password *</Label>
                    <Input
                      id="confirm_password"
                      type="password"
                      value={securityForm.confirm_password}
                      onChange={(e) => setSecurityForm(prev => ({ ...prev, confirm_password: e.target.value }))}
                      hasError={!!errors.confirm_password}
                    />
                    {errors.confirm_password && <ErrorText>{errors.confirm_password}</ErrorText>}
                  </FormGroup>
                </FormGrid>

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <Button type="submit" disabled={isSaving}>
                    {isSaving ? (
                      <>
                        <LoadingSpinner size="sm" color="currentColor" />
                        Updating...
                      </>
                    ) : (
                      'Change Password'
                    )}
                  </Button>
                </div>
              </form>
            </SettingsSection>

            <SettingsSection>
              <SectionTitle>Two-Factor Authentication</SectionTitle>
              <SettingItem>
                <SettingInfo>
                  <SettingLabel>Enable 2FA</SettingLabel>
                  <SettingDescription>
                    Add an extra layer of security to your account
                  </SettingDescription>
                </SettingInfo>
                <Button variant="secondary" onClick={() => showInfo('2FA', 'Two-factor authentication setup coming soon')}>
                  Set up
                </Button>
              </SettingItem>
            </SettingsSection>

            <SettingsSection>
              <SectionTitle>Active Sessions</SectionTitle>
              <SettingItem>
                <SettingInfo>
                  <SettingLabel>Current Session</SettingLabel>
                  <SettingDescription>
                    Chrome on macOS • Last active: now
                  </SettingDescription>
                </SettingInfo>
                <Button variant="danger" onClick={() => showInfo('Logout', 'Session management coming soon')}>
                  Revoke
                </Button>
              </SettingItem>
            </SettingsSection>
          </div>
        );

      case 'preferences':
        return (
          <div>
            <SettingsSection>
              <SectionTitle>Notifications</SectionTitle>
              <SettingItem>
                <SettingInfo>
                  <SettingLabel>Email Notifications</SettingLabel>
                  <SettingDescription>
                    Receive email notifications for important updates
                  </SettingDescription>
                </SettingInfo>
                <Toggle>
                  <ToggleInput
                    type="checkbox"
                    checked={preferences.email_notifications}
                    onChange={(e) => handlePreferenceChange('email_notifications', e.target.checked)}
                  />
                  <ToggleSlider checked={preferences.email_notifications} />
                </Toggle>
              </SettingItem>

              <SettingItem>
                <SettingInfo>
                  <SettingLabel>Push Notifications</SettingLabel>
                  <SettingDescription>
                    Get notified about simulation progress and results
                  </SettingDescription>
                </SettingInfo>
                <Toggle>
                  <ToggleInput
                    type="checkbox"
                    checked={preferences.push_notifications}
                    onChange={(e) => handlePreferenceChange('push_notifications', e.target.checked)}
                  />
                  <ToggleSlider checked={preferences.push_notifications} />
                </Toggle>
              </SettingItem>

              <SettingItem>
                <SettingInfo>
                  <SettingLabel>Marketing Emails</SettingLabel>
                  <SettingDescription>
                    Receive updates about new features and products
                  </SettingDescription>
                </SettingInfo>
                <Toggle>
                  <ToggleInput
                    type="checkbox"
                    checked={preferences.marketing_emails}
                    onChange={(e) => handlePreferenceChange('marketing_emails', e.target.checked)}
                  />
                  <ToggleSlider checked={preferences.marketing_emails} />
                </Toggle>
              </SettingItem>

              <SettingItem>
                <SettingInfo>
                  <SettingLabel>Simulation Alerts</SettingLabel>
                  <SettingDescription>
                    Get alerts when simulations complete or fail
                  </SettingDescription>
                </SettingInfo>
                <Toggle>
                  <ToggleInput
                    type="checkbox"
                    checked={preferences.simulation_alerts}
                    onChange={(e) => handlePreferenceChange('simulation_alerts', e.target.checked)}
                  />
                  <ToggleSlider checked={preferences.simulation_alerts} />
                </Toggle>
              </SettingItem>

              <SettingItem>
                <SettingInfo>
                  <SettingLabel>Weekly Reports</SettingLabel>
                  <SettingDescription>
                    Receive weekly summaries of your risk analysis
                  </SettingDescription>
                </SettingInfo>
                <Toggle>
                  <ToggleInput
                    type="checkbox"
                    checked={preferences.weekly_reports}
                    onChange={(e) => handlePreferenceChange('weekly_reports', e.target.checked)}
                  />
                  <ToggleSlider checked={preferences.weekly_reports} />
                </Toggle>
              </SettingItem>
            </SettingsSection>

            <SettingsSection>
              <SectionTitle>Display Preferences</SectionTitle>
              <FormGrid>
                <FormGroup>
                  <Label>Theme</Label>
                  <Select
                    value={preferences.theme}
                    onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="auto">Auto</option>
                  </Select>
                </FormGroup>

                <FormGroup>
                  <Label>Default Currency</Label>
                  <Select
                    value={preferences.default_currency}
                    onChange={(e) => handlePreferenceChange('default_currency', e.target.value)}
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="JPY">JPY (¥)</option>
                    <option value="CAD">CAD (C$)</option>
                  </Select>
                </FormGroup>

                <FormGroup>
                  <Label>Date Format</Label>
                  <Select
                    value={preferences.date_format}
                    onChange={(e) => handlePreferenceChange('date_format', e.target.value)}
                  >
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  </Select>
                </FormGroup>
              </FormGrid>
            </SettingsSection>
          </div>
        );

      case 'activity':
        return (
          <div>
            <SettingsSection>
              <SectionTitle>Account Statistics</SectionTitle>
              <FormGrid>
                <StatCard>
                  <StatNumber>24</StatNumber>
                  <StatLabel>Simulations Run</StatLabel>
                </StatCard>
                <StatCard>
                  <StatNumber>8</StatNumber>
                  <StatLabel>Portfolios Created</StatLabel>
                </StatCard>
                <StatCard>
                  <StatNumber>15</StatNumber>
                  <StatLabel>Scenarios Built</StatLabel>
                </StatCard>
                <StatCard>
                  <StatNumber>42</StatNumber>
                  <StatLabel>Days Active</StatLabel>
                </StatCard>
              </FormGrid>
            </SettingsSection>

            <SettingsSection>
              <SectionTitle>Recent Activity</SectionTitle>
              <ActivityList>
                {mockActivity.map((activity) => (
                  <ActivityItem key={activity.id}>
                    <ActivityIcon>{activity.icon}</ActivityIcon>
                    <ActivityContent>
                      <ActivityTitle>{activity.title}</ActivityTitle>
                      <ActivityDescription>{activity.description}</ActivityDescription>
                      <ActivityTime>{activity.time}</ActivityTime>
                    </ActivityContent>
                  </ActivityItem>
                ))}
              </ActivityList>
            </SettingsSection>
          </div>
        );

      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <ProfileContainer>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
          <LoadingSpinner size="lg" text="Loading profile..." />
        </div>
      </ProfileContainer>
    );
  }

  return (
    <ProfileContainer>
      <Header>
        <Title>👤 Profile Settings</Title>
      </Header>

      <ContentGrid>
        <Sidebar>
          <ProfilePhoto>
            <PhotoUpload
              type="file"
              accept="image/*"
              onChange={() => showInfo('Photo Upload', 'Photo upload coming soon')}
            />
            {getUserInitials()}
          </ProfilePhoto>

          <UserInfo>
            <UserName>
              {user?.first_name && user?.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user?.username || 'User'
              }
            </UserName>
            <UserEmail>{user?.email}</UserEmail>
            <UserRole>Premium User</UserRole>
          </UserInfo>

          <NavList>
            {tabs.map((tab) => (
              <NavItem
                key={tab.id}
                active={activeTab === tab.id}
                onClick={() => setActiveTab(tab.id)}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </NavItem>
            ))}
          </NavList>
        </Sidebar>

        <MainContent>
          <ContentHeader>
            <ContentTitle>
              {tabs.find(tab => tab.id === activeTab)?.label} Settings
            </ContentTitle>
            <ContentDescription>
              {activeTab === 'general' && 'Manage your personal information and account details'}
              {activeTab === 'security' && 'Keep your account secure with these settings'}
              {activeTab === 'preferences' && 'Customize your experience and notifications'}
              {activeTab === 'activity' && 'View your account activity and usage statistics'}
            </ContentDescription>
          </ContentHeader>

          <ContentBody>
            {renderTabContent()}
          </ContentBody>
        </MainContent>
      </ContentGrid>
    </ProfileContainer>
  );
};

export default ProfilePage; 