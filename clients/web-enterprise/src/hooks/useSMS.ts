import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { ApiClient } from '@/shared/api';
import { 
  SMSRequest, 
  SMSBulkRequest, 
  SMSResponse, 
  PaginatedSMSResponse 
} from '@/shared/types';

const apiClient = new ApiClient({
  baseURL: process.env.REACT_APP_API_URL || '/api/v2',
});

export const useSMS = () => {
  const queryClient = useQueryClient();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Obter lista de SMS
  const { data: smsData, isLoading: smsLoading, error: smsError } = useQuery<PaginatedSMSResponse>(
    ['sms', currentPage, pageSize],
    () => apiClient.getSMSList(currentPage, pageSize),
    {
      keepPreviousData: true,
    }
  );

  // Enviar SMS individual
  const sendSMSMutation = useMutation(
    (smsData: SMSRequest) => apiClient.sendSMS(smsData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['sms']);
      },
    }
  );

  // Enviar SMS em massa
  const sendBulkSMSMutation = useMutation(
    (bulkData: SMSBulkRequest) => apiClient.sendBulkSMS(bulkData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['sms']);
      },
    }
  );

  // Obter estatísticas
  const { data: stats } = useQuery(
    ['sms-stats'],
    () => apiClient.getSMSStats(),
    {
      refetchInterval: 30000, // Atualizar a cada 30 segundos
    }
  );

  return {
    // Dados
    smsData,
    stats,
    
    // Estados
    smsLoading,
    smsError,
    
    // Paginação
    currentPage,
    pageSize,
    setCurrentPage,
    setPageSize,
    
    // Mutações
    sendSMS: sendSMSMutation.mutateAsync,
    sendBulkSMS: sendBulkSMSMutation.mutateAsync,
    
    // Estados das mutações
    sendingSMS: sendSMSMutation.isLoading,
    sendingBulkSMS: sendBulkSMSMutation.isLoading,
  };
};
