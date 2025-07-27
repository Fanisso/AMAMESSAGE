import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Button,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Refresh,
  Warning,
  CheckCircle,
  Error,
  Info,
  TrendingUp,
  TrendingDown,
  People,
  Sms,
  Router,
  Storage,
} from '@mui/icons-material';

// Interface para métricas do sistema
interface SystemMetrics {
  system_health: 'healthy' | 'degraded' | 'unhealthy';
  total_users: number;
  active_users: number;
  messages_today: number;
  messages_success_rate: number;
  ussd_sessions_today: number;
  connected_modems: number;
  total_modems: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  uptime_seconds: number;
}

// Componente de métrica individual
const MetricCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
}> = ({ title, value, subtitle, icon, color, trend, trendValue }) => {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Box color={`${color}.main`}>
            {icon}
          </Box>
          {trend && (
            <Box display="flex" alignItems="center" gap={0.5}>
              {trend === 'up' && <TrendingUp color="success" fontSize="small" />}
              {trend === 'down' && <TrendingDown color="error" fontSize="small" />}
              <Typography variant="caption" color={trend === 'up' ? 'success.main' : 'error.main'}>
                {trendValue}
              </Typography>
            </Box>
          )}
        </Box>
        
        <Typography variant="h4" fontWeight="bold" color="text.primary">
          {value}
        </Typography>
        
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

// Componente de status do sistema
const SystemHealthCard: React.FC<{ health: string }> = ({ health }) => {
  const getHealthConfig = (status: string) => {
    switch (status) {
      case 'healthy':
        return {
          icon: <CheckCircle />,
          color: 'success' as const,
          text: 'Sistema Saudável',
          description: 'Todos os serviços funcionando normalmente'
        };
      case 'degraded':
        return {
          icon: <Warning />,
          color: 'warning' as const,
          text: 'Sistema Degradado',
          description: 'Alguns serviços com problemas'
        };
      case 'unhealthy':
        return {
          icon: <Error />,
          color: 'error' as const,
          text: 'Sistema com Problemas',
          description: 'Atenção necessária imediatamente'
        };
      default:
        return {
          icon: <Info />,
          color: 'info' as const,
          text: 'Status Desconhecido',
          description: 'Verificando estado do sistema...'
        };
    }
  };

  const config = getHealthConfig(health);

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Box color={`${config.color}.main`} fontSize="2rem">
            {config.icon}
          </Box>
          <Box>
            <Typography variant="h5" fontWeight="bold">
              {config.text}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {config.description}
            </Typography>
          </Box>
        </Box>
        
        <Chip 
          label={health.toUpperCase()} 
          color={config.color} 
          variant="outlined" 
          size="small"
        />
      </CardContent>
    </Card>
  );
};

// Componente de barra de progresso com label
const ProgressCard: React.FC<{
  title: string;
  value: number;
  max?: number;
  unit?: string;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}> = ({ title, value, max = 100, unit = '%', color = 'primary' }) => {
  const percentage = (value / max) * 100;
  
  const getColorByValue = (val: number) => {
    if (val < 50) return 'success';
    if (val < 80) return 'warning';
    return 'error';
  };

  const barColor = color === 'primary' ? getColorByValue(percentage) : color;

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h6">{title}</Typography>
          <Typography variant="h6" fontWeight="bold">
            {value}{unit}
          </Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={percentage} 
          color={barColor}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </CardContent>
    </Card>
  );
};

const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Simular dados (substituir por chamada real à API)
  const fetchMetrics = async () => {
    setLoading(true);
    
    // Simular delay de rede
    setTimeout(() => {
      const mockMetrics: SystemMetrics = {
        system_health: Math.random() > 0.8 ? 'degraded' : 'healthy',
        total_users: 1247,
        active_users: 89,
        messages_today: 5423,
        messages_success_rate: 98.2,
        ussd_sessions_today: 234,
        connected_modems: 3,
        total_modems: 4,
        cpu_usage: Math.floor(Math.random() * 80) + 10,
        memory_usage: Math.floor(Math.random() * 70) + 20,
        disk_usage: Math.floor(Math.random() * 60) + 30,
        uptime_seconds: 2847392, // 33 dias
      };
      
      setMetrics(mockMetrics);
      setLastUpdate(new Date());
      setLoading(false);
    }, 800);
  };

  useEffect(() => {
    fetchMetrics();
    
    // Atualizar a cada 30 segundos
    const interval = setInterval(fetchMetrics, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    return `${days}d ${hours}h`;
  };

  if (loading && !metrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Box textAlign="center">
          <LinearProgress sx={{ mb: 2, width: 200 }} />
          <Typography>Carregando métricas do sistema...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Dashboard Administrativo
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Visão geral completa do sistema AMA MESSAGE
          </Typography>
        </Box>
        
        <Box display="flex" gap={1} alignItems="center">
          <Typography variant="caption" color="text.secondary">
            Última atualização: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <IconButton onClick={fetchMetrics} disabled={loading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Alertas importantes */}
      {metrics?.system_health !== 'healthy' && (
        <Alert 
          severity={metrics?.system_health === 'degraded' ? 'warning' : 'error'} 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small">
              Ver Detalhes
            </Button>
          }
        >
          <strong>Atenção:</strong> Sistema com problemas detectados. Verificação necessária.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Status do Sistema */}
        <Grid item xs={12} md={6} lg={4}>
          <SystemHealthCard health={metrics?.system_health || 'unknown'} />
        </Grid>

        {/* Métricas principais */}
        <Grid item xs={12} sm={6} md={3} lg={2}>
          <MetricCard
            title="Utilizadores Totais"
            value={metrics?.total_users || 0}
            subtitle={`${metrics?.active_users || 0} ativos hoje`}
            icon={<People fontSize="large" />}
            color="primary"
            trend="up"
            trendValue="+12%"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3} lg={2}>
          <MetricCard
            title="SMS Hoje"
            value={metrics?.messages_today || 0}
            subtitle={`${metrics?.messages_success_rate || 0}% sucesso`}
            icon={<Sms fontSize="large" />}
            color="success"
            trend="up"
            trendValue="+8%"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3} lg={2}>
          <MetricCard
            title="USSD Hoje"
            value={metrics?.ussd_sessions_today || 0}
            subtitle="sessões ativas"
            icon={<Router fontSize="large" />}
            color="info"
            trend="stable"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3} lg={2}>
          <MetricCard
            title="Modems"
            value={`${metrics?.connected_modems || 0}/${metrics?.total_modems || 0}`}
            subtitle="conectados"
            icon={<Router fontSize="large" />}
            color={metrics?.connected_modems === metrics?.total_modems ? 'success' : 'warning'}
          />
        </Grid>

        {/* Uso de recursos */}
        <Grid item xs={12} md={4}>
          <ProgressCard
            title="CPU"
            value={metrics?.cpu_usage || 0}
          />
        </Grid>

        <Grid item xs={12} md={4}>
          <ProgressCard
            title="Memória"
            value={metrics?.memory_usage || 0}
          />
        </Grid>

        <Grid item xs={12} md={4}>
          <ProgressCard
            title="Disco"
            value={metrics?.disk_usage || 0}
          />
        </Grid>

        {/* Uptime */}
        <Grid item xs={12} md={6}>
          <MetricCard
            title="Uptime do Sistema"
            value={formatUptime(metrics?.uptime_seconds || 0)}
            subtitle="sem interrupções"
            icon={<Storage fontSize="large" />}
            color="success"
          />
        </Grid>

        {/* Ações rápidas */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ações Rápidas
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Button variant="outlined" color="warning" size="small">
                  Reiniciar Modems
                </Button>
                <Button variant="outlined" color="info" size="small">
                  Ver Logs Críticos
                </Button>
                <Button variant="outlined" color="error" size="small">
                  Backup de Emergência
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
