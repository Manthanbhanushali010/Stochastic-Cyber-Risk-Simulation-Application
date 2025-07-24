import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '../store/authStore';
import apiService from '../services/api';
import { LoginCredentials, RegisterData, User } from '../types';

// Mock the API service
jest.mock('../services/api');
const mockedApiService = apiService as jest.Mocked<typeof apiService>;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('AuthStore', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    
    // Reset store state
    useAuthStore.getState().user = null;
    useAuthStore.getState().token = null;
    useAuthStore.getState().refreshToken = null;
    useAuthStore.getState().isAuthenticated = false;
    useAuthStore.getState().isLoading = false;
    useAuthStore.getState().error = null;
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Login', () => {
    it('should login successfully', async () => {
      const mockUser: User = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        role: 'user',
        created_at: '2023-01-01T00:00:00Z'
      };

      const mockAuthResponse = {
        user: mockUser,
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token'
      };

      mockedApiService.login.mockResolvedValue(mockAuthResponse);

      const { result } = renderHook(() => useAuthStore());

      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      await act(async () => {
        await result.current.login(credentials);
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe('mock-access-token');
      expect(result.current.refreshToken).toBe('mock-refresh-token');
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(mockedApiService.setToken).toHaveBeenCalledWith('mock-access-token');
    });

    it('should handle login failure', async () => {
      const errorMessage = 'Invalid credentials';
      mockedApiService.login.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuthStore());

      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'wrongpassword'
      };

      await expect(
        act(async () => {
          await result.current.login(credentials);
        })
      ).rejects.toThrow(errorMessage);

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
    });

    it('should set loading state during login', async () => {
      let resolveLogin: (value: any) => void;
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve;
      });
      
      mockedApiService.login.mockReturnValue(loginPromise);

      const { result } = renderHook(() => useAuthStore());

      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      act(() => {
        result.current.login(credentials);
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        resolveLogin!({
          user: { id: '1', email: 'test@example.com' },
          access_token: 'token',
          refresh_token: 'refresh'
        });
        await loginPromise;
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Register', () => {
    it('should register successfully', async () => {
      const mockUser: User = {
        id: '2',
        email: 'newuser@example.com',
        username: 'newuser',
        first_name: 'New',
        last_name: 'User',
        role: 'user',
        created_at: '2023-01-01T00:00:00Z'
      };

      const mockAuthResponse = {
        user: mockUser,
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      };

      mockedApiService.register.mockResolvedValue(mockAuthResponse);

      const { result } = renderHook(() => useAuthStore());

      const userData: RegisterData = {
        email: 'newuser@example.com',
        username: 'newuser',
        password: 'password123',
        first_name: 'New',
        last_name: 'User'
      };

      await act(async () => {
        await result.current.register(userData);
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe('new-access-token');
      expect(result.current.refreshToken).toBe('new-refresh-token');
      expect(result.current.isAuthenticated).toBe(true);
      expect(mockedApiService.setToken).toHaveBeenCalledWith('new-access-token');
    });

    it('should handle registration failure', async () => {
      const errorMessage = 'Email already exists';
      mockedApiService.register.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuthStore());

      const userData: RegisterData = {
        email: 'existing@example.com',
        username: 'existing',
        password: 'password123',
        first_name: 'Existing',
        last_name: 'User'
      };

      await expect(
        act(async () => {
          await result.current.register(userData);
        })
      ).rejects.toThrow(errorMessage);

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBe(errorMessage);
    });
  });

  describe('Logout', () => {
    it('should logout successfully', async () => {
      // Set initial authenticated state
      const { result } = renderHook(() => useAuthStore());
      
      act(() => {
        result.current.user = { id: '1', email: 'test@example.com' } as User;
        result.current.token = 'access-token';
        result.current.refreshToken = 'refresh-token';
        result.current.isAuthenticated = true;
      });

      mockedApiService.logout.mockResolvedValue({ message: 'Logged out' });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(mockedApiService.clearTokens).toHaveBeenCalled();
    });
  });

  describe('Token Refresh', () => {
    it('should refresh auth token successfully', async () => {
      const mockResponse = {
        access_token: 'new-access-token'
      };

      mockedApiService.refreshAccessToken.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useAuthStore());
      
      // Set initial state with refresh token
      act(() => {
        result.current.refreshToken = 'valid-refresh-token';
      });

      await act(async () => {
        await result.current.refreshAuthToken();
      });

      expect(result.current.token).toBe('new-access-token');
      expect(mockedApiService.setToken).toHaveBeenCalledWith('new-access-token');
    });

    it('should handle refresh token failure', async () => {
      mockedApiService.refreshAccessToken.mockRejectedValue(new Error('Invalid refresh token'));

      const { result } = renderHook(() => useAuthStore());
      
      act(() => {
        result.current.refreshToken = 'invalid-refresh-token';
      });

      await expect(
        act(async () => {
          await result.current.refreshAuthToken();
        })
      ).rejects.toThrow('Invalid refresh token');

      expect(result.current.token).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('Update Profile', () => {
    it('should update profile successfully', async () => {
      const updatedUser: User = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Updated',
        last_name: 'Name',
        role: 'user',
        created_at: '2023-01-01T00:00:00Z'
      };

      mockedApiService.updateUserProfile.mockResolvedValue(updatedUser);

      const { result } = renderHook(() => useAuthStore());
      
      // Set initial authenticated state
      act(() => {
        result.current.user = {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          first_name: 'Test',
          last_name: 'User'
        } as User;
        result.current.isAuthenticated = true;
      });

      await act(async () => {
        await result.current.updateProfile({
          first_name: 'Updated',
          last_name: 'Name'
        });
      });

      expect(result.current.user?.first_name).toBe('Updated');
      expect(result.current.user?.last_name).toBe('Name');
    });
  });

  describe('Change Password', () => {
    it('should change password successfully', async () => {
      mockedApiService.changePassword.mockResolvedValue({ message: 'Password changed' });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.changePassword({
          current_password: 'oldpassword',
          new_password: 'newpassword'
        });
      });

      expect(mockedApiService.changePassword).toHaveBeenCalledWith({
        current_password: 'oldpassword',
        new_password: 'newpassword'
      });
    });
  });

  describe('Error Management', () => {
    it('should clear error', () => {
      const { result } = renderHook(() => useAuthStore());
      
      act(() => {
        result.current.error = 'Some error';
      });

      expect(result.current.error).toBe('Some error');

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Check Auth Status', () => {
    it('should check auth status when token exists', async () => {
      const mockUser: User = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        role: 'user',
        created_at: '2023-01-01T00:00:00Z'
      };

      localStorageMock.getItem
        .mockReturnValueOnce('stored-access-token')
        .mockReturnValueOnce('stored-refresh-token');

      mockedApiService.getUserProfile.mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.checkAuthStatus();
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe('stored-access-token');
      expect(result.current.refreshToken).toBe('stored-refresh-token');
      expect(result.current.isAuthenticated).toBe(true);
      expect(mockedApiService.setToken).toHaveBeenCalledWith('stored-access-token');
    });

    it('should handle auth status check failure', async () => {
      localStorageMock.getItem
        .mockReturnValueOnce('invalid-token')
        .mockReturnValueOnce('invalid-refresh');

      mockedApiService.getUserProfile.mockRejectedValue(new Error('Unauthorized'));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.checkAuthStatus();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(mockedApiService.clearTokens).toHaveBeenCalled();
    });
  });
}); 