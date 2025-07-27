// Sistema de Relatórios e Analytics Avançado
// Componentes para dashboards, gráficos e análises detalhadas

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/router';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
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
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/components/ui/tabs';
import { DateRange } from 'react-day-picker';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from '@/components/ui/popover';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  RadialBarChart,
  RadialBar
} from 'recharts';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Calendar as CalendarIcon,
  Download,
  RefreshCw,
  MessageSquare,
  Users,
  Target,
  DollarSign,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Filter,
  Eye,
  PieChart as PieChartIcon,
  Activity,
  Zap
} from 'lucide-react';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import {
  useSMSStats,
  useCampaignStats,
  useContactStats,
  useBillingStats,
  useSystemStats,
  useExportReport
} from '@/hooks/api-hooks';
import { NumberFormatter, DateFormatter } from '@/shared/utils/formatters';
import { toast } from 'sonner';

// ===== TIPOS =====

interface ReportFilters {
  dateRange: DateRange | undefined;
  period: '24h' | '7d' | '30d' | '90d' | 'custom';
  groupBy: 'hour' | 'day' | 'week' | 'month';
  campaignId?: number;
  contactId?: number;
  status?: string;
}

interface MetricCard {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease';
    period: string;
  };
  icon: React.ElementType;
  color: string;
  description?: string;
}

// ===== CORES PARA GRÁFICOS =====

const CHART_COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#8b5cf6',
  gray: '#6b7280'
};

const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

// ===== COMPONENTE DE FILTROS =====

function ReportFilters({ 
  filters, 
  onFiltersChange 
}: { 
  filters: ReportFilters;
  onFiltersChange: (filters: ReportFilters) => void;
}) {
  const [date, setDate] = useState<DateRange | undefined>(filters.dateRange);

  const handlePeriodChange = (period: string) => {
    const newFilters = { ...filters, period: period as any };
    
    // Definir datas baseadas no período
    const now = new Date();
    switch (period) {
      case '24h':
        newFilters.dateRange = {
          from: subDays(now, 1),
          to: now
        };
        newFilters.groupBy = 'hour';
        break;
      case '7d':
        newFilters.dateRange = {
          from: subDays(now, 7),
          to: now
        };
        newFilters.groupBy = 'day';
        break;
      case '30d':
        newFilters.dateRange = {
          from: subDays(now, 30),
          to: now
        };
        newFilters.groupBy = 'day';
        break;
      case '90d':
        newFilters.dateRange = {
          from: subDays(now, 90),
          to: now
        };
        newFilters.groupBy = 'week';
        break;
      case 'custom':
        // Manter o range atual ou definir mês atual
        if (!newFilters.dateRange) {
          newFilters.dateRange = {
            from: startOfMonth(now),
            to: endOfMonth(now)
          };
        }
        newFilters.groupBy = 'day';
        break;
    }

    onFiltersChange(newFilters);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Filter className="h-5 w-5" />
          <span>Filtros</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Período */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Período</label>
            <Select value={filters.period} onValueChange={handlePeriodChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">Últimas 24h</SelectItem>
                <SelectItem value="7d">Últimos 7 dias</SelectItem>
                <SelectItem value="30d">Últimos 30 dias</SelectItem>
                <SelectItem value="90d">Últimos 90 dias</SelectItem>
                <SelectItem value="custom">Personalizado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Data Personalizada */}
          {filters.period === 'custom' && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Data</label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date?.from ? (
                      date.to ? (
                        <>
                          {format(date.from, "dd/MM/yyyy")} -{" "}
                          {format(date.to, "dd/MM/yyyy")}
                        </>
                      ) : (
                        format(date.from, "dd/MM/yyyy")
                      )
                    ) : (
                      "Selecione as datas"
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={date?.from}
                    selected={date}
                    onSelect={(newDate) => {
                      setDate(newDate);
                      onFiltersChange({ ...filters, dateRange: newDate });
                    }}
                    numberOfMonths={2}
                    locale={ptBR}
                  />
                </PopoverContent>
              </Popover>
            </div>
          )}

          {/* Agrupamento */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Agrupar por</label>
            <Select 
              value={filters.groupBy} 
              onValueChange={(value) => 
                onFiltersChange({ ...filters, groupBy: value as any })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="hour">Hora</SelectItem>
                <SelectItem value="day">Dia</SelectItem>
                <SelectItem value="week">Semana</SelectItem>
                <SelectItem value="month">Mês</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Exportar */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Ações</label>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" className="flex-1">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ===== COMPONENTE DE CARD DE MÉTRICA =====

function MetricCardComponent({ metric }: { metric: MetricCard }) {
  const Icon = metric.icon;
  const hasChange = metric.change !== undefined;
  const isIncrease = metric.change?.type === 'increase';

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
            
            {hasChange && (
              <div className="flex items-center space-x-1">
                {isIncrease ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                )}
                <span className={`text-sm font-medium ${
                  isIncrease ? 'text-green-600' : 'text-red-600'
                }`}>
                  {metric.change!.value > 0 ? '+' : ''}{metric.change!.value}%
                </span>
                <span className="text-sm text-gray-500">
                  vs {metric.change!.period}
                </span>
              </div>
            )}

            {metric.description && (
              <p className="text-xs text-gray-500 mt-1">
                {metric.description}
              </p>
            )}
          </div>
          
          <div className={`p-3 rounded-full bg-${metric.color}-100`}>
            <Icon className={`h-6 w-6 text-${metric.color}-600`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ===== RELATÓRIO DE SMS =====

export function SMSReport() {
  const [filters, setFilters] = useState<ReportFilters>({
    dateRange: {
      from: subDays(new Date(), 30),
      to: new Date()
    },
    period: '30d',
    groupBy: 'day'
  });

  const { data: smsStats, isLoading } = useSMSStats({
    period: filters.period,
    group_by: filters.groupBy
  });

  const metrics: MetricCard[] = useMemo(() => {
    if (!smsStats) return [];

    return [
      {
        title: 'Total Enviados',
        value: smsStats.total_sent || 0,
        change: {
          value: smsStats.sent_growth_rate || 0,
          type: (smsStats.sent_growth_rate || 0) >= 0 ? 'increase' : 'decrease',
          period: 'período anterior'
        },
        icon: MessageSquare,
        color: 'blue',
        description: 'SMS enviados no período'
      },
      {
        title: 'Taxa de Sucesso',
        value: `${smsStats.success_rate || 0}%`,
        change: {
          value: smsStats.success_rate_change || 0,
          type: (smsStats.success_rate_change || 0) >= 0 ? 'increase' : 'decrease',
          period: 'período anterior'
        },
        icon: CheckCircle,
        color: 'green',
        description: 'Mensagens entregues com sucesso'
      },
      {
        title: 'Falhas',
        value: smsStats.total_failed || 0,
        change: {
          value: smsStats.failed_growth_rate || 0,
          type: (smsStats.failed_growth_rate || 0) <= 0 ? 'increase' : 'decrease',
          period: 'período anterior'
        },
        icon: XCircle,
        color: 'red',
        description: 'Mensagens que falharam'
      },
      {
        title: 'Custo Total',
        value: NumberFormatter.formatCurrency(smsStats.total_cost || 0),
        change: {
          value: smsStats.cost_growth_rate || 0,
          type: (smsStats.cost_growth_rate || 0) >= 0 ? 'increase' : 'decrease',
          period: 'período anterior'
        },
        icon: DollarSign,
        color: 'purple',
        description: 'Gasto total em SMS'
      }
    ];
  }, [smsStats]);

  const chartData = useMemo(() => {
    if (!smsStats?.daily_stats) return [];
    
    return smsStats.daily_stats.map(stat => ({
      date: DateFormatter.formatShort(stat.date),
      enviados: stat.sent_count,
      entregues: stat.delivered_count,
      falharam: stat.failed_count,
      custo: stat.cost
    }));
  }, [smsStats]);

  const statusData = useMemo(() => {
    if (!smsStats) return [];

    return [
      { name: 'Entregues', value: smsStats.delivered_count || 0, color: CHART_COLORS.success },
      { name: 'Pendentes', value: smsStats.pending_count || 0, color: CHART_COLORS.warning },
      { name: 'Falharam', value: smsStats.failed_count || 0, color: CHART_COLORS.danger }
    ];
  }, [smsStats]);

  return (
    <div className="space-y-6">
      {/* Filtros */}
      <ReportFilters filters={filters} onFiltersChange={setFilters} />

      {/* Métricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <MetricCardComponent key={index} metric={metric} />
        ))}
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Linha - Envios ao Longo do Tempo */}
        <Card>
          <CardHeader>
            <CardTitle>Envios ao Longo do Tempo</CardTitle>
            <CardDescription>
              Análise temporal dos envios de SMS
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="enviados"
                    stroke={CHART_COLORS.primary}
                    name="Enviados"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="entregues"
                    stroke={CHART_COLORS.success}
                    name="Entregues"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="falharam"
                    stroke={CHART_COLORS.danger}
                    name="Falharam"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Gráfico de Pizza - Status dos SMS */}
        <Card>
          <CardHeader>
            <CardTitle>Status dos SMS</CardTitle>
            <CardDescription>
              Distribuição por status de entrega
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de Área - Custo */}
      <Card>
        <CardHeader>
          <CardTitle>Análise de Custos</CardTitle>
          <CardDescription>
            Evolução dos custos com SMS ao longo do tempo
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip
                  formatter={(value) => [
                    NumberFormatter.formatCurrency(Number(value)),
                    'Custo'
                  ]}
                />
                <Area
                  type="monotone"
                  dataKey="custo"
                  stroke={CHART_COLORS.info}
                  fill={CHART_COLORS.info}
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ===== RELATÓRIO DE CAMPANHAS =====

export function CampaignReport() {
  const [filters, setFilters] = useState<ReportFilters>({
    dateRange: {
      from: subDays(new Date(), 30),
      to: new Date()
    },
    period: '30d',
    groupBy: 'day'
  });

  const { data: campaignStats, isLoading } = useCampaignStats({
    period: filters.period
  });

  const metrics: MetricCard[] = useMemo(() => {
    if (!campaignStats) return [];

    return [
      {
        title: 'Campanhas Ativas',
        value: campaignStats.active_count || 0,
        icon: Target,
        color: 'blue',
        description: 'Campanhas em execução'
      },
      {
        title: 'Taxa de Conversão',
        value: `${campaignStats.conversion_rate || 0}%`,
        change: {
          value: campaignStats.conversion_rate_change || 0,
          type: (campaignStats.conversion_rate_change || 0) >= 0 ? 'increase' : 'decrease',
          period: 'período anterior'
        },
        icon: TrendingUp,
        color: 'green',
        description: 'Efetividade das campanhas'
      },
      {
        title: 'ROI Médio',
        value: `${campaignStats.avg_roi || 0}%`,
        change: {
          value: campaignStats.roi_change || 0,
          type: (campaignStats.roi_change || 0) >= 0 ? 'increase' : 'decrease',
          period: 'período anterior'
        },
        icon: DollarSign,
        color: 'green',
        description: 'Retorno sobre investimento'
      },
      {
        title: 'Alcance Total',
        value: campaignStats.total_reach || 0,
        change: {
          value: campaignStats.reach_growth_rate || 0,
          type: (campaignStats.reach_growth_rate || 0) >= 0 ? 'increase' : 'decrease',
          period: 'período anterior'
        },
        icon: Users,
        color: 'purple',
        description: 'Contatos alcançados'
      }
    ];
  }, [campaignStats]);

  const performanceData = useMemo(() => {
    if (!campaignStats?.campaign_performance) return [];
    
    return campaignStats.campaign_performance.map(campaign => ({
      name: campaign.name.length > 15 
        ? `${campaign.name.substring(0, 15)}...` 
        : campaign.name,
      enviados: campaign.sent_count,
      entregues: campaign.delivered_count,
      conversoes: campaign.conversion_count,
      roi: campaign.roi
    }));
  }, [campaignStats]);

  return (
    <div className="space-y-6">
      {/* Filtros */}
      <ReportFilters filters={filters} onFiltersChange={setFilters} />

      {/* Métricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <MetricCardComponent key={index} metric={metric} />
        ))}
      </div>

      {/* Performance das Campanhas */}
      <Card>
        <CardHeader>
          <CardTitle>Performance das Campanhas</CardTitle>
          <CardDescription>
            Comparação de resultados entre campanhas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} />
                <Tooltip />
                <Legend />
                <Bar dataKey="enviados" fill={CHART_COLORS.primary} name="Enviados" />
                <Bar dataKey="entregues" fill={CHART_COLORS.success} name="Entregues" />
                <Bar dataKey="conversoes" fill={CHART_COLORS.warning} name="Conversões" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* ROI por Campanha */}
      <Card>
        <CardHeader>
          <CardTitle>ROI por Campanha</CardTitle>
          <CardDescription>
            Retorno sobre investimento de cada campanha
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart cx="50%" cy="50%" innerRadius="10%" outerRadius="80%" data={performanceData.slice(0, 5)}>
                <RadialBar dataKey="roi" cornerRadius={10} fill={CHART_COLORS.success} />
                <Tooltip formatter={(value) => [`${value}%`, 'ROI']} />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ===== PÁGINA PRINCIPAL DE RELATÓRIOS =====

export function ReportsPage() {
  const [activeTab, setActiveTab] = useState('sms');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
          <p className="text-gray-600">
            Análises detalhadas e insights do seu sistema
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Exportar Dados
          </Button>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Tabs de Relatórios */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="sms" className="flex items-center space-x-2">
            <MessageSquare className="h-4 w-4" />
            <span>SMS</span>
          </TabsTrigger>
          <TabsTrigger value="campaigns" className="flex items-center space-x-2">
            <Target className="h-4 w-4" />
            <span>Campanhas</span>
          </TabsTrigger>
          <TabsTrigger value="contacts" className="flex items-center space-x-2">
            <Users className="h-4 w-4" />
            <span>Contatos</span>
          </TabsTrigger>
          <TabsTrigger value="billing" className="flex items-center space-x-2">
            <DollarSign className="h-4 w-4" />
            <span>Faturamento</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sms" className="mt-6">
          <SMSReport />
        </TabsContent>

        <TabsContent value="campaigns" className="mt-6">
          <CampaignReport />
        </TabsContent>

        <TabsContent value="contacts" className="mt-6">
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Relatório de Contatos
            </h3>
            <p className="text-gray-600">
              Em desenvolvimento...
            </p>
          </div>
        </TabsContent>

        <TabsContent value="billing" className="mt-6">
          <div className="text-center py-12">
            <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Relatório de Faturamento
            </h3>
            <p className="text-gray-600">
              Em desenvolvimento...
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export {
  ReportFilters,
  MetricCardComponent,
  SMSReport,
  CampaignReport,
  ReportsPage
};
