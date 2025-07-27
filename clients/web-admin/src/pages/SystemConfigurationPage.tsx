import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Alert,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  InputAdornment,
} from '@mui/material';
import {
  Save,
  Refresh,
  TestConnection,
  Security,
  Sms,
  Email,
  Phone,
  Language,
  Schedule,
  Storage,
  Visibility,
  VisibilityOff,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { useSnackbar } from 'notistack';

interface SystemConfig {
  // Configurações SMS/USSD
  sms_provider: 'twilio' | 'modem';
  twilio_account_sid: string;
  twilio_auth_token: string;
  twilio_phone_number: string;
  modem_port: string;
  modem_baudrate: number;
  default_country_code: string;
  
  // Configurações de Email
  smtp_server: string;
  smtp_port: number;
  smtp_username: string;
  smtp_password: string;
  smtp_use_tls: boolean;
  default_from_email: string;
  
  // Configurações de Sistema
  system_name: string;
  system_timezone: string;
  default_language: string;
  max_sms_per_day: number;
  max_bulk_sms: number;
  session_timeout: number;
  
  // Configurações de Segurança
  require_2fa: boolean;
  password_min_length: number;
  password_require_uppercase: boolean;
  password_require_lowercase: boolean;
  password_require_numbers: boolean;
  password_require_symbols: boolean;
  max_login_attempts: number;
  lockout_duration: number;
  
  // Configurações de Base de Dados
  db_backup_enabled: boolean;
  db_backup_frequency: 'daily' | 'weekly' | 'monthly';
  db_retention_days: number;
  
  // Configurações de Logs
  log_level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  log_retention_days: number;
  log_max_size_mb: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

const SystemConfigurationPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showTwilioToken, setShowTwilioToken] = useState(false);
  const [showSmtpPassword, setShowSmtpPassword] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<{
    twilio: 'pending' | 'success' | 'error';
    smtp: 'pending' | 'success' | 'error';
    modem: 'pending' | 'success' | 'error';
  }>({
    twilio: 'pending',
    smtp: 'pending',
    modem: 'pending',
  });

  const { enqueueSnackbar } = useSnackbar();
  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isDirty },
  } = useForm<SystemConfig>();

  const smsProvider = watch('sms_provider');

  // Configuração simulada (substituir por chamada à API)
  const mockConfig: SystemConfig = {
    sms_provider: 'twilio',
    twilio_account_sid: 'AC1234567890abcdef',
    twilio_auth_token: '*********************',
    twilio_phone_number: '+1234567890',
    modem_port: 'COM3',
    modem_baudrate: 9600,
    default_country_code: '+258',
    smtp_server: 'smtp.gmail.com',
    smtp_port: 587,
    smtp_username: 'noreply@amamessage.com',
    smtp_password: '*********************',
    smtp_use_tls: true,
    default_from_email: 'noreply@amamessage.com',
    system_name: 'AMA MESSAGE',
    system_timezone: 'Africa/Maputo',
    default_language: 'pt',
    max_sms_per_day: 1000,
    max_bulk_sms: 500,
    session_timeout: 60,
    require_2fa: false,
    password_min_length: 8,
    password_require_uppercase: true,
    password_require_lowercase: true,
    password_require_numbers: true,
    password_require_symbols: false,
    max_login_attempts: 5,
    lockout_duration: 30,
    db_backup_enabled: true,
    db_backup_frequency: 'daily',
    db_retention_days: 90,
    log_level: 'INFO',
    log_retention_days: 30,
    log_max_size_mb: 100,
  };

  useEffect(() => {
    // Simular carregamento de configurações
    setTimeout(() => {
      setConfig(mockConfig);
      reset(mockConfig);
      setLoading(false);
    }, 1000);
  }, [reset]);

  const handleSaveConfig = async (data: SystemConfig) => {
    setSaving(true);
    try {
      // Simular salvamento
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setConfig(data);
      enqueueSnackbar('Configurações salvas com sucesso!', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Erro ao salvar configurações', { variant: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async (type: 'twilio' | 'smtp' | 'modem') => {
    setConnectionStatus(prev => ({ ...prev, [type]: 'pending' }));
    
    // Simular teste de conexão
    setTimeout(() => {
      const success = Math.random() > 0.3; // 70% de sucesso
      setConnectionStatus(prev => ({ 
        ...prev, 
        [type]: success ? 'success' : 'error' 
      }));
      
      enqueueSnackbar(
        `Teste de ${type.toUpperCase()}: ${success ? 'Sucesso' : 'Falha'}`,
        { variant: success ? 'success' : 'error' }
      );
    }, 2000);
  };

  const getConnectionStatusIcon = (status: 'pending' | 'success' | 'error') => {
    switch (status) {
      case 'success':
        return <CheckCircle color="success" />;
      case 'error':
        return <Warning color="error" />;
      default:
        return <TestConnection color="action" />;
    }
  };

  const passwordStrengthRules = [
    { key: 'password_require_uppercase', label: 'Letras maiúsculas' },
    { key: 'password_require_lowercase', label: 'Letras minúsculas' },
    { key: 'password_require_numbers', label: 'Números' },
    { key: 'password_require_symbols', label: 'Símbolos especiais' },
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="60vh">
        <Typography>Carregando configurações...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Configuração do Sistema
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configurações globais e parâmetros de sistema
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => reset(config!)}
            disabled={!isDirty}
          >
            Reverter
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSubmit(handleSaveConfig)}
            disabled={!isDirty || saving}
          >
            {saving ? 'Salvando...' : 'Salvar Alterações'}
          </Button>
        </Box>
      </Box>

      {/* Alertas */}
      {isDirty && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Existem alterações não salvas. Não se esqueça de salvar antes de sair.
        </Alert>
      )}

      {/* Tabs de Configuração */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab icon={<Sms />} label="SMS/USSD" />
            <Tab icon={<Email />} label="Email" />
            <Tab icon={<Security />} label="Segurança" />
            <Tab icon={<Storage />} label="Base de Dados" />
            <Tab icon={<Language />} label="Sistema" />
          </Tabs>
        </Box>

        <CardContent>
          {/* SMS/USSD Configuration */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Configurações SMS/USSD
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="sms_provider"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Provedor SMS</InputLabel>
                      <Select {...field} label="Provedor SMS">
                        <MenuItem value="twilio">Twilio (Cloud)</MenuItem>
                        <MenuItem value="modem">Modem Físico</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="default_country_code"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Código do País Padrão"
                      placeholder="+258"
                    />
                  )}
                />
              </Grid>

              {/* Configurações Twilio */}
              {smsProvider === 'twilio' && (
                <>
                  <Grid item xs={12}>
                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                      <Typography variant="h6">Configurações Twilio</Typography>
                      <Tooltip title="Testar conexão Twilio">
                        <IconButton
                          onClick={() => handleTestConnection('twilio')}
                          color="primary"
                        >
                          {getConnectionStatusIcon(connectionStatus.twilio)}
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Controller
                      name="twilio_account_sid"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Account SID"
                          placeholder="AC..."
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Controller
                      name="twilio_auth_token"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Auth Token"
                          type={showTwilioToken ? 'text' : 'password'}
                          InputProps={{
                            endAdornment: (
                              <InputAdornment position="end">
                                <IconButton
                                  onClick={() => setShowTwilioToken(!showTwilioToken)}
                                  edge="end"
                                >
                                  {showTwilioToken ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                              </InputAdornment>
                            ),
                          }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Controller
                      name="twilio_phone_number"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Número Twilio"
                          placeholder="+1234567890"
                        />
                      )}
                    />
                  </Grid>
                </>
              )}

              {/* Configurações Modem */}
              {smsProvider === 'modem' && (
                <>
                  <Grid item xs={12}>
                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                      <Typography variant="h6">Configurações Modem</Typography>
                      <Tooltip title="Testar conexão modem">
                        <IconButton
                          onClick={() => handleTestConnection('modem')}
                          color="primary"
                        >
                          {getConnectionStatusIcon(connectionStatus.modem)}
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Controller
                      name="modem_port"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Porta do Modem"
                          placeholder="COM3 ou /dev/ttyUSB0"
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Controller
                      name="modem_baudrate"
                      control={control}
                      render={({ field }) => (
                        <FormControl fullWidth>
                          <InputLabel>Baud Rate</InputLabel>
                          <Select {...field} label="Baud Rate">
                            <MenuItem value={9600}>9600</MenuItem>
                            <MenuItem value={19200}>19200</MenuItem>
                            <MenuItem value={38400}>38400</MenuItem>
                            <MenuItem value={57600}>57600</MenuItem>
                            <MenuItem value={115200}>115200</MenuItem>
                          </Select>
                        </FormControl>
                      )}
                    />
                  </Grid>
                </>
              )}
            </Grid>
          </TabPanel>

          {/* Email Configuration */}
          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Typography variant="h6">Configurações de Email</Typography>
                  <Tooltip title="Testar conexão SMTP">
                    <IconButton
                      onClick={() => handleTestConnection('smtp')}
                      color="primary"
                    >
                      {getConnectionStatusIcon(connectionStatus.smtp)}
                    </IconButton>
                  </Tooltip>
                </Box>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="smtp_server"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Servidor SMTP"
                      placeholder="smtp.gmail.com"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="smtp_port"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Porta SMTP"
                      type="number"
                      placeholder="587"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="smtp_username"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Utilizador SMTP"
                      placeholder="usuario@exemplo.com"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="smtp_password"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Password SMTP"
                      type={showSmtpPassword ? 'text' : 'password'}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowSmtpPassword(!showSmtpPassword)}
                              edge="end"
                            >
                              {showSmtpPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="default_from_email"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Email Padrão (From)"
                      placeholder="noreply@amamessage.com"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="smtp_use_tls"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch {...field} checked={field.value} />}
                      label="Usar TLS/SSL"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Security Configuration */}
          <TabPanel value={activeTab} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Configurações de Segurança
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="require_2fa"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch {...field} checked={field.value} />}
                      label="Exigir Autenticação de Dois Fatores (2FA)"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="session_timeout"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Timeout da Sessão (minutos)"
                      type="number"
                      helperText="0 = sem timeout"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Política de Passwords
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="password_min_length"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Comprimento Mínimo"
                      type="number"
                      inputProps={{ min: 4, max: 32 }}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Requisitos da Password:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {passwordStrengthRules.map((rule) => (
                      <Controller
                        key={rule.key}
                        name={rule.key as keyof SystemConfig}
                        control={control}
                        render={({ field }) => (
                          <Chip
                            label={rule.label}
                            color={field.value ? 'primary' : 'default'}
                            onClick={() => field.onChange(!field.value)}
                            variant={field.value ? 'filled' : 'outlined'}
                            size="small"
                            clickable
                          />
                        )}
                      />
                    ))}
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Proteção contra Ataques
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="max_login_attempts"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Máximo de Tentativas de Login"
                      type="number"
                      inputProps={{ min: 3, max: 10 }}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="lockout_duration"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Duração do Bloqueio (minutos)"
                      type="number"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Database Configuration */}
          <TabPanel value={activeTab} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Configurações de Base de Dados
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="db_backup_enabled"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch {...field} checked={field.value} />}
                      label="Ativar Backup Automático"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="db_backup_frequency"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Frequência de Backup</InputLabel>
                      <Select {...field} label="Frequência de Backup">
                        <MenuItem value="daily">Diário</MenuItem>
                        <MenuItem value="weekly">Semanal</MenuItem>
                        <MenuItem value="monthly">Mensal</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="db_retention_days"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Retenção de Backups (dias)"
                      type="number"
                      helperText="Backups mais antigos serão eliminados"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Configurações de Logs
                </Typography>
              </Grid>

              <Grid item xs={12} md={4}>
                <Controller
                  name="log_level"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Nível de Log</InputLabel>
                      <Select {...field} label="Nível de Log">
                        <MenuItem value="DEBUG">DEBUG</MenuItem>
                        <MenuItem value="INFO">INFO</MenuItem>
                        <MenuItem value="WARNING">WARNING</MenuItem>
                        <MenuItem value="ERROR">ERROR</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <Controller
                  name="log_retention_days"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Retenção de Logs (dias)"
                      type="number"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <Controller
                  name="log_max_size_mb"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Tamanho Máximo por Log (MB)"
                      type="number"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* System Configuration */}
          <TabPanel value={activeTab} index={4}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Configurações Gerais do Sistema
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="system_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Nome do Sistema"
                      placeholder="AMA MESSAGE"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="system_timezone"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Fuso Horário</InputLabel>
                      <Select {...field} label="Fuso Horário">
                        <MenuItem value="Africa/Maputo">Africa/Maputo (GMT+2)</MenuItem>
                        <MenuItem value="Africa/Johannesburg">Africa/Johannesburg (GMT+2)</MenuItem>
                        <MenuItem value="UTC">UTC (GMT+0)</MenuItem>
                        <MenuItem value="Europe/Lisbon">Europe/Lisbon (GMT+1)</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="default_language"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Idioma Padrão</InputLabel>
                      <Select {...field} label="Idioma Padrão">
                        <MenuItem value="pt">Português</MenuItem>
                        <MenuItem value="en">English</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Limites de Sistema
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="max_sms_per_day"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Máximo SMS por Dia (por utilizador)"
                      type="number"
                      helperText="0 = sem limite"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="max_bulk_sms"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Máximo SMS em Massa (por envio)"
                      type="number"
                      helperText="0 = sem limite"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SystemConfigurationPage;
