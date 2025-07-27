// Exemplo de Integração Completa do Sistema
// Demonstra como usar todos os componentes e hooks juntos

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { GetServerSideProps } from 'next';

// Hooks personalizados
import { useAuth, useRequireAuth } from '@/hooks/useAuth';
import { useSystemConfig } from '@/config/AppConfig';
import { useNotificationSystem, showToast } from '@/components/notifications/NotificationSystem';

// Hooks de API
import {
  useDashboardData,
  useRecentSMS,
  useSystemStatus,
  useSendSMS,
  useContacts,
  useCampaigns
} from '@/hooks/api-hooks';

// Componentes de interface
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Componentes do sistema
import { Dashboard } from '@/components/dashboard/Dashboard';
import { ContactsList } from '@/components/lists/ListComponents';
import { CreateContactPage } from '@/pages/forms/FormPages';
import { SMSReport } from '@/components/reports/ReportsSystem';
import { NotificationPanel } from '@/components/notifications/NotificationSystem';

// Componentes de formulário
import { ContactForm } from '@/components/forms/ContactForm';
import { SMSForm } from '@/components/forms/SMSForm';

// Validação e formatação
import { useZodForm } from '@/shared/hooks/useZodValidation';
import { contactCreateSchema } from '@/shared/schemas/zod-schemas';
import { PhoneFormatter, DateFormatter } from '@/shared/utils/formatters';

// Ícones
import {
  Users,
  MessageSquare,
  Target,
  BarChart3,
  Plus,
  Send,
  RefreshCw,
  Settings,
  Bell,
  Activity,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

// ===== PÁGINA PRINCIPAL DE EXEMPLO =====

export default function ExampleIntegrationPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(false);

  // ===== HOOKS DO SISTEMA =====
  
  // Autenticação
  const { user, isAuthenticated, hasPermission } = useAuth();
  useRequireAuth(); // Garantir que está autenticado

  // Configurações
  const { config, isFeatureEnabled } = useSystemConfig();

  // Notificações
  const { showNotification, unreadCount } = useNotificationSystem();

  // ===== HOOKS DE DADOS =====
  
  // Dashboard
  const { 
    data: dashboardData, 
    isLoading: isDashboardLoading,
    refetch: refetchDashboard 
  } = useDashboardData();

  // SMS recentes
  const { data: recentSMS } = useRecentSMS({ limit: 5 });

  // Status do sistema
  const { data: systemStatus } = useSystemStatus();

  // Contatos
  const { 
    data: contactsData,
    isLoading: isContactsLoading 
  } = useContacts({ per_page: 10 });

  // Campanhas
  const { data: campaignsData } = useCampaigns({ per_page: 5 });

  // ===== MUTATIONS =====
  
  const sendSMSMutation = useSendSMS();

  // ===== FORMULÁRIO DE EXEMPLO =====
  
  const contactForm = useZodForm({
    schema: contactCreateSchema,
    defaultValues: {
      name: '',
      phone: '',
      email: '',
      tags: []
    }
  });

  // ===== FUNÇÕES DE EXEMPLO =====

  const handleSendTestSMS = async () => {
    if (!user?.phone) {
      showToast.warning('Adicione um telefone ao seu perfil para testar');
      return;
    }

    setIsLoading(true);
    try {
      await sendSMSMutation.mutateAsync({
        recipient_phone: user.phone,
        message: `Olá ${user.name}! Este é um SMS de teste do AMA MESSAGE.`,
        sender_name: 'Sistema'
      });

      showNotification({
        title: 'SMS de Teste Enviado',
        message: 'Verifique seu telefone para confirmar o recebimento',
        type: 'success',
        category: 'sms',
        priority: 'medium'
      });

    } catch (error) {
      showToast.error('Erro ao enviar SMS de teste');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSampleContact = async () => {
    try {
      const sampleData = {
        name: 'Contato de Exemplo',
        phone: '+258847654321',
        email: 'exemplo@email.com',
        tags: ['exemplo', 'teste']
      };

      // Simular criação
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      showToast.success('Contato de exemplo criado com sucesso!');
      
      // Refresh dos dados
      refetchDashboard();
      
    } catch (error) {
      showToast.error('Erro ao criar contato de exemplo');
    }
  };

  const handleShowNotificationExamples = () => {
    // Exemplo de diferentes tipos de notificação
    setTimeout(() => showToast.success('Operação realizada com sucesso!'), 500);
    setTimeout(() => showToast.info('Nova funcionalidade disponível'), 1500);
    setTimeout(() => showToast.warning('Atenção: limite de SMS próximo'), 2500);
    setTimeout(() => showToast.error('Erro de conexão detectado'), 3500);
  };

  // ===== DADOS PROCESSADOS =====

  const stats = {
    totalContacts: contactsData?.pagination?.total || 0,
    totalSMS: dashboardData?.sms?.total_sent || 0,
    activeCampaigns: dashboardData?.campaigns?.active_count || 0,
    successRate: dashboardData?.sms?.success_rate || 0
  };

  // ===== RENDERIZAÇÃO =====

  return (
    <div className="space-y-6 p-6">
      {/* Header com informações do usuário */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Integração Completa - {config.app.name}
          </h1>
          <p className="text-gray-600">
            Bem-vindo, {user?.name}! Sistema rodando na versão {config.app.version}
          </p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Status do Sistema */}
          <Badge 
            variant={systemStatus?.status === 'healthy' ? 'default' : 'destructive'}
            className="flex items-center space-x-1"
          >
            <Activity className="h-3 w-3" />
            <span>
              {systemStatus?.status === 'healthy' ? 'Online' : 'Offline'}
            </span>
          </Badge>

          {/* Notificações */}
          <NotificationPanel />

          {/* Refresh geral */}
          <Button 
            variant="outline" 
            onClick={() => {
              refetchDashboard();
              showToast.success('Dados atualizados!');
            }}
            disabled={isDashboardLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isDashboardLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Cards de estatísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Contatos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalContacts}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">SMS Enviados</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalSMS}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Campanhas Ativas</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeCampaigns}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.successRate}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Ações de demonstração */}
      <Card>
        <CardHeader>
          <CardTitle>Demonstrações do Sistema</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              onClick={handleSendTestSMS}
              disabled={isLoading || sendSMSMutation.isPending}
              className="h-16 flex flex-col items-center space-y-2"
            >
              <Send className="h-5 w-5" />
              <span>Enviar SMS Teste</span>
            </Button>

            <Button 
              variant="outline"
              onClick={handleCreateSampleContact}
              className="h-16 flex flex-col items-center space-y-2"
            >
              <Plus className="h-5 w-5" />
              <span>Criar Contato Exemplo</span>
            </Button>

            <Button 
              variant="outline"
              onClick={handleShowNotificationExamples}
              className="h-16 flex flex-col items-center space-y-2"
            >
              <Bell className="h-5 w-5" />
              <span>Mostrar Notificações</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabs com diferentes seções */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="contacts">Contatos</TabsTrigger>
          <TabsTrigger value="forms">Formulários</TabsTrigger>
          <TabsTrigger value="reports">Relatórios</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="mt-6">
          <Dashboard />
        </TabsContent>

        <TabsContent value="contacts" className="mt-6">
          <ContactsList />
        </TabsContent>

        <TabsContent value="forms" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Formulário de Contato */}
            <Card>
              <CardHeader>
                <CardTitle>Exemplo - Formulário de Contato</CardTitle>
              </CardHeader>
              <CardContent>
                <ContactForm
                  mode="create"
                  onSubmit={async (data) => {
                    console.log('Dados do formulário:', data);
                    showToast.success('Formulário validado com sucesso!');
                  }}
                  onCancel={() => showToast.info('Formulário cancelado')}
                />
              </CardContent>
            </Card>

            {/* Informações de validação */}
            <Card>
              <CardHeader>
                <CardTitle>Validação Zod em Ação</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm">
                  <p className="font-medium mb-2">Características da validação:</p>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Validação em tempo real</li>
                    <li>Formatação automática de telefone</li>
                    <li>Mensagens de erro em português</li>
                    <li>Integração com React Hook Form</li>
                    <li>Consistência com backend Pydantic</li>
                  </ul>
                </div>

                <div className="text-sm">
                  <p className="font-medium mb-2">Features ativas:</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(config.features).map(([feature, enabled]) => (
                      <Badge 
                        key={feature}
                        variant={enabled ? 'default' : 'secondary'}
                      >
                        {feature}: {enabled ? 'ON' : 'OFF'}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          <SMSReport />
        </TabsContent>
      </Tabs>

      {/* Informações técnicas */}
      <Card>
        <CardHeader>
          <CardTitle>Informações Técnicas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="font-medium mb-2">Configuração:</p>
              <ul className="space-y-1 text-gray-600">
                <li>API: {config.api.baseURL}</li>
                <li>Ambiente: {config.app.environment}</li>
                <li>Versão: {config.app.version}</li>
                <li>Timeout: {config.api.timeout}ms</li>
              </ul>
            </div>

            <div>
              <p className="font-medium mb-2">Limites SMS:</p>
              <ul className="space-y-1 text-gray-600">
                <li>Máx. caracteres: {config.sms.maxLength}</li>
                <li>Unicode: {config.sms.maxLengthUnicode}</li>
                <li>Por minuto: {config.sms.rateLimiting.perMinute}</li>
                <li>Por dia: {config.sms.rateLimiting.perDay}</li>
              </ul>
            </div>

            <div>
              <p className="font-medium mb-2">Permissões do usuário:</p>
              <ul className="space-y-1 text-gray-600">
                <li>SMS: {hasPermission('sms:send') ? '✅' : '❌'}</li>
                <li>Contatos: {hasPermission('contacts:create') ? '✅' : '❌'}</li>
                <li>Campanhas: {hasPermission('campaigns:create') ? '✅' : '❌'}</li>
                <li>Relatórios: {hasPermission('reports:view') ? '✅' : '❌'}</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ===== SERVER SIDE PROPS (EXEMPLO) =====

export const getServerSideProps: GetServerSideProps = async (context) => {
  // Aqui você pode fazer verificações do lado do servidor
  // Por exemplo, verificar autenticação, carregar dados iniciais, etc.
  
  return {
    props: {
      // Props que serão passadas para o componente
      timestamp: new Date().toISOString(),
    },
  };
};
