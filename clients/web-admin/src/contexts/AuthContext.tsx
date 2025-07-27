import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserResponse, UserType } from '@/shared/types';

interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  updateUser: (userData: Partial<UserResponse>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Simular dados de um administrador
  const mockAdminUser: UserResponse = {
    id: 1,
    email: 'admin@amamessage.com',
    full_name: 'Administrador Principal',
    user_type: 'super_admin' as UserType,
    is_active: true,
    created_at: new Date('2024-01-01'),
    last_login: new Date(),
    phone_number: '+258823456789',
    company: 'AMA MESSAGE',
    timezone: 'Africa/Maputo',
    language: 'pt',
  };

  useEffect(() => {
    // Simular verificação de autenticação inicial
    const checkAuth = async () => {
      try {
        // Verificar se existe token armazenado
        const token = localStorage.getItem('admin_token');
        if (token) {
          // Simular validação do token
          await new Promise(resolve => setTimeout(resolve, 1000));
          setUser(mockAdminUser);
        }
      } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        localStorage.removeItem('admin_token');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setLoading(true);
    try {
      // Simular chamada de login
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Verificar credenciais simuladas
      if (email === 'admin@amamessage.com' && password === 'admin123') {
        // Simular token JWT
        const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_admin_token';
        localStorage.setItem('admin_token', token);
        
        setUser(mockAdminUser);
        return true;
      } else {
        throw new Error('Credenciais inválidas');
      }
    } catch (error) {
      console.error('Erro no login:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setUser(null);
  };

  const updateUser = (userData: Partial<UserResponse>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
