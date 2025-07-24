import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { 
  User, 
  LoginCredentials, 
  RegisterData, 
  SimulationRequest, 
  SimulationRun, 
  SimulationResult,
  Portfolio,
  Policy,
  PortfolioSummary,
  Scenario,
  ScenarioTemplate,
  ScenarioComparison,
  AvailableDistributions,
  ApiResponse,
  PaginatedResponse
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class ApiService {
  private axiosInstance: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors (token expired)
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              const response = await this.refreshAccessToken(refreshToken);
              this.setToken(response.access_token);
              originalRequest.headers.Authorization = `Bearer ${response.access_token}`;
              return this.axiosInstance(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            this.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );

    // Initialize token from localStorage
    const storedToken = localStorage.getItem('accessToken');
    if (storedToken) {
      this.setToken(storedToken);
    }
  }

  // Token management
  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('accessToken', token);
  }

  setRefreshToken(refreshToken: string): void {
    localStorage.setItem('refreshToken', refreshToken);
  }

  clearTokens(): void {
    this.token = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  // Authentication Methods
  async login(credentials: LoginCredentials): Promise<{ user: User; access_token: string; refresh_token: string }> {
    const response = await this.axiosInstance.post('/auth/login', credentials);
    return response.data;
  }

  async register(userData: RegisterData): Promise<{ user: User; access_token: string; refresh_token: string }> {
    const response = await this.axiosInstance.post('/auth/register', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.axiosInstance.post('/auth/logout');
    } finally {
      this.clearTokens();
    }
  }

  async refreshAccessToken(refreshToken: string): Promise<{ access_token: string }> {
    const response = await this.axiosInstance.post('/auth/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    });
    return response.data;
  }

  async getUserProfile(): Promise<{ user: User }> {
    const response = await this.axiosInstance.get('/auth/profile');
    return response.data;
  }

  async updateUserProfile(userData: Partial<User>): Promise<{ user: User }> {
    const response = await this.axiosInstance.put('/auth/profile', userData);
    return response.data;
  }

  async changePassword(passwords: { current_password: string; new_password: string }): Promise<void> {
    await this.axiosInstance.post('/auth/change-password', passwords);
  }

  async verifyToken(): Promise<{ valid: boolean; user_id: string; expires_at: number }> {
    const response = await this.axiosInstance.get('/auth/verify');
    return response.data;
  }

  // Simulation Methods
  async runSimulation(simulationData: SimulationRequest): Promise<{ simulation_id: string; simulation: SimulationRun }> {
    const response = await this.axiosInstance.post('/simulation/run', simulationData);
    return response.data;
  }

  async getSimulations(params?: { 
    status?: string; 
    limit?: number; 
    offset?: number; 
  }): Promise<PaginatedResponse<SimulationRun>> {
    const response = await this.axiosInstance.get('/simulation/list', { params });
    return {
      items: response.data.simulations,
      total_count: response.data.total_count,
      limit: response.data.limit,
      offset: response.data.offset,
      has_more: response.data.has_more
    };
  }

  async getSimulation(simulationId: string): Promise<{ simulation: SimulationRun }> {
    const response = await this.axiosInstance.get(`/simulation/${simulationId}`);
    return response.data;
  }

  async getSimulationResults(simulationId: string): Promise<{ simulation_id: string; results: SimulationResult }> {
    const response = await this.axiosInstance.get(`/simulation/${simulationId}/results`);
    return response.data;
  }

  async stopSimulation(simulationId: string): Promise<void> {
    await this.axiosInstance.post(`/simulation/${simulationId}/stop`);
  }

  async deleteSimulation(simulationId: string): Promise<void> {
    await this.axiosInstance.delete(`/simulation/${simulationId}`);
  }

  async getAvailableDistributions(): Promise<{ 
    distributions: AvailableDistributions; 
    parameter_schemas: Record<string, any> 
  }> {
    const response = await this.axiosInstance.get('/simulation/distributions');
    return response.data;
  }

  // Portfolio Methods
  async createPortfolio(portfolioData: { name: string; description?: string; configuration?: Record<string, any> }): Promise<{ portfolio: Portfolio }> {
    const response = await this.axiosInstance.post('/portfolio/', portfolioData);
    return response.data;
  }

  async getPortfolios(params?: { limit?: number; offset?: number }): Promise<PaginatedResponse<Portfolio>> {
    const response = await this.axiosInstance.get('/portfolio/', { params });
    return {
      items: response.data.portfolios,
      total_count: response.data.total_count,
      limit: response.data.limit,
      offset: response.data.offset,
      has_more: response.data.has_more
    };
  }

  async getPortfolio(portfolioId: string): Promise<{ portfolio: Portfolio }> {
    const response = await this.axiosInstance.get(`/portfolio/${portfolioId}`);
    return response.data;
  }

  async updatePortfolio(portfolioId: string, portfolioData: Partial<Portfolio>): Promise<{ portfolio: Portfolio }> {
    const response = await this.axiosInstance.put(`/portfolio/${portfolioId}`, portfolioData);
    return response.data;
  }

  async deletePortfolio(portfolioId: string): Promise<void> {
    await this.axiosInstance.delete(`/portfolio/${portfolioId}`);
  }

  async addPolicyToPortfolio(portfolioId: string, policyData: Omit<Policy, 'id' | 'created_at' | 'updated_at'>): Promise<{ policy: Policy }> {
    const response = await this.axiosInstance.post(`/portfolio/${portfolioId}/policies`, policyData);
    return response.data;
  }

  async updatePolicy(portfolioId: string, policyId: string, policyData: Omit<Policy, 'id' | 'created_at' | 'updated_at'>): Promise<{ policy: Policy }> {
    const response = await this.axiosInstance.put(`/portfolio/${portfolioId}/policies/${policyId}`, policyData);
    return response.data;
  }

  async deletePolicy(portfolioId: string, policyId: string): Promise<void> {
    await this.axiosInstance.delete(`/portfolio/${portfolioId}/policies/${policyId}`);
  }

  async getPortfolioSummary(portfolioId: string): Promise<PortfolioSummary> {
    const response = await this.axiosInstance.get(`/portfolio/${portfolioId}/summary`);
    return response.data;
  }

  // Scenario Methods
  async createScenario(scenarioData: Omit<Scenario, 'id' | 'simulation_count' | 'created_at' | 'updated_at'>): Promise<{ scenario: Scenario }> {
    const response = await this.axiosInstance.post('/scenarios/', scenarioData);
    return response.data;
  }

  async getScenarios(params?: { active_only?: boolean; limit?: number; offset?: number }): Promise<PaginatedResponse<Scenario>> {
    const response = await this.axiosInstance.get('/scenarios/', { params });
    return {
      items: response.data.scenarios,
      total_count: response.data.total_count,
      limit: response.data.limit,
      offset: response.data.offset,
      has_more: response.data.has_more
    };
  }

  async getScenario(scenarioId: string): Promise<{ scenario: Scenario }> {
    const response = await this.axiosInstance.get(`/scenarios/${scenarioId}`);
    return response.data;
  }

  async updateScenario(scenarioId: string, scenarioData: Partial<Scenario>): Promise<{ scenario: Scenario }> {
    const response = await this.axiosInstance.put(`/scenarios/${scenarioId}`, scenarioData);
    return response.data;
  }

  async deleteScenario(scenarioId: string): Promise<void> {
    await this.axiosInstance.delete(`/scenarios/${scenarioId}`);
  }

  async activateScenario(scenarioId: string): Promise<void> {
    await this.axiosInstance.post(`/scenarios/${scenarioId}/activate`);
  }

  async deactivateScenario(scenarioId: string): Promise<void> {
    await this.axiosInstance.post(`/scenarios/${scenarioId}/deactivate`);
  }

  async duplicateScenario(scenarioId: string, newName: string): Promise<{ scenario: Scenario }> {
    const response = await this.axiosInstance.post(`/scenarios/${scenarioId}/duplicate`, { name: newName });
    return response.data;
  }

  async getScenarioTemplates(): Promise<{ 
    templates: ScenarioTemplate[]; 
    modification_types: Record<string, string> 
  }> {
    const response = await this.axiosInstance.get('/scenarios/templates');
    return response.data;
  }

  async compareScenarios(scenarioIds: string[], metrics?: string[]): Promise<{
    comparison: ScenarioComparison[];
    summary: any;
  }> {
    const response = await this.axiosInstance.post('/scenarios/compare', {
      scenario_ids: scenarioIds,
      metrics
    });
    return response.data;
  }

  // General API Methods
  async getHealthCheck(): Promise<any> {
    const response = await this.axiosInstance.get('/health');
    return response.data;
  }

  async getSystemStatus(): Promise<any> {
    const response = await this.axiosInstance.get('/status');
    return response.data;
  }

  async getApiInfo(): Promise<any> {
    const response = await this.axiosInstance.get('/info');
    return response.data;
  }

  async getUserStats(): Promise<any> {
    const response = await this.axiosInstance.get('/stats');
    return response.data;
  }

  // Utility Methods
  async uploadFile(file: File, endpoint: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.axiosInstance.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async downloadFile(endpoint: string, filename: string): Promise<void> {
    const response = await this.axiosInstance.get(endpoint, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService; 