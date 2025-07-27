import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Fab,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Sms,
  Group,
  Schedule,
  Analytics,
  Send,
  Campaign,
  Assignment,
  Notifications,
  MoreVert,
  Add,
  FilterList,
  Download,
  Refresh,
  Business,
  Phone,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Dados simulados para dashboard empresarial
const mockDashboardData = {
  metrics: {
    sms_sent_today: 1247,
    sms_sent_yesterday: 1089,
    success_rate: 98.2,
    active_campaigns: 5,
    team_members: 12,
    pending_approvals: 3,
    monthly_budget: 25000,
    budget_used: 18500,
  },
  hourlyData: [
    { time: '00:00', sent: 23, delivered: 22, failed: 1 },
    { time: '01:00', sent: 15, delivered: 14, failed: 1 },
    { time: '02:00', sent: 8, delivered: 8, failed: 0 },
    { time: '03:00', sent: 12, delivered: 11, failed: 1 },
    { time: '04:00', sent: 18, delivered: 17, failed: 1 },
    { time: '05:00', sent: 45, delivered: 44, failed: 1 },
    { time: '06:00', sent: 89, delivered: 87, failed: 2 },
    { time: '07:00', sent: 156, delivered: 152, failed: 4 },
    { time: '08:00', sent: 234, delivered: 229, failed: 5 },
    { time: '09:00', sent: 189, delivered: 186, failed: 3 },
    { time: '10:00', sent: 267, delivered: 262, failed: 5 },
    { time: '11:00', sent: 298, delivered: 293, failed: 5 },
  ],
  campaignTypes: [
    { name: 'Promocional', value: 45, color: '#3b82f6' },
    { name: 'Informativo', value: 30, color: '#10b981' },
    { name: 'Transacional', value: 20, color: '#f59e0b' },
    { name: 'Suporte', value: 5, color: '#ef4444' },
  ],
  recentCampaigns: [
    {
      id: 1,
      name: 'Promoção Fim de Semana',
      status: 'active',
      sent: 850,
      delivered: 832,
      budget: 5000,
      created_by: 'Maria Silva',
      created_at: new Date(Date.now() - 3600000),
    },
    {
      id: 2,
      name: 'Lembrete de Pagamento',
      status: 'completed',
      sent: 1200,
      delivered: 1178,
      budget: 3500,
      created_by: 'João Santos',
      created_at: new Date(Date.now() - 7200000),
    },
    {
      id: 3,
      name: 'Novo Produto - Lançamento',
      status: 'scheduled',
      sent: 0,
      delivered: 0,
      budget: 8000,
      created_by: 'Ana Costa',
      created_at: new Date(Date.now() - 1800000),
    },
  ],
  teamActivity: [
    {
      user: 'Maria Silva',
      avatar: 'MS',
      action: 'Criou campanha "Promoção Fim de Semana"',
      time: '2 horas atrás',
      type: 'campaign',
    },
    {
      user: 'João Santos',
      avatar: 'JS',
      action: 'Aprovou template "Lembrete de Pagamento"',
      time: '3 horas atrás',
      type: 'approval',
    },
    {
      user: 'Ana Costa',
      avatar: 'AC',
      action: 'Agendou campanha para amanhã às 09:00',
      time: '4 horas atrás',
      type: 'schedule',
    },
    {
      user: 'Carlos Mendes',
      avatar: 'CM',
      action: 'Adicionou 500 novos contactos',
      time: '5 horas atrás',
      type: 'contacts',
    },
  ],
};

const EnterpriseDashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(mockDashboardData);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setData(mockDashboardData);
      setLoading(false);
    }, 1000);
  }, []);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'info';
      case 'scheduled': return 'warning';
      case 'paused': return 'default';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Ativa';
      case 'completed': return 'Concluída';
      case 'scheduled': return 'Agendada';
      case 'paused': return 'Pausada';
      default: return status;
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'campaign': return <Campaign sx={{ color: 'primary.main' }} />;
      case 'approval': return <Assignment sx={{ color: 'success.main' }} />;
      case 'schedule': return <Schedule sx={{ color: 'warning.main' }} />;
      case 'contacts': return <Group sx={{ color: 'info.main' }} />;
      default: return <Notifications />;
    }
  };

  const successRate = (data.metrics.sms_sent_today > 0) 
    ? (data.metrics.success_rate)
    : 0;

  const budgetUsedPercentage = (data.metrics.budget_used / data.metrics.monthly_budget) * 100;

  const growthRate = data.metrics.sms_sent_yesterday > 0 
    ? ((data.metrics.sms_sent_today - data.metrics.sms_sent_yesterday) / data.metrics.sms_sent_yesterday) * 100
    : 0;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="60vh">
        <Typography>Carregando dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Dashboard Empresarial
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Visão geral das operações de SMS e campanhas de marketing
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<Analytics />}>
            Relatórios
          </Button>
          <Button variant="contained" startIcon={<Campaign />}>
            Nova Campanha
          </Button>
        </Box>
      </Box>

      {/* Alertas de Aprovação */}
      {data.metrics.pending_approvals > 0 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Tem {data.metrics.pending_approvals} campanhas pendentes de aprovação.{' '}
          <Button size="small" color="inherit">
            Ver Pendências
          </Button>
        </Alert>
      )}

      {/* Métricas Principais */}
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
                    {data.metrics.sms_sent_today.toLocaleString()}
                  </Typography>
                  <Box display="flex" alignItems="center" mt={1}>
                    {growthRate >= 0 ? (
                      <TrendingUp sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                    ) : (
                      <TrendingDown sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }} />
                    )}
                    <Typography
                      variant="caption"
                      color={growthRate >= 0 ? 'success.main' : 'error.main'}
                    >
                      {Math.abs(growthRate).toFixed(1)}% vs ontem
                    </Typography>
                  </Box>
                </Box>
                <Sms sx={{ fontSize: 40, color: 'primary.main', opacity: 0.8 }} />
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
                    {successRate.toFixed(1)}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={successRate}
                    sx={{ mt: 1, height: 6, borderRadius: 3 }}
                    color="success"
                  />
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: 'success.main', opacity: 0.8 }} />
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
                    Campanhas Ativas
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="warning.main">
                    {data.metrics.active_campaigns}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {data.metrics.team_members} membros da equipe
                  </Typography>
                </Box>
                <Campaign sx={{ fontSize: 40, color: 'warning.main', opacity: 0.8 }} />
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
                    Orçamento Mensal
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="info.main">
                    {budgetUsedPercentage.toFixed(0)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {data.metrics.budget_used.toLocaleString()} MT de {data.metrics.monthly_budget.toLocaleString()} MT
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={budgetUsedPercentage}
                    sx={{ mt: 1, height: 6, borderRadius: 3 }}
                    color={budgetUsedPercentage > 90 ? 'error' : budgetUsedPercentage > 75 ? 'warning' : 'info'}
                  />
                </Box>
                <Business sx={{ fontSize: 40, color: 'info.main', opacity: 0.8 }} />
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
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" fontWeight="bold">
                  Envios por Hora (Hoje)
                </Typography>
                <IconButton onClick={handleMenuOpen}>
                  <MoreVert />
                </IconButton>
                <Menu
                  anchorEl={menuAnchor}
                  open={Boolean(menuAnchor)}
                  onClose={handleMenuClose}
                >
                  <MenuItem onClick={handleMenuClose}>
                    <Download sx={{ mr: 1 }} />
                    Exportar Dados
                  </MenuItem>
                  <MenuItem onClick={handleMenuClose}>
                    <Refresh sx={{ mr: 1 }} />
                    Atualizar
                  </MenuItem>
                </Menu>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data.hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="sent"
                    stackId="1"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.6}
                    name="Enviados"
                  />
                  <Area
                    type="monotone"
                    dataKey="delivered"
                    stackId="2"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.6}
                    name="Entregues"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Distribuição por Tipo de Campanha */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Tipos de Campanha
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={data.campaignTypes}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {data.campaignTypes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Campanhas Recentes */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" fontWeight="bold">
                  Campanhas Recentes
                </Typography>
                <Button size="small" startIcon={<Add />}>
                  Nova Campanha
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Campanha</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Enviados</TableCell>
                      <TableCell align="right">Taxa Entrega</TableCell>
                      <TableCell>Criado por</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.recentCampaigns.map((campaign) => (
                      <TableRow key={campaign.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {campaign.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Orçamento: {campaign.budget.toLocaleString()} MT
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={getStatusLabel(campaign.status)}
                            color={getStatusColor(campaign.status) as any}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold">
                            {campaign.sent.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            variant="body2"
                            color={campaign.sent > 0 && (campaign.delivered / campaign.sent) > 0.95 ? 'success.main' : 'text.primary'}
                          >
                            {campaign.sent > 0 ? ((campaign.delivered / campaign.sent) * 100).toFixed(1) : '0'}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Avatar sx={{ width: 32, height: 32, mr: 1, fontSize: '0.75rem' }}>
                              {campaign.created_by.split(' ').map(n => n[0]).join('')}
                            </Avatar>
                            <Box>
                              <Typography variant="body2">
                                {campaign.created_by}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {campaign.created_at.toLocaleTimeString('pt-PT', { 
                                  hour: '2-digit', 
                                  minute: '2-digit' 
                                })}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Atividade da Equipe */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Atividade da Equipe
              </Typography>
              <Box>
                {data.teamActivity.map((activity, index) => (
                  <Box key={index} display="flex" alignItems="center" mb={2}>
                    <Box sx={{ mr: 2 }}>
                      {getActivityIcon(activity.type)}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2">
                        <strong>{activity.user}</strong> {activity.action}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {activity.time}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
              <Button fullWidth variant="outlined" size="small" sx={{ mt: 2 }}>
                Ver Toda Atividade
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Fab para ações rápidas */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => {}}
      >
        <Send />
      </Fab>
    </Box>
  );
};

export default EnterpriseDashboardPage;
