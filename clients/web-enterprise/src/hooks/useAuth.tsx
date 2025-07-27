// Hook de Autenticação Integrado com API
// Gerenciamento completo de autenticação com context e persistência

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

// ===== TIPOS =====

interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  avatar_url?: string;
  role: 'admin' | 'user' | 'operator';
  permissions: string[];
  company?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  preferences?: {
    theme: 'light' | 'dark';
    language: 'pt' | 'en';
    notifications: {
      email: boolean;
      sms: boolean;
      push: boolean;
    };
  };
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
  password_confirmation: string;
  phone?: string;
  company?: string;
}

interface AuthContextType {
  // Estado
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  
  // Ações
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  
  // Verificações
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

// ===== CONTEXT =====

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ===== HOOK =====

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
}

// ===== PROVIDER =====

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false
  });

  const router = useRouter();

  // ===== FUNÇÕES AUXILIARES =====

  const setAuthData = (user: User, token: string) => {
    // Salvar no localStorage
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(user));
    
    // Configurar header do API client
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    // Atualizar estado
    setAuthState({
      user,
      token,
      isLoading: false,
      isAuthenticated: true
    });
  };

  const clearAuthData = () => {
    // Limpar localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    
    // Limpar header do API client
    delete apiClient.defaults.headers.common['Authorization'];
    
    // Atualizar estado
    setAuthState({
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false
    });
  };

  // ===== AÇÕES DE AUTENTICAÇÃO =====

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      const response = await apiClient.post('/auth/login', credentials);
      const { user, token, expires_in } = response.data;
      
      setAuthData(user, token);
      
      // Configurar refresh automático
      if (expires_in) {
        setTimeout(() => {
          refreshToken().catch(() => {
            toast.error('Sessão expirada. Faça login novamente.');
            logout();
          });
        }, (expires_in - 60) * 1000); // Refresh 1 minuto antes de expirar
      }
      
      toast.success(`Bem-vindo, ${user.name}!`);
      
      // Redirecionar para dashboard ou página anterior
      const returnUrl = router.query.returnUrl as string || '/dashboard';
      router.push(returnUrl);
      
    } catch (error: any) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      
      const message = error.response?.data?.message || 'Erro ao fazer login';
      toast.error(message);
      throw error;
    }
  };

  const register = async (data: RegisterData): Promise<void> => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      const response = await apiClient.post('/auth/register', data);
      const { user, token } = response.data;
      
      setAuthData(user, token);
      
      toast.success('Conta criada com sucesso!');
      router.push('/dashboard');
      
    } catch (error: any) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      
      const message = error.response?.data?.message || 'Erro ao criar conta';
      toast.error(message);
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Tentar fazer logout no servidor
      if (authState.token) {
        await apiClient.post('/auth/logout');
      }
    } catch (error) {
      // Ignorar erros de logout no servidor
      console.warn('Erro ao fazer logout no servidor:', error);
    } finally {
      clearAuthData();
      router.push('/login');
    }
  };

  const refreshToken = async (): Promise<void> => {
    try {
      const response = await apiClient.post('/auth/refresh');
      const { user, token } = response.data;
      
      setAuthData(user, token);
      
    } catch (error) {
      clearAuthData();
      throw error;
    }
  };

  const updateProfile = async (data: Partial<User>): Promise<void> => {
    try {
      const response = await apiClient.put('/auth/profile', data);
      const updatedUser = response.data;
      
      setAuthState(prev => ({
        ...prev,
        user: updatedUser
      }));
      
      // Atualizar localStorage
      localStorage.setItem('auth_user', JSON.stringify(updatedUser));
      
      toast.success('Perfil atualizado com sucesso!');
      
    } catch (error: any) {
      const message = error.response?.data?.message || 'Erro ao atualizar perfil';
      toast.error(message);
      throw error;
    }
  };

  const changePassword = async (
    currentPassword: string, 
    newPassword: string
  ): Promise<void> => {
    try {
      await apiClient.put('/auth/password', {
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirmation: newPassword
      });
      
      toast.success('Senha alterada com sucesso!');
      
    } catch (error: any) {
      const message = error.response?.data?.message || 'Erro ao alterar senha';
      toast.error(message);
      throw error;
    }
  };

  // ===== VERIFICAÇÕES DE PERMISSÃO =====

  const hasPermission = (permission: string): boolean => {
    if (!authState.user) return false;
    return authState.user.permissions.includes(permission);
  };

  const hasRole = (role: string): boolean => {
    if (!authState.user) return false;
    return authState.user.role === role;
  };

  // ===== EFEITOS =====

  // Inicializar autenticação
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const userStr = localStorage.getItem('auth_user');
        
        if (token && userStr) {
          const user = JSON.parse(userStr);
          
          // Configurar header do API client
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Verificar se o token ainda é válido
          try {
            const response = await apiClient.get('/auth/me');
            const currentUser = response.data;
            
            setAuthData(currentUser, token);
          } catch (error) {
            // Token inválido, limpar dados
            clearAuthData();
          }
        } else {
          setAuthState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        console.error('Erro ao inicializar autenticação:', error);
        clearAuthData();
      }
    };

    initAuth();
  }, []);

  // Interceptor para lidar com respostas 401
  useEffect(() => {
    const interceptor = apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && authState.isAuthenticated) {
          // Token expirado, tentar refresh
          try {
            await refreshToken();
            // Repetir a requisição original
            return apiClient.request(error.config);
          } catch (refreshError) {
            // Refresh falhou, fazer logout
            clearAuthData();
            router.push('/login');
            toast.error('Sessão expirada. Faça login novamente.');
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      apiClient.interceptors.response.eject(interceptor);
    };
  }, [authState.isAuthenticated]);

  // ===== PROVIDER VALUE =====

  const value: AuthContextType = {
    // Estado
    user: authState.user,
    token: authState.token,
    isLoading: authState.isLoading,
    isAuthenticated: authState.isAuthenticated,
    
    // Ações
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
    changePassword,
    
    // Verificações
    hasPermission,
    hasRole
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ===== HOOK PARA VERIFICAR AUTENTICAÇÃO =====

export function useRequireAuth(redirectTo: string = '/login') {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push({
        pathname: redirectTo,
        query: { returnUrl: router.asPath }
      });
    }
  }, [isAuthenticated, isLoading, router, redirectTo]);

  return { isAuthenticated, isLoading };
}

// ===== HOOK PARA VERIFICAR PERMISSÕES =====

export function usePermission(permission: string) {
  const { hasPermission, user, isLoading } = useAuth();
  
  return {
    hasPermission: hasPermission(permission),
    user,
    isLoading
  };
}

// ===== COMPONENTE DE PROTEÇÃO DE ROTA =====

interface ProtectedRouteProps {
  children: ReactNode;
  requiredPermission?: string;
  requiredRole?: string;
  fallback?: ReactNode;
}

export function ProtectedRoute({ 
  children, 
  requiredPermission, 
  requiredRole,
  fallback 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, hasPermission, hasRole } = useAuth();
  
  useRequireAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // useRequireAuth vai redirecionar
  }

  // Verificar permissão específica
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Acesso Negado
            </h2>
            <p className="text-gray-600">
              Você não tem permissão para acessar esta página.
            </p>
          </div>
        </div>
      )
    );
  }

  // Verificar role específico
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Acesso Restrito
            </h2>
            <p className="text-gray-600">
              Esta página é restrita para {requiredRole}s.
            </p>
          </div>
        </div>
      )
    );
  }

  return <>{children}</>;
}

export default useAuth;
