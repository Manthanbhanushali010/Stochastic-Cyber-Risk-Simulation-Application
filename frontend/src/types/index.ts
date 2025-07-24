// User and Authentication Types
export interface User {
  id: string;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  full_name: string;
  role: 'user' | 'admin' | 'analyst';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

// Simulation Types
export interface EventParameters {
  frequency_distribution: 'poisson' | 'negative_binomial' | 'binomial';
  frequency_params: Record<string, number>;
  severity_distribution: 'lognormal' | 'pareto' | 'gamma' | 'exponential' | 'weibull';
  severity_params: Record<string, number>;
  correlation_enabled: boolean;
  correlation_params: Record<string, any>;
}

export interface SimulationRequest {
  name: string;
  description?: string;
  num_iterations: number;
  random_seed?: number;
  event_params: EventParameters;
  portfolio_id?: string;
  apply_deductibles: boolean;
  apply_limits: boolean;
  apply_reinsurance: boolean;
  reinsurance_config: Record<string, any>;
  max_events_per_iteration: number;
  convergence_check: boolean;
  convergence_threshold: number;
  convergence_window: number;
  batch_size: number;
  parallel_processing: boolean;
  max_workers?: number;
  save_raw_losses: boolean;
  calculate_percentiles: boolean;
  percentile_levels: number[];
}

export interface SimulationRun {
  id: string;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  num_iterations: number;
  random_seed?: number;
  event_parameters: EventParameters;
  simulation_config: Record<string, any>;
  progress_percent: number;
  current_iteration: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  duration?: number;
  error_message?: string;
}

export interface RiskMetrics {
  expected_loss: number;
  standard_deviation: number;
  variance: number;
  minimum_loss: number;
  maximum_loss: number;
  var_95: number;
  var_99: number;
  var_99_9: number;
  tvar_95: number;
  tvar_99: number;
  tvar_99_9: number;
  skewness: number;
  kurtosis: number;
  coefficient_of_variation: number;
  probability_of_loss: number;
  median_loss: number;
  mode_loss?: number;
  percentiles?: Record<string, number>;
  histogram_data?: HistogramData;
  exceedance_curve?: ExceedanceCurve;
}

export interface SimulationResult {
  id: string;
  simulation_run_id: string;
  expected_loss: number;
  var_95: number;
  var_99: number;
  var_99_9: number;
  tvar_95: number;
  tvar_99: number;
  tvar_99_9: number;
  min_loss: number;
  max_loss: number;
  std_deviation: number;
  skewness?: number;
  kurtosis?: number;
  probability_of_loss?: number;
  loss_distribution?: HistogramData;
  percentiles?: Record<string, number>;
  exceedance_probabilities?: ExceedanceCurve;
  created_at: string;
}

export interface HistogramData {
  counts: number[];
  bin_edges: number[];
  bin_centers: number[];
  bin_width: number;
  total_observations: number;
}

export interface ExceedanceCurve {
  loss_levels: number[];
  exceedance_probabilities: number[];
  return_periods: number[];
}

// Portfolio Types
export interface Policy {
  id: string;
  policy_number: string;
  policyholder_name: string;
  coverage_type: 'cyber_liability' | 'data_breach' | 'business_interruption' | 'errors_omissions';
  coverage_limit: number;
  deductible: number;
  sub_limits: Record<string, number>;
  annual_premium?: number;
  policy_start_date: string;
  policy_end_date: string;
  industry_sector?: string;
  company_size?: 'small' | 'medium' | 'large' | 'enterprise';
  risk_score?: number;
  country?: string;
  region?: string;
  attributes: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Portfolio {
  id: string;
  name: string;
  description?: string;
  configuration: Record<string, any>;
  policy_count: number;
  created_at: string;
  updated_at: string;
  policies?: Policy[];
}

export interface PortfolioSummary {
  portfolio_id: string;
  summary: {
    total_policies: number;
    total_coverage_limit: number;
    total_premium: number;
    average_deductible: number;
    coverage_types: Record<string, number>;
    company_sizes: Record<string, number>;
    industry_sectors: Record<string, number>;
  };
}

// Scenario Types
export interface ScenarioModification {
  frequency_multiplier: number;
  severity_multiplier: number;
  frequency_additive: number;
  severity_additive: number;
  frequency_param_modifications: Record<string, number>;
  severity_param_modifications: Record<string, number>;
  custom_modifications: Record<string, any>;
}

export interface Scenario {
  id: string;
  name: string;
  description?: string;
  base_parameters: EventParameters;
  modifications: ScenarioModification;
  is_active: boolean;
  simulation_count: number;
  created_at: string;
  updated_at: string;
}

export interface ScenarioTemplate {
  name: string;
  description: string;
  modifications: Partial<ScenarioModification>;
}

export interface ScenarioComparison {
  scenario: Scenario;
  has_results: boolean;
  results?: Partial<RiskMetrics>;
  simulation_date?: string;
}

// Distribution Types
export interface DistributionParameter {
  name: string;
  description: string;
  type: 'number' | 'integer';
  min?: number;
  max?: number;
  default?: number;
  required: boolean;
}

export interface DistributionInfo {
  name: string;
  display_name: string;
  description: string;
  parameters: DistributionParameter[];
  category: 'frequency' | 'severity';
}

export interface AvailableDistributions {
  frequency: string[];
  severity: string[];
}

// WebSocket Types
export interface SocketMessage {
  type: 'simulation_status' | 'simulation_progress' | 'simulation_complete' | 'simulation_error' | 'simulation_stopped';
  data: any;
}

export interface SimulationProgress {
  simulation_id: string;
  progress_percent: number;
  current_iteration: number;
  total_iterations: number;
}

export interface SimulationStatus {
  simulation_id: string;
  status: SimulationRun['status'];
  message: string;
}

// UI State Types
export interface UiState {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  loading: boolean;
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  timestamp: string;
}

// Chart Types
export interface ChartData {
  labels: string[] | number[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
  tension?: number;
}

export interface ChartOptions {
  responsive: boolean;
  maintainAspectRatio: boolean;
  scales?: any;
  plugins?: any;
  elements?: any;
}

// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  details?: any;
  status_code?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'email' | 'password' | 'select' | 'textarea' | 'checkbox' | 'date';
  value: any;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  options?: Array<{ value: any; label: string }>;
  min?: number;
  max?: number;
  step?: number;
}

export interface ValidationError {
  field: string;
  message: string;
}

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = 
  Pick<T, Exclude<keyof T, Keys>> & 
  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>> }[Keys];

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

export interface FieldError {
  field: string;
  message: string;
} 