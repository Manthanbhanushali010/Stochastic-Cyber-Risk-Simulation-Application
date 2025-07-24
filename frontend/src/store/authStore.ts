import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials, RegisterData, AuthState } from '../types';
import apiService from '../services/api';

interface AuthStore extends AuthState {
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuthToken: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
  changePassword: (passwords: { current_password: string; new_password: string }) => Promise<void>;
  clearError: () => void;
  checkAuthStatus: () => Promise<void>;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginCredentials) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await apiService.login(credentials);
          
          // Set tokens in API service
          apiService.setToken(response.access_token);
          apiService.setRefreshToken(response.refresh_token);
          
          set({
            user: response.user,
            token: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || error.message || 'Login failed';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
            token: null,
            refreshToken: null
          });
          throw error;
        }
      },

      register: async (userData: RegisterData) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await apiService.register(userData);
          
          // Set tokens in API service
          apiService.setToken(response.access_token);
          apiService.setRefreshToken(response.refresh_token);
          
          set({
            user: response.user,
            token: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || error.message || 'Registration failed';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
            token: null,
            refreshToken: null
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          // Attempt to logout on server (doesn't matter if it fails)
          await apiService.logout();
        } catch (error) {
          // Ignore server logout errors
        } finally {
          // Clear local state regardless
          apiService.clearTokens();
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        }
      },

      refreshAuthToken: async () => {
        try {
          const { refreshToken } = get();
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          const response = await apiService.refreshAccessToken(refreshToken);
          
          apiService.setToken(response.access_token);
          
          set({
            token: response.access_token,
            error: null
          });
        } catch (error: any) {
          // Refresh failed, logout user
          get().logout();
          throw error;
        }
      },

      updateProfile: async (userData: Partial<User>) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await apiService.updateUserProfile(userData);
          
          set({
            user: response.user,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || error.message || 'Profile update failed';
          set({
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      changePassword: async (passwords: { current_password: string; new_password: string }) => {
        try {
          set({ isLoading: true, error: null });
          
          await apiService.changePassword(passwords);
          
          set({
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || error.message || 'Password change failed';
          set({
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      checkAuthStatus: async () => {
        try {
          const { token } = get();
          if (!token) {
            return;
          }

          set({ isLoading: true });
          
          // Verify token is still valid
          await apiService.verifyToken();
          
          // Get fresh user profile
          const response = await apiService.getUserProfile();
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          // Token is invalid, logout user
          get().logout();
        }
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
); 