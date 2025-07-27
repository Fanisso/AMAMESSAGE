// Componente de Formulário de Campanha com Validação Zod
import React, { useState, useMemo } from 'react';
import { useZodForm } from '@/shared/hooks/useZodValidation';
import { CampaignFormSchema, type CampaignForm, CampaignTypeEnum } from '@/shared/schemas/zod-schemas';
import { NumberFormatter, DateFormatter } from '@/shared/utils/formatters';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent 
} from '@/components/ui/card';
import { 
  Form, 
  FormControl, 
  FormField, 
  FormItem, 
  FormLabel, 
  FormMessage,
  FormDescription
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { 
  Megaphone, 
  Calendar, 
  DollarSign, 
  Users, 
  MessageSquare, 
  Save, 
  AlertCircle,
  CheckCircle,
  Info,
  Target
} from 'lucide-react';
import { toast } from 'sonner';

interface CampaignFormProps {
  initialData?: Partial<CampaignForm>;
  onSubmit: (data: CampaignForm) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}

const CAMPAIGN_TYPE_OPTIONS = [
  { 
    value: 'promotional', 
    label: 'Promocional', 
    description: 'Campanhas de promoção e ofertas especiais',
    icon: '🎯'
  },
  { 
    value: 'informational', 
    label: 'Informativa', 
    description: 'Comunicados e informações gerais',
    icon: 'ℹ️'
  },
  { 
    value: 'transactional', 
    label: 'Transacional', 
    description: 'Confirmações e notificações de transações',
    icon: '💳'
  },
  { 
    value: 'support', 
    label: 'Suporte', 
    description: 'Atendimento ao cliente e suporte',
    icon: '🎧'
  },
  { 
    value: 'welcome', 
    label: 'Boas-vindas', 
    description: 'Mensagens de boas-vindas para novos clientes',
    icon: '👋'
  },
  { 
    value: 'reminder', 
    label: 'Lembrete', 
    description: 'Lembretes de compromissos e prazos',
    icon: '⏰'
  }
];

const TARGET_AUDIENCE_OPTIONS = [
  'Todos os Contatos',
  'Clientes VIP',
  'Novos Clientes',
  'Clientes Inativos',
  'Leads Qualificados',
  'Parceiros',
  'Funcionários',
  'Grupo Personalizado'
];

export function CampaignForm({ 
  initialData, 
  onSubmit, 
  onCancel, 
  isLoading = false,
  mode = 'create'
}: CampaignFormProps) {
  const [messageLength, setMessageLength] = useState(0);
  const [estimatedCost, setEstimatedCost] = useState(0);
  const [estimatedReach, setEstimatedReach] = useState(100);

  const form = useZodForm({
    schema: CampaignFormSchema,
    defaultValues: {
      name: '',
      description: '',
      message: '',
      type: 'promotional' as const,
      target_audience: '',
      budget: 0,
      scheduled_at: undefined,
      ...initialData
    },
    mode: 'onChange'
  });

  const { 
    handleSubmit, 
    control, 
    formState: { errors, isValid, isDirty },
    watch,
    setValue
  } = form;

  const watchedMessage = watch('message');
  const watchedBudget = watch('budget');
  const watchedTargetAudience = watch('target_audience');

  // Calcular métricas em tempo real
  const metrics = useMemo(() => {
    const length = watchedMessage?.length || 0;
    const costPerSMS = 3.5; // MT por SMS
    const maxSMSWithBudget = Math.floor(watchedBudget / costPerSMS);
    const estimatedReachValue = Math.min(maxSMSWithBudget, estimatedReach);
    const totalCost = estimatedReachValue * costPerSMS;

    return {
      messageLength: length,
      remainingChars: 160 - length,
      estimatedReach: estimatedReachValue,
      costPerSMS,
      totalCost,
      maxPossibleSMS: maxSMSWithBudget
    };
  }, [watchedMessage, watchedBudget, estimatedReach]);

  React.useEffect(() => {
    setMessageLength(metrics.messageLength);
    setEstimatedCost(metrics.totalCost);
  }, [metrics]);

  const handleFormSubmit = async (data: CampaignForm) => {
    try {
      // Validações adicionais de negócio
      if (data.scheduled_at && new Date(data.scheduled_at) <= new Date()) {
        toast.error('A data agendada deve ser no futuro');
        return;
      }

      if (metrics.totalCost > data.budget) {
        toast.error('O custo estimado excede o orçamento disponível');
        return;
      }

      const sanitizedData: CampaignForm = {
        ...data,
        name: data.name.trim(),
        description: data.description?.trim() || '',
        message: data.message.trim(),
        target_audience: data.target_audience.trim(),
        budget: Number(data.budget)
      };

      await onSubmit(sanitizedData);
      
      toast.success(
        mode === 'create' 
          ? 'Campanha criada com sucesso!' 
          : 'Campanha atualizada com sucesso!'
      );
    } catch (error) {
      toast.error('Erro ao salvar campanha. Tente novamente.');
      console.error('Campaign form submission error:', error);
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage <= 50) return 'bg-green-500';
    if (percentage <= 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const messageProgressPercentage = (messageLength / 160) * 100;

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Megaphone className="h-5 w-5" />
          {mode === 'create' ? 'Nova Campanha SMS' : 'Editar Campanha'}
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <Form {...form}>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
            
            {/* Informações Básicas */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Coluna Esquerda - Dados da Campanha */}
              <div className="space-y-4">
                <FormField
                  control={control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="flex items-center gap-2">
                        <Megaphone className="h-4 w-4" />
                        Nome da Campanha *
                      </FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="Ex: Promoção de Verão 2025"
                          {...field}
                          className={errors.name ? 'border-red-500' : ''}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Descrição</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Descreva o objetivo e contexto da campanha..."
                          rows={3}
                          {...field}
                          className={errors.description ? 'border-red-500' : ''}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={control}
                  name="type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tipo de Campanha *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecionar tipo..." />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {CAMPAIGN_TYPE_OPTIONS.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              <div className="flex items-center gap-2">
                                <span>{option.icon}</span>
                                <div>
                                  <div className="font-medium">{option.label}</div>
                                  <div className="text-xs text-gray-500">
                                    {option.description}
                                  </div>
                                </div>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={control}
                  name="target_audience"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="flex items-center gap-2">
                        <Target className="h-4 w-4" />
                        Público-Alvo *
                      </FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecionar público..." />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {TARGET_AUDIENCE_OPTIONS.map(option => (
                            <SelectItem key={option} value={option}>
                              {option}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Coluna Direita - Orçamento e Agendamento */}
              <div className="space-y-4">
                <FormField
                  control={control}
                  name="budget"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4" />
                        Orçamento (MT) *
                      </FormLabel>
                      <FormControl>
                        <Input 
                          type="number"
                          min="0"
                          step="0.01"
                          placeholder="0.00"
                          {...field}
                          onChange={(e) => field.onChange(Number(e.target.value))}
                          className={errors.budget ? 'border-red-500' : ''}
                        />
                      </FormControl>
                      <FormDescription>
                        Custo por SMS: {NumberFormatter.currency(3.5)}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={control}
                  name="scheduled_at"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        Agendamento (Opcional)
                      </FormLabel>
                      <FormControl>
                        <Input 
                          type="datetime-local"
                          {...field}
                          value={field.value ? DateFormatter.forInput(field.value) : ''}
                          onChange={(e) => field.onChange(e.target.value ? new Date(e.target.value) : undefined)}
                          className={errors.scheduled_at ? 'border-red-500' : ''}
                        />
                      </FormControl>
                      <FormDescription>
                        Deixe em branco para envio imediato
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Métricas em Tempo Real */}
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-900 mb-3 flex items-center gap-2">
                    <Info className="h-4 w-4" />
                    Estimativas
                  </h4>
                  
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-blue-700">SMS Máximos:</span>
                      <span className="font-medium">{metrics.maxPossibleSMS.toLocaleString()}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-blue-700">Alcance Estimado:</span>
                      <span className="font-medium">{metrics.estimatedReach.toLocaleString()}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-blue-700">Custo Total:</span>
                      <span className="font-medium text-green-600">
                        {NumberFormatter.currency(metrics.totalCost)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Mensagem SMS */}
            <FormField
              control={control}
              name="message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4" />
                    Mensagem SMS *
                  </FormLabel>
                  <FormControl>
                    <div className="space-y-2">
                      <Textarea 
                        placeholder="Digite sua mensagem aqui..."
                        rows={4}
                        {...field}
                        className={`${errors.message ? 'border-red-500' : ''} ${
                          messageLength > 160 ? 'border-red-500' : ''
                        }`}
                      />
                      
                      {/* Contador de Caracteres */}
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-4">
                          <span className={
                            messageLength > 160 
                              ? 'text-red-600 font-medium' 
                              : messageLength > 140 
                                ? 'text-yellow-600'
                                : 'text-gray-600'
                          }>
                            {messageLength}/160 caracteres
                          </span>
                          
                          {metrics.remainingChars < 0 && (
                            <span className="text-red-600 font-medium">
                              {Math.abs(metrics.remainingChars)} caracteres excedentes
                            </span>
                          )}
                        </div>
                        
                        <div className="w-32">
                          <Progress 
                            value={Math.min(messageProgressPercentage, 100)} 
                            className="h-2"
                          />
                        </div>
                      </div>
                    </div>
                  </FormControl>
                  <FormDescription>
                    SMS padrão suporta até 160 caracteres. Mensagens maiores podem ser divididas.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Preview da Mensagem */}
            {watchedMessage && (
              <div className="p-4 bg-gray-50 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-2">Preview do SMS:</h4>
                <div className="bg-white p-3 rounded border border-gray-200 text-sm">
                  <div className="bg-blue-500 text-white p-2 rounded-t text-xs">
                    SMS de: AMA MESSAGE
                  </div>
                  <div className="p-3 border border-t-0 rounded-b">
                    {watchedMessage || "Sua mensagem aparecerá aqui..."}
                  </div>
                </div>
              </div>
            )}

            {/* Botões de Ação */}
            <div className="flex justify-end gap-3">
              {onCancel && (
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={onCancel}
                  disabled={isLoading}
                >
                  Cancelar
                </Button>
              )}
              
              <Button 
                type="submit" 
                disabled={!isValid || isLoading || messageLength > 160}
                className="flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Salvando...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    {mode === 'create' ? 'Criar Campanha' : 'Salvar Alterações'}
                  </>
                )}
              </Button>
            </div>

            {/* Status da Validação */}
            {isDirty && (
              <div className={`text-sm p-3 rounded-md ${
                isValid && messageLength <= 160
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
              }`}>
                {isValid && messageLength <= 160 ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Campanha válida e pronta para criação
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    {messageLength > 160 
                      ? 'Mensagem excede 160 caracteres'
                      : 'Por favor, corrija os erros acima antes de continuar'
                    }
                  </div>
                )}
              </div>
            )}
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
