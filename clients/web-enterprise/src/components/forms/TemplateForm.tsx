// Componente de Formulário de Template com Validação Zod
import React, { useState, useMemo } from 'react';
import { useZodForm } from '@/shared/hooks/useZodValidation';
import { TemplateFormSchema, type TemplateForm, CampaignTypeEnum } from '@/shared/schemas/zod-schemas';
import { TextFormatter } from '@/shared/utils/formatters';
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
import { Switch } from '@/components/ui/switch';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  Tag, 
  Globe, 
  MessageSquare, 
  Save, 
  AlertCircle,
  CheckCircle,
  Eye,
  Plus,
  X,
  Variable,
  Lightbulb
} from 'lucide-react';
import { toast } from 'sonner';

interface TemplateFormProps {
  initialData?: Partial<TemplateForm>;
  onSubmit: (data: TemplateForm) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}

const CATEGORY_OPTIONS = [
  { 
    value: 'promotional', 
    label: 'Promocional', 
    description: 'Templates para ofertas e promoções',
    icon: '🎯',
    color: 'bg-red-50 text-red-700 border-red-200'
  },
  { 
    value: 'informational', 
    label: 'Informativo', 
    description: 'Templates para comunicados gerais',
    icon: 'ℹ️',
    color: 'bg-blue-50 text-blue-700 border-blue-200'
  },
  { 
    value: 'transactional', 
    label: 'Transacional', 
    description: 'Templates para confirmações',
    icon: '💳',
    color: 'bg-green-50 text-green-700 border-green-200'
  },
  { 
    value: 'support', 
    label: 'Suporte', 
    description: 'Templates para atendimento',
    icon: '🎧',
    color: 'bg-purple-50 text-purple-700 border-purple-200'
  },
  { 
    value: 'welcome', 
    label: 'Boas-vindas', 
    description: 'Templates de boas-vindas',
    icon: '👋',
    color: 'bg-yellow-50 text-yellow-700 border-yellow-200'
  },
  { 
    value: 'reminder', 
    label: 'Lembrete', 
    description: 'Templates de lembretes',
    icon: '⏰',
    color: 'bg-orange-50 text-orange-700 border-orange-200'
  }
];

const LANGUAGE_OPTIONS = [
  { value: 'pt', label: 'Português', flag: '🇵🇹' },
  { value: 'en', label: 'English', flag: '🇺🇸' },
  { value: 'fr', label: 'Français', flag: '🇫🇷' },
  { value: 'es', label: 'Español', flag: '🇪🇸' }
];

const PREDEFINED_TAGS = [
  'urgente',
  'promocao',
  'desconto',
  'novidade',
  'evento',
  'confirmacao',
  'lembrete',
  'boas-vindas',
  'agradecimento',
  'importante'
];

const TEMPLATE_SUGGESTIONS = [
  {
    category: 'promotional',
    content: 'Oferta especial! {{desconto}}% de desconto em {{produto}}. Válido até {{data_limite}}. Use o código {{codigo}}. {{empresa}}'
  },
  {
    category: 'welcome',
    content: 'Bem-vindo(a) {{nome}}! Obrigado por se juntar à {{empresa}}. Sua conta foi criada com sucesso.'
  },
  {
    category: 'reminder',
    content: 'Lembrete: Você tem um agendamento em {{data}} às {{hora}}. {{local}}. Para cancelar, responda CANCELAR.'
  },
  {
    category: 'transactional',
    content: 'Transação confirmada! Valor: {{valor}} MT. {{descricao}}. Referência: {{referencia}}. {{empresa}}'
  }
];

export function TemplateForm({ 
  initialData, 
  onSubmit, 
  onCancel, 
  isLoading = false,
  mode = 'create'
}: TemplateFormProps) {
  const [newTag, setNewTag] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [previewVariables, setPreviewVariables] = useState<Record<string, string>>({});

  const form = useZodForm({
    schema: TemplateFormSchema,
    defaultValues: {
      name: '',
      description: '',
      content: '',
      category: 'informational' as const,
      language: 'pt',
      tags: [],
      is_active: true,
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

  const watchedContent = watch('content');
  const watchedTags = watch('tags');
  const watchedCategory = watch('category');

  // Extrair variáveis do template
  const templateVariables = useMemo(() => {
    if (!watchedContent) return [];
    const matches = watchedContent.match(/\{\{([^}]+)\}\}/g);
    return matches ? matches.map(match => match.replace(/[{}]/g, '')) : [];
  }, [watchedContent]);

  // Métricas do template
  const templateMetrics = useMemo(() => {
    const contentLength = watchedContent?.length || 0;
    const variableCount = templateVariables.length;
    const remainingChars = 160 - contentLength;
    
    return {
      contentLength,
      variableCount,
      remainingChars,
      progressPercentage: (contentLength / 160) * 100
    };
  }, [watchedContent, templateVariables]);

  // Gerar preview com variáveis substituídas
  const generatePreview = () => {
    if (!watchedContent) return '';
    
    let preview = watchedContent;
    templateVariables.forEach(variable => {
      const value = previewVariables[variable] || `[${variable}]`;
      preview = preview.replace(new RegExp(`\\{\\{${variable}\\}\\}`, 'g'), value);
    });
    
    return preview;
  };

  const handleFormSubmit = async (data: TemplateForm) => {
    try {
      const sanitizedData: TemplateForm = {
        ...data,
        name: TextFormatter.titleCase(data.name.trim()),
        description: data.description?.trim() || '',
        content: data.content.trim(),
        tags: data.tags.filter(tag => tag.trim().length > 0)
      };

      await onSubmit(sanitizedData);
      
      toast.success(
        mode === 'create' 
          ? 'Template criado com sucesso!' 
          : 'Template atualizado com sucesso!'
      );
    } catch (error) {
      toast.error('Erro ao salvar template. Tente novamente.');
      console.error('Template form submission error:', error);
    }
  };

  const addTag = () => {
    if (newTag.trim() && !watchedTags.includes(newTag.trim().toLowerCase())) {
      const updatedTags = [...watchedTags, newTag.trim().toLowerCase()];
      setValue('tags', updatedTags, { shouldValidate: true });
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    const updatedTags = watchedTags.filter(tag => tag !== tagToRemove);
    setValue('tags', updatedTags, { shouldValidate: true });
  };

  const applySuggestion = (suggestion: string) => {
    setValue('content', suggestion, { shouldValidate: true });
  };

  const selectedCategory = CATEGORY_OPTIONS.find(cat => cat.value === watchedCategory);

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      
      {/* Card Principal */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            {mode === 'create' ? 'Novo Template SMS' : 'Editar Template'}
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <Form {...form}>
            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
              
              {/* Informações Básicas */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Coluna Esquerda */}
                <div className="space-y-4">
                  <FormField
                    control={control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          Nome do Template *
                        </FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="Ex: Confirmação de Pedido"
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
                            placeholder="Descreva quando usar este template..."
                            rows={3}
                            {...field}
                            className={errors.description ? 'border-red-500' : ''}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={control}
                      name="category"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Categoria *</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Selecionar..." />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {CATEGORY_OPTIONS.map(option => (
                                <SelectItem key={option.value} value={option.value}>
                                  <div className="flex items-center gap-2">
                                    <span>{option.icon}</span>
                                    <span>{option.label}</span>
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
                      name="language"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="flex items-center gap-2">
                            <Globe className="h-4 w-4" />
                            Idioma
                          </FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {LANGUAGE_OPTIONS.map(option => (
                                <SelectItem key={option.value} value={option.value}>
                                  <div className="flex items-center gap-2">
                                    <span>{option.flag}</span>
                                    <span>{option.label}</span>
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Coluna Direita - Status e Métricas */}
                <div className="space-y-4">
                  <FormField
                    control={control}
                    name="is_active"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                        <div className="space-y-0.5">
                          <FormLabel className="text-base">Template Ativo</FormLabel>
                          <FormDescription>
                            Templates ativos podem ser usados em campanhas
                          </FormDescription>
                        </div>
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  {/* Categoria Selecionada */}
                  {selectedCategory && (
                    <div className={`p-4 rounded-lg border ${selectedCategory.color}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">{selectedCategory.icon}</span>
                        <span className="font-medium">{selectedCategory.label}</span>
                      </div>
                      <p className="text-sm">{selectedCategory.description}</p>
                    </div>
                  )}

                  {/* Métricas */}
                  <div className="p-4 bg-gray-50 rounded-lg border">
                    <h4 className="font-medium text-gray-900 mb-3">Métricas do Template</h4>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Caracteres:</span>
                        <span className={`font-medium ${
                          templateMetrics.contentLength > 160 ? 'text-red-600' : 'text-gray-900'
                        }`}>
                          {templateMetrics.contentLength}/160
                        </span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-gray-600">Variáveis:</span>
                        <span className="font-medium">{templateMetrics.variableCount}</span>
                      </div>
                      
                      <div className="w-full">
                        <Progress 
                          value={Math.min(templateMetrics.progressPercentage, 100)} 
                          className="h-2"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Conteúdo do Template */}
              <FormField
                control={control}
                name="content"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      Conteúdo do Template *
                    </FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Textarea 
                          placeholder="Digite o conteúdo do template aqui... Use {{variavel}} para campos dinâmicos."
                          rows={5}
                          {...field}
                          className={`${errors.content ? 'border-red-500' : ''} ${
                            templateMetrics.contentLength > 160 ? 'border-red-500' : ''
                          }`}
                        />
                        
                        {/* Indicador de caracteres */}
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-4">
                            <span className={
                              templateMetrics.contentLength > 160 
                                ? 'text-red-600 font-medium' 
                                : templateMetrics.contentLength > 140 
                                  ? 'text-yellow-600'
                                  : 'text-gray-600'
                            }>
                              {templateMetrics.contentLength}/160 caracteres
                            </span>
                            
                            {templateMetrics.remainingChars < 0 && (
                              <span className="text-red-600 font-medium">
                                {Math.abs(templateMetrics.remainingChars)} excedentes
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </FormControl>
                    <FormDescription className="flex items-center gap-2">
                      <Variable className="h-4 w-4" />
                      Use {`{{nome_variavel}}`} para campos dinâmicos. Ex: {`{{nome}}, {{empresa}}, {{data}}`}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Variáveis Detectadas */}
              {templateVariables.length > 0 && (
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-900 mb-3 flex items-center gap-2">
                    <Variable className="h-4 w-4" />
                    Variáveis Detectadas ({templateVariables.length})
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {templateVariables.map((variable, index) => (
                      <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800">
                        {`{{${variable}}}`}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Tags */}
              <div className="space-y-3">
                <FormLabel className="flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Tags
                </FormLabel>
                
                {/* Tags Existentes */}
                {watchedTags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {watchedTags.map((tag, index) => (
                      <Badge 
                        key={index} 
                        variant="secondary" 
                        className="flex items-center gap-1"
                      >
                        {tag}
                        <X 
                          className="h-3 w-3 cursor-pointer hover:text-red-500"
                          onClick={() => removeTag(tag)}
                        />
                      </Badge>
                    ))}
                  </div>
                )}

                {/* Adicionar Nova Tag */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Nova tag..."
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  />
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="sm"
                    onClick={addTag}
                    disabled={!newTag.trim()}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>

                {/* Tags Predefinidas */}
                <div className="flex flex-wrap gap-2">
                  {PREDEFINED_TAGS
                    .filter(tag => !watchedTags.includes(tag))
                    .map(tag => (
                      <Badge 
                        key={tag}
                        variant="outline" 
                        className="cursor-pointer hover:bg-gray-100"
                        onClick={() => {
                          const updatedTags = [...watchedTags, tag];
                          setValue('tags', updatedTags, { shouldValidate: true });
                        }}
                      >
                        + {tag}
                      </Badge>
                    ))
                  }
                </div>
              </div>

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
                    disabled={!isValid || isLoading || templateMetrics.contentLength > 160}
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
                        {mode === 'create' ? 'Criar Template' : 'Salvar Alterações'}
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Status da Validação */}
              {isDirty && (
                <div className={`text-sm p-3 rounded-md ${
                  isValid && templateMetrics.contentLength <= 160
                    ? 'bg-green-50 text-green-700 border border-green-200'
                    : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                }`}>
                  {isValid && templateMetrics.contentLength <= 160 ? (
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      Template válido e pronto para uso
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      {templateMetrics.contentLength > 160 
                        ? 'Conteúdo excede 160 caracteres'
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

      {/* Sugestões de Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Sugestões de Templates
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {TEMPLATE_SUGGESTIONS.map((suggestion, index) => {
              const category = CATEGORY_OPTIONS.find(cat => cat.value === suggestion.category);
              return (
                <div key={index} className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center gap-2 mb-2">
                    <span>{category?.icon}</span>
                    <span className="font-medium">{category?.label}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{suggestion.content}</p>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => applySuggestion(suggestion.content)}
                  >
                    Usar este template
                  </Button>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Preview Modal/Card */}
      {showPreview && watchedContent && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Preview do Template
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Campos para Variáveis */}
            {templateVariables.length > 0 && (
              <div className="mb-4 space-y-3">
                <h4 className="font-medium">Preencha as variáveis para preview:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {templateVariables.map((variable) => (
                    <div key={variable}>
                      <label className="text-sm font-medium">{`{{${variable}}}:`}</label>
                      <Input
                        placeholder={`Valor para ${variable}`}
                        value={previewVariables[variable] || ''}
                        onChange={(e) => 
                          setPreviewVariables(prev => ({
                            ...prev,
                            [variable]: e.target.value
                          }))
                        }
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Preview do SMS */}
            <div className="bg-white border rounded-lg">
              <div className="bg-blue-500 text-white p-2 rounded-t text-xs">
                SMS de: AMA MESSAGE
              </div>
              <div className="p-4 border-t">
                <p className="text-sm">{generatePreview()}</p>
              </div>
              <div className="bg-gray-50 p-2 rounded-b text-xs text-gray-600">
                Caracteres: {generatePreview().length}/160
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
