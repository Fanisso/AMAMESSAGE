/**
 * Definições de tipos TypeScript - AMAMESSAGE
 * Para uso nos clientes web (Enterprise e Individual)
 */

// Enums
export enum UserType {
  INDIVIDUAL = 'individual',
  ENTERPRISE = 'enterprise',
  ADMIN = 'admin'
}

export enum MessageType {
  SMS = 'sms',
  USSD = 'ussd',
  AUTO_REPLY = 'auto_reply'
}

export enum MessageStatus {
  PENDING = 'pending',
  SENT = 'sent',
  DELIVERED = 'delivered',
  FAILED = 'failed',
  EXPIRED = 'expired'
}

export enum USSDSessionStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  TIMEOUT = 'timeout',
  ERROR = 'error'
}

export enum PlatformType {
  WEB = 'web',
  ANDROID = 'android',
  IOS = 'ios',
  WINDOWS = 'windows'
}

// Interface base para responses da API
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: APIError;
  timestamp: string;
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Interfaces de autenticação
export interface LoginRequest {
  email: string;
  password: string;
  platform: PlatformType;
  deviceInfo?: Record<string, string>;
}

export interface LoginResponse {
  success: boolean;
  accessToken: string;
  refreshToken: string;
  user: UserProfile;
  expiresIn: number;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

// Interfaces de usuário
export interface UserProfile {
  id: number;
  email: string;
  name: string;
  phone?: string;
  userType: UserType;
  companyName?: string;
  isActive: boolean;
  createdAt: string;
  preferences?: Record<string, any>;
}

export interface UserRegistration {
  email: string;
  password: string;
  name: string;
  phone?: string;
  userType: UserType;
  companyName?: string;
}

export interface UserUpdate {
  name?: string;
  phone?: string;
  companyName?: string;
  preferences?: Record<string, any>;
}

// Interfaces de SMS
export interface SMSSendRequest {
  to: string;
  message: string;
  scheduleAt?: string;
}

export interface SMSBulkSendRequest {
  recipients: string[];
  message: string;
  scheduleAt?: string;
}

export interface SMSMessage {
  id: string;
  to: string;
  message: string;
  status: MessageStatus;
  createdAt: string;
  cost?: number;
}

export interface SMSListResponse {
  messages: SMSMessage[];
  total: number;
  page: number;
  perPage: number;
  hasNext: boolean;
}

// Interfaces de USSD
export interface USSDSendRequest {
  code: string;
}

export interface USSDResponse {
  sessionId: string;
  code: string;
  response?: string;
  status: USSDSessionStatus;
  createdAt: string;
  completedAt?: string;
}

export interface USSDSession {
  id: string;
  code: string;
  status: USSDSessionStatus;
  response?: string;
  sessionSteps?: Array<Record<string, string>>;
  currentStep: number;
  createdAt: string;
  completedAt?: string;
}

// Interfaces de contactos
export interface Contact {
  id: number;
  name: string;
  phone: string;
  email?: string;
  group?: string;
  notes?: string;
  isBlocked: boolean;
  createdAt: string;
  updatedAt?: string;
}

export interface ContactCreate {
  name: string;
  phone: string;
  email?: string;
  group?: string;
  notes?: string;
}

export interface ContactUpdate {
  name?: string;
  phone?: string;
  email?: string;
  group?: string;
  notes?: string;
  isBlocked?: boolean;
}

export interface ContactListResponse {
  contacts: Contact[];
  total: number;
  page: number;
  perPage: number;
  hasNext: boolean;
}

// Interfaces de regras de reencaminhamento
export interface ForwardingRule {
  id: number;
  name: string;
  description?: string;
  conditionType: 'contains' | 'equals' | 'starts_with' | 'regex';
  conditionValue: string;
  sourceNumbers?: string[];
  actionType: 'forward' | 'auto_reply' | 'block' | 'alert';
  actionValue: string;
  priority: number;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
  triggerCount: number;
}

export interface ForwardingRuleCreate {
  name: string;
  description?: string;
  conditionType: 'contains' | 'equals' | 'starts_with' | 'regex';
  conditionValue: string;
  sourceNumbers?: string[];
  actionType: 'forward' | 'auto_reply' | 'block' | 'alert';
  actionValue: string;
  priority: number;
  isActive: boolean;
}

export interface ForwardingRuleUpdate {
  name?: string;
  description?: string;
  conditionType?: 'contains' | 'equals' | 'starts_with' | 'regex';
  conditionValue?: string;
  sourceNumbers?: string[];
  actionType?: 'forward' | 'auto_reply' | 'block' | 'alert';
  actionValue?: string;
  priority?: number;
  isActive?: boolean;
}

// Interfaces de sistema
export interface ModemStatus {
  id: string;
  port: string;
  manufacturer?: string;
  model?: string;
  firmwareVersion?: string;
  isConnected: boolean;
  networkRegistered: boolean;
  signalStrength?: number;
  operatorName?: string;
  simStatus?: string;
  phoneNumber?: string;
  lastSeen?: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  uptime: number;
  databaseStatus: string;
  modemStatus: string;
  messageQueueSize: number;
  lastCheck: string;
}

// Interfaces de paginação e busca
export interface PaginationQuery {
  page: number;
  perPage: number;
  sortBy?: string;
  sortOrder: 'asc' | 'desc';
}

export interface SearchQuery {
  q?: string;
  filters?: Record<string, any>;
  dateFrom?: string;
  dateTo?: string;
}

// Interfaces de configuração
export interface WebClientConfig {
  theme: 'light' | 'dark' | 'auto';
  language: 'pt' | 'en' | 'es';
  notificationsEnabled: boolean;
  autoRefreshInterval: number;
  itemsPerPage: number;
}

export interface MobileClientConfig {
  pushNotifications: boolean;
  syncContacts: boolean;
  autoBackup: boolean;
  offlineMode: boolean;
  biometricAuth: boolean;
}

// Interfaces específicas para o cliente web
export interface DashboardStats {
  totalMessages: number;
  sentToday: number;
  deliveredToday: number;
  failedToday: number;
  pendingMessages: number;
  activeUSSDSessions: number;
  contactsCount: number;
  rulesCount: number;
}

export interface MessageChart {
  date: string;
  sent: number;
  delivered: number;
  failed: number;
}

export interface RecentActivity {
  id: string;
  type: 'sms_sent' | 'ussd_executed' | 'rule_triggered' | 'contact_added';
  description: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error';
}

// Interfaces de formulários
export interface ContactImportData {
  file: File;
  hasHeaders: boolean;
  mapping: {
    name: number;
    phone: number;
    email?: number;
    group?: number;
  };
}

export interface BulkMessageData {
  recipients: Contact[];
  message: string;
  scheduleAt?: string;
  useTemplate: boolean;
  templateId?: string;
}

// Interfaces de templates
export interface MessageTemplate {
  id: number;
  name: string;
  content: string;
  variables: string[];
  category: string;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
  usageCount: number;
}

export interface TemplateVariable {
  name: string;
  value: string;
  type: 'text' | 'number' | 'date' | 'contact_field';
}

// Interfaces de notificações
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
  actionText?: string;
}

// Interfaces de webhook/integrações
export interface WebhookConfig {
  id: number;
  name: string;
  url: string;
  events: string[];
  isActive: boolean;
  secretKey: string;
  headers?: Record<string, string>;
  retryPolicy: {
    maxRetries: number;
    retryDelay: number;
  };
}

// Interfaces de relatórios
export interface ReportFilter {
  dateFrom: string;
  dateTo: string;
  messageType?: MessageType;
  status?: MessageStatus;
  contactGroup?: string;
  phoneNumber?: string;
}

export interface ReportData {
  summary: {
    totalMessages: number;
    successRate: number;
    totalCost: number;
    averageResponseTime: number;
  };
  chartData: MessageChart[];
  topContacts: Array<{
    name: string;
    phone: string;
    messageCount: number;
  }>;
  errorAnalysis: Array<{
    errorType: string;
    count: number;
    percentage: number;
  }>;
}

// Interfaces de contexto React
export interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  updateProfile: (data: UserUpdate) => Promise<void>;
}

export interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  colors: Record<string, string>;
}

export interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  clearAll: () => void;
}

// Tipos utilitários
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export type FormMode = 'create' | 'edit' | 'view';

export type SortDirection = 'asc' | 'desc';

export type FilterOperator = 'equals' | 'contains' | 'starts_with' | 'ends_with' | 'greater_than' | 'less_than';

// Constantes exportadas
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v2/auth/login',
    LOGOUT: '/api/v2/auth/logout',
    REFRESH: '/api/v2/auth/refresh',
    REGISTER: '/api/v2/auth/register'
  },
  SMS: {
    SEND: '/api/v2/sms/send',
    BULK_SEND: '/api/v2/sms/bulk-send',
    LIST: '/api/v2/sms',
    DETAIL: '/api/v2/sms'
  },
  USSD: {
    SEND: '/api/v2/ussd/send',
    SESSIONS: '/api/v2/ussd/sessions',
    SESSION_DETAIL: '/api/v2/ussd/sessions'
  },
  CONTACTS: {
    LIST: '/api/v2/contacts',
    CREATE: '/api/v2/contacts',
    UPDATE: '/api/v2/contacts',
    DELETE: '/api/v2/contacts',
    IMPORT: '/api/v2/contacts/import',
    EXPORT: '/api/v2/contacts/export'
  },
  RULES: {
    LIST: '/api/v2/forwarding-rules',
    CREATE: '/api/v2/forwarding-rules',
    UPDATE: '/api/v2/forwarding-rules',
    DELETE: '/api/v2/forwarding-rules'
  },
  SYSTEM: {
    HEALTH: '/api/v2/system/health',
    MODEM_STATUS: '/api/v2/system/modem-status',
    STATS: '/api/v2/system/stats'
  }
} as const;

export const MESSAGE_LIMITS = {
  SMS_MAX_LENGTH: 1600,
  BULK_MAX_RECIPIENTS: 100,
  CONTACTS_MAX_PER_USER: 5000,
  RULES_MAX_PER_USER: 50
} as const;

export const UI_CONSTANTS = {
  ITEMS_PER_PAGE_OPTIONS: [10, 20, 50, 100],
  AUTO_REFRESH_INTERVALS: [10, 30, 60, 300],
  THEMES: ['light', 'dark', 'auto'],
  LANGUAGES: ['pt', 'en', 'es']
} as const;
