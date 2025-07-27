import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { QueryClient, QueryClientProvider } from 'react-query';

// Context providers
import { AuthProvider } from '@/contexts/AuthContext';
import { useAuth } from '@/hooks/useAuth';

// Components
import AdminLayout from '@/components/AdminLayout';
import LoadingSpinner from '@/components/LoadingSpinner';

// Pages
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import UsersManagementPage from '@/pages/UsersManagementPage';
import SystemConfigurationPage from '@/pages/SystemConfigurationPage';
import SystemMonitoringPage from '@/pages/SystemMonitoringPage';
import LogsAuditPage from '@/pages/LogsAuditPage';
import HardwareManagementPage from '@/pages/HardwareManagementPage';
import GlobalReportsPage from '@/pages/GlobalReportsPage';
import SecurityPage from '@/pages/SecurityPage';

// Configuração do React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 2 * 60 * 1000, // 2 minutos (admin precisa dados mais frescos)
    },
  },
});

// Tema administrativo - mais sério e focado em dados
const adminTheme = createTheme({
  palette: {
    mode: 'dark', // Por padrão modo escuro para administradores
    primary: {
      main: '#dc2626', // Vermelho administrativo
      light: '#f87171',
      dark: '#991b1b',
    },
    secondary: {
      main: '#ea580c', // Laranja complementar
      light: '#fb923c',
      dark: '#c2410c',
    },
    background: {
      default: '#0f172a', // Azul escuro profissional
      paper: '#1e293b',
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#cbd5e1',
    },
    error: {
      main: '#ef4444',
    },
    warning: {
      main: '#f59e0b',
    },
    success: {
      main: '#10b981',
    },
    info: {
      main: '#3b82f6',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 700,
      fontSize: '1.875rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1.125rem',
    },
    body1: {
      fontSize: '0.95rem',
    },
    body2: {
      fontSize: '0.875rem',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          backgroundImage: 'none',
          border: '1px solid rgba(148, 163, 184, 0.1)',
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: 'none',
          '& .MuiDataGrid-cell': {
            borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1e293b',
          borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
        },
      },
    },
  },
});

// Componente para rotas protegidas (apenas admins)
const AdminProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner message="Verificando permissões..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Verificar se é admin ou super_admin
  if (!user || !['admin', 'super_admin'].includes(user.user_type)) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        flexDirection="column"
        gap={2}
      >
        <Box fontSize="4rem">🚫</Box>
        <Box textAlign="center">
          <h2>Acesso Negado</h2>
          <p>Esta interface é restrita a administradores do sistema.</p>
          <p>Contacte o administrador se precisa de acesso.</p>
        </Box>
      </Box>
    );
  }

  return <>{children}</>;
};

// Componente principal das rotas administrativas
const AdminApp: React.FC = () => {
  return (
    <AdminLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/users" element={<UsersManagementPage />} />
        <Route path="/system-config" element={<SystemConfigurationPage />} />
        <Route path="/monitoring" element={<SystemMonitoringPage />} />
        <Route path="/logs-audit" element={<LogsAuditPage />} />
        <Route path="/hardware" element={<HardwareManagementPage />} />
        <Route path="/reports" element={<GlobalReportsPage />} />
        <Route path="/security" element={<SecurityPage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AdminLayout>
  );
};

// Componente principal da aplicação administrativa
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={adminTheme}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={5}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          dense
        >
          <AuthProvider>
            <Router>
              <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
                <Routes>
                  <Route path="/login" element={<LoginPage />} />
                  <Route
                    path="/*"
                    element={
                      <AdminProtectedRoute>
                        <AdminApp />
                      </AdminProtectedRoute>
                    }
                  />
                </Routes>
              </Box>
            </Router>
          </AuthProvider>
        </SnackbarProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
