// React Query Hooks para integração com API
// Hooks personalizados usando React Query para gerenciamento de estado

import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions 
} from '@tanstack/react-query';
import { toast } from 'sonner';
import { 
  apiClient, 
  API_KEYS 
} from '@/lib/api-client';
import {
  ContactForm,
  ContactResponse,
  CampaignForm,
  CampaignResponse,
  TemplateForm,
  TemplateResponse,
  SMSForm,
  SMSResponse,
  PaginatedResponse,
  PaginationParams
} from '@/shared/schemas/zod-schemas';

// ===== TIPOS AUXILIARES =====

type QueryOptions<T> = Omit<UseQueryOptions<T>, 'queryKey' | 'queryFn'>;
type MutationOptions<TData, TVariables> = Omit<
  UseMutationOptions<TData, Error, TVariables>, 
  'mutationFn'
>;

// ===== CONTATOS =====

export function useContacts(
  params?: PaginationParams & {
    search?: string;
    status?: string;
    groups?: string[];
    tags?: string[];
  },
  options?: QueryOptions<PaginatedResponse<ContactResponse>>
) {
  return useQuery({
    queryKey: API_KEYS.contacts(params),
    queryFn: () => apiClient.getContacts(params),
    staleTime: 5 * 60 * 1000, // 5 minutos
    ...options,
  });
}

export function useContact(
  id: number,
  options?: QueryOptions<ContactResponse>
) {
  return useQuery({
    queryKey: API_KEYS.contact(id),
    queryFn: () => apiClient.getContact(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateContact(
  options?: MutationOptions<ContactResponse, ContactForm>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: ContactForm) => apiClient.createContact(data),
    onSuccess: (newContact) => {
      // Invalidar lista de contatos
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      
      // Adicionar contato ao cache
      queryClient.setQueryData(API_KEYS.contact(newContact.id), newContact);
      
      toast.success('Contato criado com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao criar contato: ${error.message}`);
    },
    ...options,
  });
}

export function useUpdateContact(
  options?: MutationOptions<ContactResponse, { id: number; data: Partial<ContactForm> }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => apiClient.updateContact(id, data),
    onSuccess: (updatedContact) => {
      // Atualizar contato no cache
      queryClient.setQueryData(API_KEYS.contact(updatedContact.id), updatedContact);
      
      // Invalidar lista de contatos
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      
      toast.success('Contato atualizado com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao atualizar contato: ${error.message}`);
    },
    ...options,
  });
}

export function useDeleteContact(
  options?: MutationOptions<void, number>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteContact(id),
    onSuccess: (_, deletedId) => {
      // Remover contato do cache
      queryClient.removeQueries({ queryKey: API_KEYS.contact(deletedId) });
      
      // Invalidar lista de contatos
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      
      toast.success('Contato excluído com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao excluir contato: ${error.message}`);
    },
    ...options,
  });
}

export function useBulkImportContacts(
  options?: MutationOptions<any, { contacts: ContactForm[]; options?: any }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ contacts, options: importOptions }) => 
      apiClient.bulkImportContacts(contacts, importOptions),
    onSuccess: (result) => {
      // Invalidar lista de contatos
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      
      toast.success(`${result.successful} contatos importados com sucesso!`);
      
      if (result.failed > 0) {
        toast.warning(`${result.failed} contatos falharam na importação.`);
      }
    },
    onError: (error) => {
      toast.error(`Erro na importação: ${error.message}`);
    },
    ...options,
  });
}

// ===== CAMPANHAS =====

export function useCampaigns(
  params?: PaginationParams & {
    status?: string;
    type?: string;
    search?: string;
    date_from?: string;
    date_to?: string;
  },
  options?: QueryOptions<PaginatedResponse<CampaignResponse>>
) {
  return useQuery({
    queryKey: API_KEYS.campaigns(params),
    queryFn: () => apiClient.getCampaigns(params),
    staleTime: 2 * 60 * 1000, // 2 minutos
    ...options,
  });
}

export function useCampaign(
  id: number,
  options?: QueryOptions<CampaignResponse>
) {
  return useQuery({
    queryKey: API_KEYS.campaign(id),
    queryFn: () => apiClient.getCampaign(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateCampaign(
  options?: MutationOptions<CampaignResponse, CampaignForm>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CampaignForm) => apiClient.createCampaign(data),
    onSuccess: (newCampaign) => {
      // Invalidar lista de campanhas
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      
      // Adicionar campanha ao cache
      queryClient.setQueryData(API_KEYS.campaign(newCampaign.id), newCampaign);
      
      toast.success('Campanha criada com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao criar campanha: ${error.message}`);
    },
    ...options,
  });
}

export function useUpdateCampaign(
  options?: MutationOptions<CampaignResponse, { id: number; data: Partial<CampaignForm> }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => apiClient.updateCampaign(id, data),
    onSuccess: (updatedCampaign) => {
      // Atualizar campanha no cache
      queryClient.setQueryData(API_KEYS.campaign(updatedCampaign.id), updatedCampaign);
      
      // Invalidar lista de campanhas
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      
      toast.success('Campanha atualizada com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao atualizar campanha: ${error.message}`);
    },
    ...options,
  });
}

export function useStartCampaign(
  options?: MutationOptions<CampaignResponse, number>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.startCampaign(id),
    onSuccess: (updatedCampaign) => {
      // Atualizar campanha no cache
      queryClient.setQueryData(API_KEYS.campaign(updatedCampaign.id), updatedCampaign);
      
      // Invalidar listas relacionadas
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      
      toast.success('Campanha iniciada com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao iniciar campanha: ${error.message}`);
    },
    ...options,
  });
}

export function usePauseCampaign(
  options?: MutationOptions<CampaignResponse, number>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.pauseCampaign(id),
    onSuccess: (updatedCampaign) => {
      queryClient.setQueryData(API_KEYS.campaign(updatedCampaign.id), updatedCampaign);
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      
      toast.success('Campanha pausada com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao pausar campanha: ${error.message}`);
    },
    ...options,
  });
}

export function useApproveCampaign(
  options?: MutationOptions<CampaignResponse, number>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.approveCampaign(id),
    onSuccess: (updatedCampaign) => {
      queryClient.setQueryData(API_KEYS.campaign(updatedCampaign.id), updatedCampaign);
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      
      toast.success('Campanha aprovada com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao aprovar campanha: ${error.message}`);
    },
    ...options,
  });
}

// ===== TEMPLATES =====

export function useTemplates(
  params?: PaginationParams & {
    category?: string;
    language?: string;
    search?: string;
    is_active?: boolean;
    tags?: string[];
  },
  options?: QueryOptions<PaginatedResponse<TemplateResponse>>
) {
  return useQuery({
    queryKey: API_KEYS.templates(params),
    queryFn: () => apiClient.getTemplates(params),
    staleTime: 10 * 60 * 1000, // 10 minutos (templates mudam menos)
    ...options,
  });
}

export function useTemplate(
  id: number,
  options?: QueryOptions<TemplateResponse>
) {
  return useQuery({
    queryKey: API_KEYS.template(id),
    queryFn: () => apiClient.getTemplate(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateTemplate(
  options?: MutationOptions<TemplateResponse, TemplateForm>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: TemplateForm) => apiClient.createTemplate(data),
    onSuccess: (newTemplate) => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      queryClient.setQueryData(API_KEYS.template(newTemplate.id), newTemplate);
      
      toast.success('Template criado com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao criar template: ${error.message}`);
    },
    ...options,
  });
}

export function useUpdateTemplate(
  options?: MutationOptions<TemplateResponse, { id: number; data: Partial<TemplateForm> }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => apiClient.updateTemplate(id, data),
    onSuccess: (updatedTemplate) => {
      queryClient.setQueryData(API_KEYS.template(updatedTemplate.id), updatedTemplate);
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      
      toast.success('Template atualizado com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao atualizar template: ${error.message}`);
    },
    ...options,
  });
}

export function useDeleteTemplate(
  options?: MutationOptions<void, number>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteTemplate(id),
    onSuccess: (_, deletedId) => {
      queryClient.removeQueries({ queryKey: API_KEYS.template(deletedId) });
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      
      toast.success('Template excluído com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao excluir template: ${error.message}`);
    },
    ...options,
  });
}

export function useToggleTemplateFavorite(
  options?: MutationOptions<TemplateResponse, number>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.toggleTemplateFavorite(id),
    onSuccess: (updatedTemplate) => {
      queryClient.setQueryData(API_KEYS.template(updatedTemplate.id), updatedTemplate);
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      
      const action = updatedTemplate.is_favorite ? 'adicionado aos' : 'removido dos';
      toast.success(`Template ${action} favoritos!`);
    },
    onError: (error) => {
      toast.error(`Erro ao alterar favorito: ${error.message}`);
    },
    ...options,
  });
}

// ===== SMS =====

export function useSendSMS(
  options?: MutationOptions<SMSResponse, SMSForm>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: SMSForm) => apiClient.sendSMS(data),
    onSuccess: (sentSMS) => {
      // Invalidar histórico de SMS
      queryClient.invalidateQueries({ queryKey: ['sms'] });
      
      // Invalidar dashboard stats
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      
      toast.success('SMS enviado com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao enviar SMS: ${error.message}`);
    },
    ...options,
  });
}

export function useSendBulkSMS(
  options?: MutationOptions<any, {
    phones: string[];
    message: string;
    scheduledAt?: Date;
    templateId?: number;
    contactGroups?: string[];
  }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => apiClient.sendBulkSMS(data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['sms'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      
      toast.success(`${result.successful} SMS enviados com sucesso!`);
      
      if (result.failed > 0) {
        toast.warning(`${result.failed} SMS falharam no envio.`);
      }
    },
    onError: (error) => {
      toast.error(`Erro no envio em massa: ${error.message}`);
    },
    ...options,
  });
}

export function useSMSHistory(
  params?: PaginationParams & {
    status?: string;
    phone?: string;
    campaign_id?: number;
    date_from?: string;
    date_to?: string;
  },
  options?: QueryOptions<PaginatedResponse<SMSResponse>>
) {
  return useQuery({
    queryKey: API_KEYS.smsHistory(params),
    queryFn: () => apiClient.getSMSHistory(params),
    staleTime: 30 * 1000, // 30 segundos (dados mais dinâmicos)
    ...options,
  });
}

export function useCancelScheduledSMS(
  options?: MutationOptions<SMSResponse, number>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.cancelScheduledSMS(id),
    onSuccess: (updatedSMS) => {
      queryClient.setQueryData(API_KEYS.sms(updatedSMS.id), updatedSMS);
      queryClient.invalidateQueries({ queryKey: ['sms'] });
      
      toast.success('SMS agendado cancelado com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro ao cancelar SMS: ${error.message}`);
    },
    ...options,
  });
}

// ===== DASHBOARD E ESTATÍSTICAS =====

export function useDashboardStats(
  options?: QueryOptions<any>
) {
  return useQuery({
    queryKey: API_KEYS.dashboardStats,
    queryFn: () => apiClient.getDashboardStats(),
    staleTime: 60 * 1000, // 1 minuto
    refetchInterval: 2 * 60 * 1000, // Atualizar a cada 2 minutos
    ...options,
  });
}

export function useCampaignStats(
  campaignId: number,
  options?: QueryOptions<any>
) {
  return useQuery({
    queryKey: API_KEYS.campaignStats(campaignId),
    queryFn: () => apiClient.getCampaignStats(campaignId),
    enabled: !!campaignId,
    staleTime: 2 * 60 * 1000, // 2 minutos
    ...options,
  });
}

export function useContactStats(
  options?: QueryOptions<any>
) {
  return useQuery({
    queryKey: API_KEYS.contactStats,
    queryFn: () => apiClient.getContactStats(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    ...options,
  });
}

// ===== UTILITÁRIOS =====

export function useExportContacts(
  options?: MutationOptions<Blob, {
    format: 'csv' | 'excel';
    filters?: any;
  }>
) {
  return useMutation({
    mutationFn: ({ format, filters }) => apiClient.exportContacts(format, filters),
    onSuccess: (blob, variables) => {
      // Criar URL para download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `contatos.${variables.format === 'excel' ? 'xlsx' : 'csv'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Exportação concluída!');
    },
    onError: (error) => {
      toast.error(`Erro na exportação: ${error.message}`);
    },
    ...options,
  });
}

export function useUploadFile(
  options?: MutationOptions<any, { file: File; type: string }>
) {
  return useMutation({
    mutationFn: ({ file, type }) => apiClient.uploadFile(file, type as any),
    onSuccess: (result) => {
      toast.success('Arquivo enviado com sucesso!');
    },
    onError: (error) => {
      toast.error(`Erro no upload: ${error.message}`);
    },
    ...options,
  });
}

// ===== HOOKS PERSONALIZADOS COMBINADOS =====

// Hook para dados da página de contatos
export function useContactsPage(filters?: any) {
  const contactsQuery = useContacts(filters);
  const contactStatsQuery = useContactStats();
  
  return {
    contacts: contactsQuery.data,
    contactStats: contactStatsQuery.data,
    isLoading: contactsQuery.isLoading || contactStatsQuery.isLoading,
    error: contactsQuery.error || contactStatsQuery.error,
    refetch: () => {
      contactsQuery.refetch();
      contactStatsQuery.refetch();
    }
  };
}

// Hook para dados da página de campanhas
export function useCampaignsPage(filters?: any) {
  const campaignsQuery = useCampaigns(filters);
  const templatesQuery = useTemplates({ is_active: true });
  
  return {
    campaigns: campaignsQuery.data,
    templates: templatesQuery.data,
    isLoading: campaignsQuery.isLoading || templatesQuery.isLoading,
    error: campaignsQuery.error || templatesQuery.error,
    refetch: () => {
      campaignsQuery.refetch();
      templatesQuery.refetch();
    }
  };
}

// Hook para dashboard completo
export function useDashboardPage() {
  const dashboardStats = useDashboardStats();
  const recentCampaigns = useCampaigns({ per_page: 5, sort_by: 'created_at' });
  const recentSMS = useSMSHistory({ per_page: 10, sort_by: 'created_at' });
  
  return {
    stats: dashboardStats.data,
    recentCampaigns: recentCampaigns.data,
    recentSMS: recentSMS.data,
    isLoading: dashboardStats.isLoading || recentCampaigns.isLoading || recentSMS.isLoading,
    error: dashboardStats.error || recentCampaigns.error || recentSMS.error,
    refetch: () => {
      dashboardStats.refetch();
      recentCampaigns.refetch();
      recentSMS.refetch();
    }
  };
}
