// Componente de Formulário de Envio de SMS com Validação Zod
import React, { useState, useMemo } from 'react';
import { useZodForm } from '@/shared/hooks/useZodValidation';
import { SMSFormSchema, type SMSForm } from '@/shared/schemas/zod-schemas';
import { PhoneFormatter, DateFormatter, NumberFormatter } from '@/shared/utils/formatters';
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
import { Badge } from '@/components/ui/badge';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { 
  MessageSquare, 
  Phone, 
  Calendar, 
  Send, 
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  FileText,
  User,
  Eye
} from 'lucide-react';
import { toast } from 'sonner';

interface SMSFormProps {
  initialData?: Partial<SMSForm>;
  onSubmit: (data: SMSForm) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  mode?: 'single' | 'quick';
  templates?: Array<{
    id: number;
    name: string;
    content: string;
    variables: string[];
  }>;
  contacts?: Array<{
    id: number;
    name: string;
    phone: string;
  }>;
}

const QUICK_MESSAGES = [
  'Obrigado pelo seu contacto. Entraremos em contacto em breve.',
  'Confirmamos o seu agendamento para hoje às {{hora}}.',
  'A sua encomenda foi processada com sucesso. Referência: {{ref}}',
  'Lembrete: Reunião marcada para amanhã às {{hora}}.',
  'Promoção especial! {{desconto}}% de desconto até {{data}}.'
];

export function SMSForm({ 
  initialData, 
  onSubmit, 
  onCancel, 
  isLoading = false,
  mode = 'single',
  templates = [],
  contacts = []
}: SMSFormProps) {
  const [phonePreview, setPhonePreview] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [templateVariables, setTemplateVariables] = useState<Record<string, string>>({});
  const [showPreview, setShowPreview] = useState(false);

  const form = useZodForm({
    schema: SMSFormSchema,
    defaultValues: {
      phone: '',
      message: '',
      template_id: undefined,
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
    setValue,
    clearErrors
  } = form;

  const watchedPhone = watch('phone');
  const watchedMessage = watch('message');
  const watchedScheduledAt = watch('scheduled_at');

  // Atualizar preview do telefone
  React.useEffect(() => {
    if (watchedPhone) {
      try {
        const formatted = PhoneFormatter.display(watchedPhone);
        setPhonePreview(formatted);
        clearErrors('phone');
      } catch {
        setPhonePreview('Formato inválido');
      }
    } else {
      setPhonePreview('');
    }
  }, [watchedPhone, clearErrors]);

  // Métricas da mensagem
  const messageMetrics = useMemo(() => {
    const length = watchedMessage?.length || 0;
    const costPerSMS = 3.5;
    const remainingChars = 160 - length;
    const smsCount = Math.ceil(length / 160) || 1;
    const totalCost = smsCount * costPerSMS;

    return {
      length,
      remainingChars,
      smsCount,
      totalCost,
      progressPercentage: (length / 160) * 100
    };
  }, [watchedMessage]);

  const handleFormSubmit = async (data: SMSForm) => {
    try {
      // Validações adicionais
      if (data.scheduled_at && new Date(data.scheduled_at) <= new Date()) {
        toast.error('A data agendada deve ser no futuro');
        return;
      }

      const sanitizedData: SMSForm = {
        ...data,
        phone: PhoneFormatter.forSending(data.phone),
        message: data.message.trim(),
        scheduled_at: data.scheduled_at || undefined
      };

      await onSubmit(sanitizedData);
      
      toast.success('SMS enviado com sucesso!');
      
      // Reset form for quick mode
      if (mode === 'quick') {
        form.reset();
        setSelectedTemplate(null);
        setTemplateVariables({});
      }
    } catch (error) {
      toast.error('Erro ao enviar SMS. Tente novamente.');
      console.error('SMS form submission error:', error);
    }
  };

  const handleTemplateSelect = (templateId: string) => {
    const template = templates.find(t => t.id === parseInt(templateId));
    if (template) {
      setSelectedTemplate(template);
      setValue('template_id', template.id, { shouldValidate: true });
      setValue('message', template.content, { shouldValidate: true });
      
      // Reset variables
      const initialVariables: Record<string, string> = {};
      template.variables.forEach(variable => {
        initialVariables[variable] = '';
      });
      setTemplateVariables(initialVariables);
    }
  };

  const handleContactSelect = (contactId: string) => {
    const contact = contacts.find(c => c.id === parseInt(contactId));
    if (contact) {
      setValue('phone', contact.phone, { shouldValidate: true });
    }
  };

  const applyQuickMessage = (message: string) => {
    setValue('message', message, { shouldValidate: true });
    setSelectedTemplate(null);
  };

  const applyTemplateVariables = () => {
    if (selectedTemplate) {
      let finalMessage = selectedTemplate.content;
      
      Object.entries(templateVariables).forEach(([variable, value]) => {
        if (value.trim()) {
          finalMessage = finalMessage.replace(
            new RegExp(`\\{\\{${variable}\\}\\}`, 'g'), 
            value
          );
        }
      });
      
      setValue('message', finalMessage, { shouldValidate: true });
    }
  };

  const generatePreview = () => {
    if (!watchedMessage) return '';
    
    // Se há template selecionado e variáveis preenchidas, aplica as variáveis
    if (selectedTemplate && Object.keys(templateVariables).length > 0) {
      let preview = watchedMessage;
      Object.entries(templateVariables).forEach(([variable, value]) => {
        if (value.trim()) {
          preview = preview.replace(
            new RegExp(`\\{\\{${variable}\\}\\}`, 'g'), 
            value
          );
        }
      });
      return preview;
    }
    
    return watchedMessage;
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      
      {/* Card Principal */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            {mode === 'quick' ? 'Envio Rápido de SMS' : 'Enviar SMS'}
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <Form {...form}>
            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
              
              {/* Primeira Linha - Destinatário */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Telefone */}
                <FormField
                  control={control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="flex items-center gap-2">
                        <Phone className="h-4 w-4" />
                        Telefone do Destinatário *
                      </FormLabel>
                      <FormControl>
                        <div className="space-y-2">
                          <Input 
                            placeholder="84 123 4567"
                            {...field}
                            className={errors.phone ? 'border-red-500' : ''}
                          />
                          
                          {/* Preview do telefone */}
                          {phonePreview && (
                            <p className={`text-xs flex items-center gap-1 ${
                              phonePreview === 'Formato inválido' 
                                ? 'text-red-500' 
                                : 'text-green-600'
                            }`}>
                              {phonePreview === 'Formato inválido' ? (
                                <>
                                  <AlertCircle className="h-3 w-3" />
                                  Formato inválido
                                </>
                              ) : (
                                <>
                                  <CheckCircle className="h-3 w-3" />
                                  Preview: {phonePreview}
                                </>
                              )}
                            </p>
                          )}
                          
                          {/* Seletor de contatos */}
                          {contacts.length > 0 && (
                            <Select onValueChange={handleContactSelect}>
                              <SelectTrigger>
                                <SelectValue placeholder="Ou selecionar contato..." />
                              </SelectTrigger>
                              <SelectContent>
                                {contacts.map(contact => (
                                  <SelectItem key={contact.id} value={contact.id.toString()}>
                                    <div className="flex items-center gap-2">
                                      <User className="h-4 w-4" />
                                      <div>
                                        <div className="font-medium">{contact.name}</div>
                                        <div className="text-xs text-gray-500">
                                          {PhoneFormatter.display(contact.phone)}
                                        </div>
                                      </div>
                                    </div>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          )}
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Agendamento */}
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
                        <div className="space-y-2">
                          <Input 
                            type="datetime-local"
                            {...field}
                            value={field.value ? DateFormatter.forInput(field.value) : ''}
                            onChange={(e) => field.onChange(e.target.value ? new Date(e.target.value) : undefined)}
                            className={errors.scheduled_at ? 'border-red-500' : ''}
                          />
                          
                          {watchedScheduledAt && (
                            <p className="text-xs text-blue-600 flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              Será enviado em: {DateFormatter.display(watchedScheduledAt)}
                            </p>
                          )}
                        </div>
                      </FormControl>
                      <FormDescription>
                        Deixe em branco para envio imediato
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Templates e Mensagens Rápidas */}
              <div className="space-y-4">
                
                {/* Seletor de Template */}
                {templates.length > 0 && (
                  <div>
                    <FormLabel className="flex items-center gap-2 mb-2">
                      <FileText className="h-4 w-4" />
                      Templates Disponíveis
                    </FormLabel>
                    <Select onValueChange={handleTemplateSelect}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecionar template..." />
                      </SelectTrigger>
                      <SelectContent>
                        {templates.map(template => (
                          <SelectItem key={template.id} value={template.id.toString()}>
                            <div>
                              <div className="font-medium">{template.name}</div>
                              <div className="text-xs text-gray-500 truncate max-w-xs">
                                {template.content}
                              </div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Variáveis do Template */}
                {selectedTemplate && selectedTemplate.variables.length > 0 && (
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-medium text-blue-900 mb-3">
                      Preencher Variáveis do Template
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {selectedTemplate.variables.map((variable: string) => (
                        <div key={variable}>
                          <label className="text-sm font-medium text-blue-800">
                            {`{{${variable}}}:`}
                          </label>
                          <Input
                            placeholder={`Valor para ${variable}`}
                            value={templateVariables[variable] || ''}
                            onChange={(e) => 
                              setTemplateVariables(prev => ({
                                ...prev,
                                [variable]: e.target.value
                              }))
                            }
                            className="mt-1"
                          />
                        </div>
                      ))}
                    </div>
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={applyTemplateVariables}
                      className="mt-3"
                    >
                      Aplicar Variáveis
                    </Button>
                  </div>
                )}

                {/* Mensagens Rápidas */}
                {mode === 'quick' && (
                  <div>
                    <FormLabel className="mb-2 block">Mensagens Rápidas</FormLabel>
                    <div className="flex flex-wrap gap-2">
                      {QUICK_MESSAGES.map((message, index) => (
                        <Badge 
                          key={index}
                          variant="outline" 
                          className="cursor-pointer hover:bg-gray-100 p-2"
                          onClick={() => applyQuickMessage(message)}
                        >
                          {message.length > 40 ? `${message.substring(0, 40)}...` : message}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Mensagem */}
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
                            messageMetrics.length > 160 ? 'border-yellow-500' : ''
                          }`}
                        />
                        
                        {/* Métricas da mensagem */}
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-4">
                            <span className={
                              messageMetrics.length > 160 
                                ? 'text-yellow-600 font-medium' 
                                : messageMetrics.length > 140 
                                  ? 'text-yellow-600'
                                  : 'text-gray-600'
                            }>
                              {messageMetrics.length}/160 caracteres
                            </span>
                            
                            {messageMetrics.smsCount > 1 && (
                              <span className="text-yellow-600">
                                {messageMetrics.smsCount} SMS
                              </span>
                            )}
                            
                            <span className="text-green-600 flex items-center gap-1">
                              <DollarSign className="h-3 w-3" />
                              {NumberFormatter.currency(messageMetrics.totalCost)}
                            </span>
                          </div>
                          
                          <div className="w-32">
                            <Progress 
                              value={Math.min(messageMetrics.progressPercentage, 100)} 
                              className="h-2"
                            />
                          </div>
                        </div>
                      </div>
                    </FormControl>
                    <FormDescription>
                      {messageMetrics.smsCount > 1 
                        ? `Mensagem será dividida em ${messageMetrics.smsCount} SMS`
                        : 'SMS padrão suporta até 160 caracteres'
                      }
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Botões de Ação */}
              <div className="flex justify-between">
                <div className="flex gap-2">
                  <Button 
                    type="button" 
                    variant="outline"
                    onClick={() => setShowPreview(!showPreview)}
                    className="flex items-center gap-2"
                  >
                    <Eye className="h-4 w-4" />
                    {showPreview ? 'Ocultar Preview' : 'Preview'}
                  </Button>
                </div>

                <div className="flex gap-3">
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
                    disabled={!isValid || isLoading}
                    className="flex items-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                        Enviando...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        {watchedScheduledAt ? 'Agendar SMS' : 'Enviar SMS'}
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Status da Validação */}
              {isDirty && (
                <div className={`text-sm p-3 rounded-md ${
                  isValid 
                    ? 'bg-green-50 text-green-700 border border-green-200'
                    : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                }`}>
                  {isValid ? (
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      SMS válido e pronto para envio
                      {messageMetrics.smsCount > 1 && (
                        <span className="ml-2">
                          • Custo total: {NumberFormatter.currency(messageMetrics.totalCost)}
                        </span>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      Por favor, corrija os erros acima antes de enviar
                    </div>
                  )}
                </div>
              )}
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Preview do SMS */}
      {showPreview && watchedMessage && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Preview do SMS
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-white border rounded-lg max-w-sm mx-auto">
              <div className="bg-blue-500 text-white p-2 rounded-t text-xs">
                SMS de: AMA MESSAGE
              </div>
              <div className="p-4 border-t">
                <p className="text-sm">{generatePreview()}</p>
              </div>
              <div className="bg-gray-50 p-2 rounded-b text-xs text-gray-600 flex justify-between">
                <span>Caracteres: {generatePreview().length}</span>
                <span>Custo: {NumberFormatter.currency(messageMetrics.totalCost)}</span>
              </div>
            </div>
            
            {phonePreview && phonePreview !== 'Formato inválido' && (
              <p className="text-center text-sm text-gray-600 mt-2">
                Será enviado para: {phonePreview}
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
