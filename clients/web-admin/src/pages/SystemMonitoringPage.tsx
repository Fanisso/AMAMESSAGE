import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  IconButton,
  Tooltip,
  RefreshIcon,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  Error,
  CheckCircle,
  Storage,
  Memory,
  Speed,
  NetworkCheck,
  Sms,
  People,
  Schedule,
  Refresh,
  Notifications,
  Phone,
  Computer,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useSnackbar } from 'notistack';

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_io: { sent: number; received: number };
  active_connections: number;
  uptime: number;
  last_updated: Date;
}

interface ServiceStatus {
  name: string;
  status: 'online' | 'offline' | 'warning';
  uptime: number;
  response_time: number;
  last_check: Date;
}

interface SMSMetrics {
  sent_today: number;
  failed_today: number;
  pending: number;
  success_rate: number;
  avg_delivery_time: number;
}

interface Alert {
  id: number;
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  resolved: boolean;
}

interface HourlyData {
  time: string;
  sms_sent: number;
  users_active: number;
  cpu_usage: number;
  memory_usage: number;
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

const SystemMonitoringPage: React.FC = () => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [smsMetrics, setSmsMetrics] = useState<SMSMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [hourlyData, setHourlyData] = useState<HourlyData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { enqueueSnackbar } = useSnackbar();

  // Dados simulados
  const mockSystemMetrics: SystemMetrics = {
    cpu_usage: 45.2,
    memory_usage: 67.8,
    disk_usage: 34.1,
    network_io: { sent: 1024, received: 2048 },
    active_connections: 127,
    uptime: 172800, // 2 dias em segundos
    last_updated: new Date(),
  };

  const mockServices: ServiceStatus[] = [
    {
      name: 'API Backend',
      status: 'online',
      uptime: 99.9,
      response_time: 85,
      last_check: new Date(),
    },
    {
      name: 'Base de Dados',
      status: 'online',
      uptime: 99.8,
      response_time: 12,
      last_check: new Date(),
    },
    {
      name: 'Twilio SMS',
      status: 'online',
      uptime: 98.5,
      response_time: 450,
      last_check: new Date(),
    },
    {
      name: 'Modem SMS',
      status: 'warning',
      uptime: 95.2,
      response_time: 1200,
      last_check: new Date(),
    },
    {
      name: 'Redis Cache',
      status: 'online',
      uptime: 99.7,
      response_time: 5,
      last_check: new Date(),
    },
    {
      name: 'Email SMTP',
      status: 'offline',
      uptime: 87.3,
      response_time: 0,
      last_check: new Date(Date.now() - 300000), // 5 min atrás
    },
  ];

  const mockSmsMetrics: SMSMetrics = {
    sent_today: 1247,
    failed_today: 23,
    pending: 45,
    success_rate: 98.2,
    avg_delivery_time: 2.3,
  };

  const mockAlerts: Alert[] = [
    {
      id: 1,
      type: 'error',
      title: 'Serviço SMTP Offline',
      message: 'O serviço de email SMTP está offline há mais de 5 minutos. Verificar configurações.',
      timestamp: new Date(Date.now() - 300000),
      resolved: false,
    },
    {
      id: 2,
      type: 'warning',
      title: 'Modem SMS Lento',
      message: 'O modem SMS está com tempo de resposta elevado (>1s). Verificar conexão.',
      timestamp: new Date(Date.now() - 600000),
      resolved: false,
    },
    {
      id: 3,
      type: 'info',
      title: 'Backup Concluído',
      message: 'Backup diário da base de dados concluído com sucesso.',
      timestamp: new Date(Date.now() - 3600000),
      resolved: true,
    },
  ];

  const mockHourlyData: HourlyData[] = [
    { time: '00:00', sms_sent: 23, users_active: 5, cpu_usage: 25, memory_usage: 45 },
    { time: '01:00', sms_sent: 15, users_active: 3, cpu_usage: 20, memory_usage: 43 },
    { time: '02:00', sms_sent: 8, users_active: 2, cpu_usage: 18, memory_usage: 42 },
    { time: '03:00', sms_sent: 12, users_active: 1, cpu_usage: 15, memory_usage: 40 },
    { time: '04:00', sms_sent: 18, users_active: 4, cpu_usage: 22, memory_usage: 44 },
    { time: '05:00', sms_sent: 45, users_active: 12, cpu_usage: 35, memory_usage: 52 },
    { time: '06:00', sms_sent: 89, users_active: 23, cpu_usage: 45, memory_usage: 58 },
    { time: '07:00', sms_sent: 156, users_active: 45, cpu_usage: 52, memory_usage: 62 },
    { time: '08:00', sms_sent: 234, users_active: 67, cpu_usage: 48, memory_usage: 65 },
    { time: '09:00', sms_sent: 189, users_active: 89, cpu_usage: 55, memory_usage: 68 },
    { time: '10:00', sms_sent: 267, users_active: 95, cpu_usage: 58, memory_usage: 72 },
    { time: '11:00', sms_sent: 298, users_active: 102, cpu_usage: 62, memory_usage: 75 },
  ];

  useEffect(() => {
    const loadData = () => {
      setSystemMetrics(mockSystemMetrics);
      setServices(mockServices);
      setSmsMetrics(mockSmsMetrics);
      setAlerts(mockAlerts);
      setHourlyData(mockHourlyData);
      setLoading(false);
    };

    loadData();

    // Auto-refresh a cada 30 segundos
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadData();
        enqueueSnackbar('Dados atualizados', { variant: 'info', autoHideDuration: 1000 });
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [autoRefresh, enqueueSnackbar]);

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'success';
      case 'warning': return 'warning';
      case 'offline': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle color="success" />;
      case 'warning': return <Warning color="warning" />;
      case 'offline': return <Error color="error" />;
      default: return <CheckCircle />;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error': return <Error color="error" />;
      case 'warning': return <Warning color="warning" />;
      case 'info': return <CheckCircle color="info" />;
      default: return <CheckCircle />;
    }
  };

  const resolveAlert = (alertId: number) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId ? { ...alert, resolved: true } : alert
    ));
    enqueueSnackbar('Alerta resolvido', { variant: 'success' });
  };

  const refreshData = () => {
    setLoading(true);
    setTimeout(() => {
      setSystemMetrics({ ...mockSystemMetrics, last_updated: new Date() });
      setLoading(false);
      enqueueSnackbar('Dados atualizados manualmente', { variant: 'success' });
    }, 1000);
  };

  if (loading && !systemMetrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="60vh">
        <Typography>Carregando dados de monitorização...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Monitorização do Sistema
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Estatísticas em tempo real e alertas do sistema
          </Typography>
        </Box>
        
        <Box display="flex" gap={1} alignItems="center">
          <Chip
            label={autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
            color={autoRefresh ? 'success' : 'default'}
            onClick={() => setAutoRefresh(!autoRefresh)}
            clickable
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshData}
            disabled={loading}
          >
            Atualizar
          </Button>
        </Box>
      </Box>

      {/* Alertas Ativos */}
      {alerts.filter(a => !a.resolved).length > 0 && (
        <Card sx={{ mb: 3, border: '1px solid', borderColor: 'warning.main' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom display="flex" alignItems="center">
              <Notifications sx={{ mr: 1 }} />
              Alertas Ativos ({alerts.filter(a => !a.resolved).length})
            </Typography>
            {alerts.filter(a => !a.resolved).slice(0, 3).map((alert) => (
              <Alert
                key={alert.id}
                severity={alert.type}
                sx={{ mb: 1 }}
                action={
                  <Button
                    size="small"
                    onClick={() => resolveAlert(alert.id)}
                  >
                    Resolver
                  </Button>
                }
              >
                <strong>{alert.title}</strong> - {alert.message}
              </Alert>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Métricas do Sistema */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    CPU
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {systemMetrics?.cpu_usage.toFixed(1)}%
                  </Typography>
                </Box>
                <Speed color="primary" fontSize="large" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={systemMetrics?.cpu_usage || 0}
                sx={{ mt: 1 }}
                color={systemMetrics && systemMetrics.cpu_usage > 80 ? 'error' : 'primary'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Memória
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {systemMetrics?.memory_usage.toFixed(1)}%
                  </Typography>
                </Box>
                <Memory color="info" fontSize="large" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={systemMetrics?.memory_usage || 0}
                sx={{ mt: 1 }}
                color={systemMetrics && systemMetrics.memory_usage > 85 ? 'error' : 'info'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Disco
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {systemMetrics?.disk_usage.toFixed(1)}%
                  </Typography>
                </Box>
                <Storage color="warning" fontSize="large" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={systemMetrics?.disk_usage || 0}
                sx={{ mt: 1 }}
                color={systemMetrics && systemMetrics.disk_usage > 90 ? 'error' : 'warning'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Uptime
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {formatUptime(systemMetrics?.uptime || 0)}
                  </Typography>
                </Box>
                <Computer color="success" fontSize="large" />
              </Box>
              <Typography variant="caption" color="text.secondary">
                Desde: {new Date(Date.now() - (systemMetrics?.uptime || 0) * 1000).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* SMS Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    SMS Enviados Hoje
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="primary.main">
                    {smsMetrics?.sent_today.toLocaleString()}
                  </Typography>
                </Box>
                <Sms color="primary" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Taxa de Sucesso
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {smsMetrics?.success_rate.toFixed(1)}%
                  </Typography>
                </Box>
                <CheckCircle color="success" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    SMS Pendentes
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="warning.main">
                    {smsMetrics?.pending}
                  </Typography>
                </Box>
                <Schedule color="warning" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Conexões Ativas
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="info.main">
                    {systemMetrics?.active_connections}
                  </Typography>
                </Box>
                <NetworkCheck color="info" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} mb={3}>
        {/* Gráfico de SMS por Hora */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SMS Enviados por Hora (Últimas 12h)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Area
                    type="monotone"
                    dataKey="sms_sent"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance do Sistema */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Sistema
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line
                    type="monotone"
                    dataKey="cpu_usage"
                    stroke="#ff7c7c"
                    strokeWidth={2}
                    name="CPU %"
                  />
                  <Line
                    type="monotone"
                    dataKey="memory_usage"
                    stroke="#82ca9d"
                    strokeWidth={2}
                    name="Memória %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Status dos Serviços */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Status dos Serviços
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Serviço</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Uptime</TableCell>
                  <TableCell>Tempo Resposta</TableCell>
                  <TableCell>Última Verificação</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {services.map((service) => (
                  <TableRow key={service.name}>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        {getStatusIcon(service.status)}
                        <Typography sx={{ ml: 1 }}>{service.name}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={service.status.toUpperCase()}
                        color={getStatusColor(service.status) as any}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{service.uptime.toFixed(1)}%</TableCell>
                    <TableCell>
                      {service.response_time > 0 ? `${service.response_time}ms` : '-'}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {service.last_check.toLocaleTimeString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Últimos Alertas */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Histórico de Alertas
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tipo</TableCell>
                  <TableCell>Título</TableCell>
                  <TableCell>Mensagem</TableCell>
                  <TableCell>Hora</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts.slice(0, 10).map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>
                      {getAlertIcon(alert.type)}
                    </TableCell>
                    <TableCell>
                      <Typography fontWeight="bold">{alert.title}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{alert.message}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {alert.timestamp.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={alert.resolved ? 'Resolvido' : 'Ativo'}
                        color={alert.resolved ? 'success' : 'error'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SystemMonitoringPage;
