import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  CircularProgress,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  AdminPanelSettings,
  Login as LoginIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useForm, Controller } from 'react-hook-form';

interface LoginFormData {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { login, loading } = useAuth();

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const handleLogin = async (data: LoginFormData) => {
    setLoginError(null);
    
    const success = await login(data.email, data.password);
    
    if (success) {
      navigate('/dashboard');
    } else {
      setLoginError('Email ou password incorretos. Contacte o administrador do sistema.');
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        padding: 3,
      }}
    >
      <Card
        sx={{
          maxWidth: 400,
          width: '100%',
          borderRadius: 3,
          boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
          backgroundColor: 'background.paper',
        }}
      >
        <CardContent sx={{ p: 4 }}>
          {/* Logo e Título */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <AdminPanelSettings 
              sx={{ 
                fontSize: 48, 
                color: 'primary.main', 
                mb: 2,
                filter: 'drop-shadow(0 4px 8px rgba(220,38,38,0.3))',
              }} 
            />
            <Typography variant="h4" fontWeight="bold" color="primary.main" gutterBottom>
              AMA MESSAGE
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Interface Administrativa
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Acesso restrito a administradores do sistema
            </Typography>
          </Box>

          {/* Alerta de erro */}
          {loginError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {loginError}
            </Alert>
          )}

          {/* Credenciais de demonstração */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              <strong>Credenciais de demonstração:</strong>
            </Typography>
            <Typography variant="body2">
              Email: admin@amamessage.com<br />
              Password: admin123
            </Typography>
          </Alert>

          {/* Formulário de Login */}
          <form onSubmit={handleSubmit(handleLogin)}>
            <Box sx={{ mb: 3 }}>
              <Controller
                name="email"
                control={control}
                rules={{
                  required: 'Email é obrigatório',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email inválido',
                  },
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Email de Administrador"
                    type="email"
                    error={!!errors.email}
                    helperText={errors.email?.message}
                    disabled={loading}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                      },
                    }}
                  />
                )}
              />
            </Box>

            <Box sx={{ mb: 4 }}>
              <Controller
                name="password"
                control={control}
                rules={{
                  required: 'Password é obrigatória',
                  minLength: {
                    value: 6,
                    message: 'Password deve ter pelo menos 6 caracteres',
                  },
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    error={!!errors.password}
                    helperText={errors.password?.message}
                    disabled={loading}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label="toggle password visibility"
                            onClick={togglePasswordVisibility}
                            edge="end"
                            disabled={loading}
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                      },
                    }}
                  />
                )}
              />
            </Box>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
              sx={{
                borderRadius: 2,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                textTransform: 'none',
                background: loading 
                  ? 'rgba(220, 38, 38, 0.5)' 
                  : 'linear-gradient(45deg, #dc2626 30%, #ea580c 90%)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #b91c1c 30%, #c2410c 90%)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 6px 20px rgba(220, 38, 38, 0.4)',
                },
                transition: 'all 0.2s ease-in-out',
              }}
            >
              {loading ? 'Autenticando...' : 'Entrar no Sistema'}
            </Button>
          </form>

          {/* Rodapé */}
          <Box sx={{ textAlign: 'center', mt: 4, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary">
              © 2024 AMA MESSAGE - Sistema de Administração
            </Typography>
            <br />
            <Typography variant="caption" color="text.secondary">
              Contacte o administrador do sistema para obter acesso
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginPage;
