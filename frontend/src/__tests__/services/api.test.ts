import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import apiService from '../services/api';
import { LoginCredentials, RegisterData, SimulationRequest } from '../types';

describe('ApiService', () => {
  let mockAxios: MockAdapter;

  beforeEach(() => {
    mockAxios = new MockAdapter(axios);
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    mockAxios.restore();
  });

  describe('Authentication', () => {
    it('should login successfully', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      const mockResponse = {
        user: { id: '1', email: 'test@example.com', username: 'testuser' },
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token'
      };

      mockAxios.onPost('/api/auth/login').reply(200, mockResponse);

      const result = await apiService.login(credentials);

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('accessToken')).toBe('mock-access-token');
      expect(localStorage.getItem('refreshToken')).toBe('mock-refresh-token');
    });

    it('should register successfully', async () => {
      const userData: RegisterData = {
        email: 'newuser@example.com',
        username: 'newuser',
        password: 'password123',
        first_name: 'New',
        last_name: 'User'
      };

      const mockResponse = {
        user: { id: '2', email: 'newuser@example.com', username: 'newuser' },
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      };

      mockAxios.onPost('/api/auth/register').reply(201, mockResponse);

      const result = await apiService.register(userData);

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('accessToken')).toBe('new-access-token');
      expect(localStorage.getItem('refreshToken')).toBe('new-refresh-token');
    });

    it('should handle login failure', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'wrongpassword'
      };

      mockAxios.onPost('/api/auth/login').reply(401, {
        message: 'Invalid credentials'
      });

      await expect(apiService.login(credentials)).rejects.toThrow();
    });

    it('should logout and clear tokens', async () => {
      // Set initial tokens
      localStorage.setItem('accessToken', 'test-token');
      localStorage.setItem('refreshToken', 'test-refresh');

      mockAxios.onPost('/api/auth/logout').reply(200, { message: 'Logged out' });

      await apiService.logout();

      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });

    it('should refresh access token', async () => {
      const refreshToken = 'test-refresh-token';
      const mockResponse = {
        access_token: 'new-access-token'
      };

      mockAxios.onPost('/api/auth/refresh').reply(200, mockResponse);

      const result = await apiService.refreshAccessToken(refreshToken);

      expect(result).toEqual(mockResponse);
    });
  });

  describe('Simulation API', () => {
    beforeEach(() => {
      // Set authorization header for authenticated requests
      localStorage.setItem('accessToken', 'test-access-token');
      apiService.setToken('test-access-token');
    });

    it('should create simulation run', async () => {
      const simulationRequest: SimulationRequest = {
        name: 'Test Simulation',
        portfolio_id: 'portfolio-1',
        iterations: 10000,
        event_parameters: {
          frequency_distribution: 'poisson',
          frequency_params: { lambda: 2.5 },
          severity_distribution: 'lognormal',
          severity_params: { mu: 12.0, sigma: 1.5 }
        }
      };

      const mockResponse = {
        simulation_id: 'sim-123',
        status: 'running',
        message: 'Simulation started successfully'
      };

      mockAxios.onPost('/api/simulation/run').reply(201, mockResponse);

      const result = await apiService.createSimulationRun(simulationRequest);

      expect(result).toEqual(mockResponse);
      expect(mockAxios.history.post[0].data).toBe(JSON.stringify(simulationRequest));
    });

    it('should get simulation list', async () => {
      const mockResponse = {
        simulations: [
          {
            id: 'sim-1',
            name: 'Test Simulation 1',
            status: 'completed',
            created_at: '2023-01-01T00:00:00Z'
          },
          {
            id: 'sim-2',
            name: 'Test Simulation 2',
            status: 'running',
            created_at: '2023-01-02T00:00:00Z'
          }
        ],
        total: 2
      };

      mockAxios.onGet('/api/simulation/list').reply(200, mockResponse);

      const result = await apiService.getSimulations();

      expect(result).toEqual(mockResponse);
    });

    it('should get simulation details', async () => {
      const simulationId = 'sim-123';
      const mockResponse = {
        id: simulationId,
        name: 'Test Simulation',
        status: 'completed',
        iterations: 10000,
        created_at: '2023-01-01T00:00:00Z',
        completed_at: '2023-01-01T00:05:00Z'
      };

      mockAxios.onGet(`/api/simulation/${simulationId}`).reply(200, mockResponse);

      const result = await apiService.getSimulation(simulationId);

      expect(result).toEqual(mockResponse);
    });

    it('should get simulation results', async () => {
      const simulationId = 'sim-123';
      const mockResponse = {
        simulation_run_id: simulationId,
        risk_metrics: {
          expected_loss: 1250000,
          var_95: 3500000,
          tvar_95: 5200000,
          max_loss: 12000000
        },
        histogram_data: {
          bins: ['0-100K', '100K-200K', '200K-300K'],
          frequencies: [150, 120, 80]
        },
        exceedance_curves: {
          loss_amounts: [0, 100000, 200000, 300000],
          probabilities: [1.0, 0.8, 0.5, 0.2]
        }
      };

      mockAxios.onGet(`/api/simulation/${simulationId}/results`).reply(200, mockResponse);

      const result = await apiService.getSimulationResult(simulationId);

      expect(result).toEqual(mockResponse);
    });

    it('should stop simulation', async () => {
      const simulationId = 'sim-123';
      const mockResponse = {
        message: 'Simulation stopped successfully'
      };

      mockAxios.onPost(`/api/simulation/${simulationId}/stop`).reply(200, mockResponse);

      const result = await apiService.stopSimulation(simulationId);

      expect(result).toEqual(mockResponse);
    });
  });

  describe('Portfolio API', () => {
    beforeEach(() => {
      localStorage.setItem('accessToken', 'test-access-token');
      apiService.setToken('test-access-token');
    });

    it('should get portfolios', async () => {
      const mockResponse = {
        portfolios: [
          {
            id: 'portfolio-1',
            name: 'Tech Portfolio',
            description: 'Technology companies portfolio',
            policies_count: 45
          }
        ],
        total: 1
      };

      mockAxios.onGet('/api/portfolio/list').reply(200, mockResponse);

      const result = await apiService.getPortfolios();

      expect(result).toEqual(mockResponse);
    });

    it('should create portfolio', async () => {
      const portfolioData = {
        name: 'New Portfolio',
        description: 'A new test portfolio'
      };

      const mockResponse = {
        id: 'portfolio-new',
        name: 'New Portfolio',
        description: 'A new test portfolio',
        policies_count: 0
      };

      mockAxios.onPost('/api/portfolio/create').reply(201, mockResponse);

      const result = await apiService.createPortfolio(portfolioData);

      expect(result).toEqual(mockResponse);
    });
  });

  describe('Error Handling', () => {
    it('should handle 401 errors and attempt token refresh', async () => {
      localStorage.setItem('accessToken', 'expired-token');
      localStorage.setItem('refreshToken', 'valid-refresh-token');
      
      apiService.setToken('expired-token');

      // First request fails with 401
      mockAxios.onGet('/api/auth/profile').replyOnce(401);
      
      // Refresh token request succeeds
      mockAxios.onPost('/api/auth/refresh').reply(200, {
        access_token: 'new-access-token'
      });
      
      // Retry original request succeeds
      mockAxios.onGet('/api/auth/profile').reply(200, {
        id: '1',
        email: 'test@example.com'
      });

      const result = await apiService.getUserProfile();

      expect(result.email).toBe('test@example.com');
      expect(localStorage.getItem('accessToken')).toBe('new-access-token');
    });

    it('should redirect to login when refresh token fails', async () => {
      localStorage.setItem('accessToken', 'expired-token');
      localStorage.setItem('refreshToken', 'invalid-refresh-token');
      
      apiService.setToken('expired-token');

      // Mock window.location.href
      delete (window as any).location;
      window.location = { ...window.location, href: '' };

      // First request fails with 401
      mockAxios.onGet('/api/auth/profile').replyOnce(401);
      
      // Refresh token request fails
      mockAxios.onPost('/api/auth/refresh').reply(401);

      await expect(apiService.getUserProfile()).rejects.toThrow();
      
      expect(window.location.href).toBe('/login');
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });

    it('should handle network errors', async () => {
      mockAxios.onPost('/api/auth/login').networkError();

      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      await expect(apiService.login(credentials)).rejects.toThrow('Network Error');
    });
  });
}); 