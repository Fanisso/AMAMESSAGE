import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserResponse, LoginRequest, RegisterRequest } from '@/shared/types';
import { ApiClient } from '@/shared/api';

interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Configurar cliente API
const apiClient = new ApiClient({
  baseURL: process.env.REACT_APP_API_URL || '/api/v2',
  timeout: 10000,
});

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!user;

  // Verificar token ao carregar a aplicação
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          apiClient.setToken(token);
          const userProfile = await apiClient.getCurrentUser();
          setUser(userProfile);
        } catch (error) {
          console.error('Erro ao verificar token:', error);
          localStorage.removeItem('authToken');
          apiClient.clearToken();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      setLoading(true);
      const response = await apiClient.login(credentials);
      
      // Armazenar token
      localStorage.setItem('authToken', response.access_token);
      apiClient.setToken(response.access_token);
      
      // Obter dados do usuário
      const userProfile = await apiClient.getCurrentUser();
      setUser(userProfile);
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: RegisterRequest) => {
    try {
      setLoading(true);
      await apiClient.register(userData);
      
      // Fazer login automático após registro
      await login({
        email: userData.email,
        password: userData.password,
      });
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    apiClient.clearToken();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userProfile = await apiClient.getCurrentUser();
      setUser(userProfile);
    } catch (error) {
      console.error('Erro ao atualizar usuário:', error);
      logout();
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
