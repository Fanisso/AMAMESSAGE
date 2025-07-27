// Configuração Principal do Sistema Enterprise
// Centralizador de configurações, providers e inicialização

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from '@/hooks/useAuth';
import { NotificationProvider } from '@/components/notifications/NotificationSystem';
import { AppLayout } from '@/components/layout/AppLayout';
import { Toaster } from 'sonner';

// ===== CONFIGURAÇÃO DO REACT QUERY =====

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
      retry: (failureCount, error: any) => {
        // Não retry para erros 401, 403, 404
        if (error?.response?.status && [401, 403, 404].includes(error.response.status)) {
          return false;
        }
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
      onError: (error: any) => {
        console.error('Mutation error:', error);
      },
    },
  },
});

// ===== CONFIGURAÇÕES DO SISTEMA =====

export const SYSTEM_CONFIG = {
  app: {
    name: 'AMA MESSAGE',
    version: '2.0.0',
    environment: process.env.NODE_ENV || 'development',
    description: 'Sistema Enterprise de SMS'
  },
  
  api: {
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v2',
    timeout: 30000,
    retries: 3
  },
  
  sms: {
    maxLength: 160,
    maxLengthUnicode: 70,
    defaultProvider: 'twilio',
    rateLimiting: {
      perMinute: 100,
      perHour: 1000,
      perDay: 10000
    }
  },
  
  contacts: {
    maxBulkImport: 1000,
    exportFormats: ['csv', 'xlsx', 'json'],
    phoneValidation: {
      country: 'MZ',
      format: 'E164'
    }
  },
  
  campaigns: {
    maxRecipients: 10000,
    schedulingLimits: {
      minAdvance: 15, // minutos
      maxAdvance: 365 * 24 * 60 // 1 ano em minutos
    }
  },
  
  ui: {
    theme: {
      primary: '#3b82f6',
      secondary: '#64748b',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#8b5cf6'
    },
    
    animations: {
      duration: 200,
      easing: 'ease-in-out'
    },
    
    pagination: {
      defaultPageSize: 20,
      pageSizeOptions: [10, 20, 50, 100]
    }
  },
  
  notifications: {
    position: 'top-right',
    duration: 4000,
    maxVisible: 5,
    sounds: {
      success: '/sounds/success.mp3',
      error: '/sounds/error.mp3',
      warning: '/sounds/warning.mp3',
      info: '/sounds/info.mp3'
    }
  },
  
  storage: {
    keys: {
      auth: 'ama_auth',
      user: 'ama_user',
      settings: 'ama_settings',
      theme: 'ama_theme',
      notifications: 'ama_notifications'
    }
  },
  
  features: {
    multiLanguage: true,
    darkMode: true,
    realTimeNotifications: true,
    advancedReports: true,
    bulkOperations: true,
    apiAccess: true,
    webhooks: true
  }
};

// ===== PROVIDER PRINCIPAL =====

interface AppProvidersProps {
  children: React.ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <NotificationProvider>
          {children}
          
          {/* DevTools apenas em desenvolvimento */}
          {SYSTEM_CONFIG.app.environment === 'development' && (
            <ReactQueryDevtools initialIsOpen={false} />
          )}
          
          {/* Toaster global */}
          <Toaster
            position={SYSTEM_CONFIG.notifications.position as any}
            duration={SYSTEM_CONFIG.notifications.duration}
            visibleToasts={SYSTEM_CONFIG.notifications.maxVisible}
            richColors={true}
            closeButton={true}
            expand={true}
            toastOptions={{
              style: {
                background: 'white',
                border: '1px solid #e5e7eb',
                color: '#374151',
                borderRadius: '8px',
                padding: '16px',
                fontSize: '14px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
              },
            }}
          />
        </NotificationProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

// ===== LAYOUT WRAPPER =====

interface AppWrapperProps {
  children: React.ReactNode;
  useLayout?: boolean;
}

export function AppWrapper({ children, useLayout = true }: AppWrapperProps) {
  if (useLayout) {
    return (
      <AppLayout>
        {children}
      </AppLayout>
    );
  }
  
  return <>{children}</>;
}

// ===== UTILIDADES DE CONFIGURAÇÃO =====

export const configUtils = {
  // Verificar se uma feature está habilitada
  isFeatureEnabled: (feature: keyof typeof SYSTEM_CONFIG.features): boolean => {
    return SYSTEM_CONFIG.features[feature];
  },
  
  // Obter configuração da API
  getApiConfig: () => ({
    baseURL: SYSTEM_CONFIG.api.baseURL,
    timeout: SYSTEM_CONFIG.api.timeout,
    retries: SYSTEM_CONFIG.api.retries
  }),
  
  // Obter configurações de SMS
  getSmsConfig: () => SYSTEM_CONFIG.sms,
  
  // Obter configurações de UI
  getUiConfig: () => SYSTEM_CONFIG.ui,
  
  // Verificar ambiente
  isDevelopment: () => SYSTEM_CONFIG.app.environment === 'development',
  isProduction: () => SYSTEM_CONFIG.app.environment === 'production',
  
  // Obter informações da versão
  getVersion: () => SYSTEM_CONFIG.app.version,
  getAppName: () => SYSTEM_CONFIG.app.name
};

// ===== HOOK PARA ACESSAR CONFIGURAÇÕES =====

export function useSystemConfig() {
  return {
    config: SYSTEM_CONFIG,
    utils: configUtils,
    
    // Shortcuts para configurações mais usadas
    api: SYSTEM_CONFIG.api,
    sms: SYSTEM_CONFIG.sms,
    ui: SYSTEM_CONFIG.ui,
    features: SYSTEM_CONFIG.features,
    
    // Funções utilitárias
    isFeatureEnabled: configUtils.isFeatureEnabled,
    isDevelopment: configUtils.isDevelopment,
    isProduction: configUtils.isProduction
  };
}

// ===== TIPOS PARA TYPESCRIPT =====

export type SystemConfig = typeof SYSTEM_CONFIG;
export type AppFeatures = keyof typeof SYSTEM_CONFIG.features;
export type ThemeColors = keyof typeof SYSTEM_CONFIG.ui.theme;
export type NotificationPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';

// ===== CONSTANTES ÚTEIS =====

export const ROUTES = {
  // Autenticação
  LOGIN: '/login',
  REGISTER: '/register',
  RESET_PASSWORD: '/reset-password',
  
  // Dashboard
  DASHBOARD: '/dashboard',
  
  // SMS
  SMS_SEND: '/sms/send',
  SMS_QUICK: '/sms/quick',
  SMS_HISTORY: '/sms/history',
  SMS_REPORTS: '/sms/reports',
  
  // Contatos
  CONTACTS: '/contacts',
  CONTACTS_NEW: '/contacts/new',
  CONTACTS_IMPORT: '/contacts/import',
  CONTACTS_GROUPS: '/contacts/groups',
  
  // Campanhas
  CAMPAIGNS: '/campaigns',
  CAMPAIGNS_NEW: '/campaigns/new',
  CAMPAIGNS_TEMPLATES: '/campaigns/templates',
  CAMPAIGNS_SCHEDULED: '/campaigns/scheduled',
  
  // Templates
  TEMPLATES: '/templates',
  TEMPLATES_NEW: '/templates/new',
  TEMPLATES_LIBRARY: '/templates/library',
  
  // Relatórios
  REPORTS: '/reports',
  REPORTS_SMS: '/reports/sms',
  REPORTS_CAMPAIGNS: '/reports/campaigns',
  REPORTS_COSTS: '/reports/costs',
  
  // Configurações
  SETTINGS: '/settings',
  SETTINGS_PROFILE: '/settings/profile',
  SETTINGS_ACCOUNT: '/settings/account',
  SETTINGS_NOTIFICATIONS: '/settings/notifications',
  SETTINGS_SECURITY: '/settings/security',
  SETTINGS_API: '/settings/api'
} as const;

export const API_ENDPOINTS = {
  // Autenticação
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
    RESET_PASSWORD: '/auth/reset-password',
    CHANGE_PASSWORD: '/auth/change-password'
  },
  
  // SMS
  SMS: {
    SEND: '/sms/send',
    BULK_SEND: '/sms/bulk-send',
    HISTORY: '/sms/history',
    STATS: '/sms/stats',
    STATUS: '/sms/status'
  },
  
  // Contatos
  CONTACTS: {
    LIST: '/contacts',
    CREATE: '/contacts',
    UPDATE: '/contacts',
    DELETE: '/contacts',
    IMPORT: '/contacts/import',
    EXPORT: '/contacts/export',
    BULK_DELETE: '/contacts/bulk-delete'
  },
  
  // Campanhas
  CAMPAIGNS: {
    LIST: '/campaigns',
    CREATE: '/campaigns',
    UPDATE: '/campaigns',
    DELETE: '/campaigns',
    START: '/campaigns/start',
    PAUSE: '/campaigns/pause',
    STATS: '/campaigns/stats'
  },
  
  // Templates
  TEMPLATES: {
    LIST: '/templates',
    CREATE: '/templates',
    UPDATE: '/templates',
    DELETE: '/templates',
    DUPLICATE: '/templates/duplicate'
  },
  
  // Sistema
  SYSTEM: {
    STATUS: '/system/status',
    STATS: '/system/stats',
    HEALTH: '/system/health'
  }
} as const;

export const PERMISSIONS = {
  // SMS
  SMS_SEND: 'sms:send',
  SMS_VIEW: 'sms:view',
  SMS_DELETE: 'sms:delete',
  
  // Contatos
  CONTACTS_VIEW: 'contacts:view',
  CONTACTS_CREATE: 'contacts:create',
  CONTACTS_UPDATE: 'contacts:update',
  CONTACTS_DELETE: 'contacts:delete',
  CONTACTS_IMPORT: 'contacts:import',
  CONTACTS_EXPORT: 'contacts:export',
  
  // Campanhas
  CAMPAIGNS_VIEW: 'campaigns:view',
  CAMPAIGNS_CREATE: 'campaigns:create',
  CAMPAIGNS_UPDATE: 'campaigns:update',
  CAMPAIGNS_DELETE: 'campaigns:delete',
  CAMPAIGNS_START: 'campaigns:start',
  
  // Templates
  TEMPLATES_VIEW: 'templates:view',
  TEMPLATES_CREATE: 'templates:create',
  TEMPLATES_UPDATE: 'templates:update',
  TEMPLATES_DELETE: 'templates:delete',
  
  // Relatórios
  REPORTS_VIEW: 'reports:view',
  REPORTS_EXPORT: 'reports:export',
  
  // Sistema
  SYSTEM_VIEW: 'system:view',
  SYSTEM_CONFIG: 'system:config',
  
  // Usuários
  USERS_VIEW: 'users:view',
  USERS_CREATE: 'users:create',
  USERS_UPDATE: 'users:update',
  USERS_DELETE: 'users:delete'
} as const;

export default AppProviders;
