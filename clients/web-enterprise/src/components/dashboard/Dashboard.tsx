// Dashboard Principal com Métricas e Widgets Integrados
// Dashboard completo com integração total às APIs do sistema

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/router';
import {
  useDashboardData,
  useRecentSMS,
  useRecentCampaigns,
  useSystemStatus,
  useContactStats,
  useSMSStats,
  useCampaignStats
} from '@/hooks/api-hooks';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import {
  Users,
  MessageSquare,
  Send,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Calendar,
  Phone,
  Mail,
  DollarSign,
  Activity,
  Zap,
  Eye,
  Plus,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  PieChart,
  Target,
  Filter
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { toast } from 'sonner';
import { formatDistance } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { PhoneFormatter, DateFormatter, NumberFormatter } from '@/shared/utils/formatters';

// ===== TIPOS =====

interface DashboardMetric {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease';
    period: string;
  };
  icon: React.ElementType;
  color: string;
  trend?: Array<{ date: string; value: number }>;
}

interface QuickAction {
  title: string;
  description: string;
  icon: React.ElementType;
  action: () => void;
  color: string;
}

// ===== COMPONENTES DE MÉTRICAS =====

function MetricCard({ metric }: { metric: DashboardMetric }) {
  const Icon = metric.icon;
  const hasIncrease = metric.change?.type === 'increase';

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 mb-1">
              {metric.title}
            </p>
            <p className="text-3xl font-bold text-gray-900 mb-2">
              {typeof metric.value === 'number' 
                ? NumberFormatter.formatNumber(metric.value)
                : metric.value
              }
            </p>
            
            {metric.change && (
              <div className="flex items-center space-x-1">
                {hasIncrease ? (
                  <ArrowUpRight className="h-4 w-4 text-green-600" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-red-600" />
                )}
                <span className={`text-sm font-medium ${
                  hasIncrease ? 'text-green-600' : 'text-red-600'
                }`}>
                  {metric.change.value}%
                </span>
                <span className="text-sm text-gray-500">
                  vs {metric.change.period}
                </span>
              </div>
            )}
          </div>
          
          <div className={`p-3 rounded-full bg-${metric.color}-100`}>
            <Icon className={`h-6 w-6 text-${metric.color}-600`} />
          </div>
        </div>

        {/* Mini gráfico de tendência */}
        {metric.trend && metric.trend.length > 0 && (
          <div className="mt-4 h-8">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metric.trend}>
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={`var(--${metric.color}-600)`}
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ===== WIDGET DE AÇÕES RÁPIDAS =====

function QuickActionsWidget() {
  const router = useRouter();

  const quickActions: QuickAction[] = [
    {
      title: 'Enviar SMS',
      description: 'Envie uma mensagem rapidamente',
      icon: MessageSquare,
      action: () => router.push('/sms/send'),
      color: 'blue'
    },
    {
      title: 'Novo Contato',
      description: 'Adicione um novo contato',
      icon: Users,
      action: () => router.push('/contacts/new'),
      color: 'green'
    },
    {
      title: 'Nova Campanha',
      description: 'Crie uma campanha de SMS',
      icon: Target,
      action: () => router.push('/campaigns/new'),
      color: 'purple'
    },
    {
      title: 'Novo Template',
      description: 'Crie um template reutilizável',
      icon: Mail,
      action: () => router.push('/templates/new'),
      color: 'orange'
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Zap className="h-5 w-5" />
          <span>Ações Rápidas</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Button
                key={index}
                variant="outline"
                className="h-auto p-4 flex flex-col items-center space-y-2 hover:shadow-md transition-shadow"
                onClick={action.action}
              >
                <div className={`p-2 rounded-full bg-${action.color}-100`}>
                  <Icon className={`h-5 w-5 text-${action.color}-600`} />
                </div>
                <div className="text-center">
                  <p className="font-medium text-sm">{action.title}</p>
                  <p className="text-xs text-gray-500">{action.description}</p>
                </div>
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// ===== WIDGET DE SMS RECENTES =====

function RecentSMSWidget() {
  const router = useRouter();
  const { data: recentSMS, isLoading } = useRecentSMS({ limit: 5 });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusLabel = (status: string) => {
    const labels = {
      sent: 'Enviado',
      failed: 'Falhou',
      pending: 'Pendente',
      delivered: 'Entregue'
    };
    return labels[status as keyof typeof labels] || status;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center space-x-2">
          <MessageSquare className="h-5 w-5" />
          <span>SMS Recentes</span>
        </CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={() => router.push('/sms/history')}
        >
          Ver Todos
          <ArrowUpRight className="h-4 w-4 ml-1" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="h-3 bg-gray-200 rounded w-2/3 animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        ) : recentSMS && recentSMS.length > 0 ? (
          <div className="space-y-4">
            {recentSMS.map((sms) => (
              <div key={sms.id} className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {getStatusIcon(sms.status)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {sms.recipient_name || PhoneFormatter.formatDisplay(sms.recipient_phone)}
                    </p>
                    <Badge variant="outline" className="text-xs">
                      {getStatusLabel(sms.status)}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-gray-600 truncate mt-1">
                    {sms.message.length > 50 
                      ? `${sms.message.substring(0, 50)}...`
                      : sms.message
                    }
                  </p>
                  
                  <p className="text-xs text-gray-500 mt-1">
                    {formatDistance(new Date(sms.created_at), new Date(), {
                      addSuffix: true,
                      locale: ptBR
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6">
            <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Nenhum SMS enviado ainda</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={() => router.push('/sms/send')}
            >
              Enviar Primeiro SMS
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ===== WIDGET DE CAMPANHAS ATIVAS =====

function ActiveCampaignsWidget() {
  const router = useRouter();
  const { data: campaigns, isLoading } = useRecentCampaigns({ 
    status: 'running',
    limit: 3 
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center space-x-2">
          <Target className="h-5 w-5" />
          <span>Campanhas Ativas</span>
        </CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={() => router.push('/campaigns')}
        >
          Ver Todas
          <ArrowUpRight className="h-4 w-4 ml-1" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="p-4 border rounded-lg">
                <div className="h-4 bg-gray-200 rounded animate-pulse mb-2" />
                <div className="h-3 bg-gray-200 rounded w-2/3 animate-pulse" />
              </div>
            ))}
          </div>
        ) : campaigns && campaigns.length > 0 ? (
          <div className="space-y-4">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="p-4 border rounded-lg hover:shadow-sm transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{campaign.name}</h4>
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    Ativa
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>{campaign.sent_count || 0} / {campaign.recipient_count || 0} enviados</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/campaigns/${campaign.id}`)}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
                
                {/* Barra de progresso */}
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{
                        width: `${
                          campaign.recipient_count 
                            ? (campaign.sent_count / campaign.recipient_count) * 100
                            : 0
                        }%`
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6">
            <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Nenhuma campanha ativa</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={() => router.push('/campaigns/new')}
            >
              Criar Campanha
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ===== GRÁFICO DE ENVIOS =====

function SMSChart() {
  const [period, setPeriod] = useState('7d');
  const { data: smsStats, isLoading } = useSMSStats({
    period: period as '24h' | '7d' | '30d' | '90d'
  });

  const chartData = useMemo(() => {
    if (!smsStats?.daily_stats) return [];
    
    return smsStats.daily_stats.map(stat => ({
      date: DateFormatter.formatShort(stat.date),
      enviados: stat.sent_count,
      falharam: stat.failed_count,
      total: stat.sent_count + stat.failed_count
    }));
  }, [smsStats]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center space-x-2">
          <BarChart3 className="h-5 w-5" />
          <span>Envios de SMS</span>
        </CardTitle>
        
        <Select value={period} onValueChange={setPeriod}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="24h">24 horas</SelectItem>
            <SelectItem value="7d">7 dias</SelectItem>
            <SelectItem value="30d">30 dias</SelectItem>
            <SelectItem value="90d">90 dias</SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      
      <CardContent>
        {isLoading ? (
          <div className="h-64 flex items-center justify-center">
            <RefreshCw className="h-8 w-8 animate-spin" />
          </div>
        ) : chartData.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="enviados" fill="#10b981" name="Enviados" />
                <Bar dataKey="falharam" fill="#ef4444" name="Falharam" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Sem dados para exibir</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ===== DASHBOARD PRINCIPAL =====

export function Dashboard() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);

  // Dados do dashboard
  const { 
    data: dashboardData, 
    isLoading: isDashboardLoading,
    refetch: refetchDashboard 
  } = useDashboardData();

  const { data: systemStatus } = useSystemStatus();

  // Métricas principais
  const metrics: DashboardMetric[] = useMemo(() => {
    if (!dashboardData) return [];

    return [
      {
        title: 'Total de Contatos',
        value: dashboardData.contacts.total,
        change: {
          value: dashboardData.contacts.growth_rate || 0,
          type: (dashboardData.contacts.growth_rate || 0) >= 0 ? 'increase' : 'decrease',
          period: 'mês anterior'
        },
        icon: Users,
        color: 'blue',
        trend: dashboardData.contacts.trend
      },
      {
        title: 'SMS Enviados',
        value: dashboardData.sms.total_sent,
        change: {
          value: dashboardData.sms.growth_rate || 0,
          type: (dashboardData.sms.growth_rate || 0) >= 0 ? 'increase' : 'decrease',
          period: 'mês anterior'
        },
        icon: MessageSquare,
        color: 'green',
        trend: dashboardData.sms.trend
      },
      {
        title: 'Taxa de Sucesso',
        value: `${dashboardData.sms.success_rate || 0}%`,
        change: {
          value: dashboardData.sms.success_rate_change || 0,
          type: (dashboardData.sms.success_rate_change || 0) >= 0 ? 'increase' : 'decrease',
          period: 'semana anterior'
        },
        icon: CheckCircle,
        color: 'purple'
      },
      {
        title: 'Campanhas Ativas',
        value: dashboardData.campaigns.active_count,
        icon: Target,
        color: 'orange'
      }
    ];
  }, [dashboardData]);

  // Função de refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refetchDashboard();
      toast.success('Dashboard atualizado com sucesso!');
    } catch (error) {
      toast.error('Erro ao atualizar dashboard');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Visão geral do sistema AMA MESSAGE
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {systemStatus && (
            <Badge 
              variant={systemStatus.status === 'healthy' ? 'default' : 'destructive'}
              className="flex items-center space-x-1"
            >
              <Activity className="h-3 w-3" />
              <span>
                {systemStatus.status === 'healthy' ? 'Sistema OK' : 'Sistema com Problemas'}
              </span>
            </Badge>
          )}
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Métricas Principais */}
      {isDashboardLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                  <div className="h-8 bg-gray-200 rounded w-2/3 mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-1/2" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <MetricCard key={index} metric={metric} />
          ))}
        </div>
      )}

      {/* Gráficos e Widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gráfico de SMS - ocupa 2 colunas */}
        <div className="lg:col-span-2">
          <SMSChart />
        </div>
        
        {/* Ações Rápidas */}
        <QuickActionsWidget />
      </div>

      {/* Widgets de Atividades */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentSMSWidget />
        <ActiveCampaignsWidget />
      </div>
    </div>
  );
}

export default Dashboard;
