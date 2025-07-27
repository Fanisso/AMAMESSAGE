// Componente de Formulário de Contato com Validação Zod
import React, { useState } from 'react';
import { useZodForm } from '@/shared/hooks/useZodValidation';
import { ContactFormSchema, type ContactForm } from '@/shared/schemas/zod-schemas';
import { PhoneFormatter, TextFormatter } from '@/shared/utils/formatters';
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
  FormMessage 
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
import { 
  User, 
  Phone, 
  Mail, 
  Building, 
  MapPin, 
  Briefcase, 
  Save, 
  X, 
  Plus,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';

interface ContactFormProps {
  initialData?: Partial<ContactForm>;
  onSubmit: (data: ContactForm) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}

const CONTACT_GROUPS = [
  'Clientes VIP',
  'Leads',
  'Parceiros',
  'Fornecedores',
  'Funcionários',
  'Prospectos'
];

const PREDEFINED_TAGS = [
  'importante',
  'vip',
  'lead',
  'cliente',
  'parceiro',
  'prospect',
  'ativo',
  'inativo'
];

export function ContactForm({ 
  initialData, 
  onSubmit, 
  onCancel, 
  isLoading = false,
  mode = 'create'
}: ContactFormProps) {
  const [newTag, setNewTag] = useState('');
  const [phonePreview, setPhonePreview] = useState('');

  const form = useZodForm({
    schema: ContactFormSchema,
    defaultValues: {
      name: '',
      phone: '',
      email: '',
      company: '',
      position: '',
      location: '',
      tags: [],
      groups: [],
      notes: '',
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
  const watchedTags = watch('tags');
  const watchedGroups = watch('groups');

  // Atualizar preview do telefone em tempo real
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

  const handleFormSubmit = async (data: ContactForm) => {
    try {
      // Sanitizar dados antes do envio
      const sanitizedData = {
        ...data,
        name: TextFormatter.titleCase(data.name.trim()),
        phone: PhoneFormatter.forSending(data.phone),
        email: data.email?.trim().toLowerCase() || undefined,
        company: data.company?.trim() || undefined,
        position: data.position?.trim() || undefined,
        location: data.location?.trim() || undefined,
        notes: data.notes?.trim() || undefined,
        tags: data.tags.filter(tag => tag.trim().length > 0),
        groups: data.groups
      };

      await onSubmit(sanitizedData);
      
      toast.success(
        mode === 'create' 
          ? 'Contato criado com sucesso!' 
          : 'Contato atualizado com sucesso!'
      );
    } catch (error) {
      toast.error('Erro ao salvar contato. Tente novamente.');
      console.error('Contact form submission error:', error);
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

  const addGroup = (group: string) => {
    if (!watchedGroups.includes(group)) {
      const updatedGroups = [...watchedGroups, group];
      setValue('groups', updatedGroups, { shouldValidate: true });
    }
  };

  const removeGroup = (groupToRemove: string) => {
    const updatedGroups = watchedGroups.filter(group => group !== groupToRemove);
    setValue('groups', updatedGroups, { shouldValidate: true });
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          {mode === 'create' ? 'Novo Contato' : 'Editar Contato'}
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <Form {...form}>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
            
            {/* Informações Básicas */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      Nome Completo *
                    </FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="João Silva"
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
                name="phone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Phone className="h-4 w-4" />
                      Telefone *
                    </FormLabel>
                    <FormControl>
                      <div className="space-y-1">
                        <Input 
                          placeholder="84 123 4567"
                          {...field}
                          className={errors.phone ? 'border-red-500' : ''}
                        />
                        {phonePreview && (
                          <p className={`text-xs ${
                            phonePreview === 'Formato inválido' 
                              ? 'text-red-500' 
                              : 'text-green-600'
                          }`}>
                            {phonePreview === 'Formato inválido' ? (
                              <><AlertCircle className="h-3 w-3 inline mr-1" />Formato inválido</>
                            ) : (
                              <><CheckCircle className="h-3 w-3 inline mr-1" />Preview: {phonePreview}</>
                            )}
                          </p>
                        )}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Email
                    </FormLabel>
                    <FormControl>
                      <Input 
                        type="email"
                        placeholder="joao@exemplo.com"
                        {...field}
                        className={errors.email ? 'border-red-500' : ''}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={control}
                name="company"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Building className="h-4 w-4" />
                      Empresa
                    </FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Empresa Lda"
                        {...field}
                        className={errors.company ? 'border-red-500' : ''}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={control}
                name="position"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Briefcase className="h-4 w-4" />
                      Cargo
                    </FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Diretor Geral"
                        {...field}
                        className={errors.position ? 'border-red-500' : ''}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={control}
                name="location"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      Localização
                    </FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Maputo, Moçambique"
                        {...field}
                        className={errors.location ? 'border-red-500' : ''}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Tags */}
            <div className="space-y-3">
              <FormLabel>Tags</FormLabel>
              
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
                  className="flex-1"
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

            {/* Grupos */}
            <div className="space-y-3">
              <FormLabel>Grupos</FormLabel>
              
              {/* Grupos Selecionados */}
              {watchedGroups.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {watchedGroups.map((group, index) => (
                    <Badge 
                      key={index} 
                      variant="default" 
                      className="flex items-center gap-1"
                    >
                      {group}
                      <X 
                        className="h-3 w-3 cursor-pointer hover:text-red-200"
                        onClick={() => removeGroup(group)}
                      />
                    </Badge>
                  ))}
                </div>
              )}

              {/* Selecionar Grupo */}
              <Select onValueChange={addGroup}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecionar grupo..." />
                </SelectTrigger>
                <SelectContent>
                  {CONTACT_GROUPS
                    .filter(group => !watchedGroups.includes(group))
                    .map(group => (
                      <SelectItem key={group} value={group}>
                        {group}
                      </SelectItem>
                    ))
                  }
                </SelectContent>
              </Select>
            </div>

            {/* Notas */}
            <FormField
              control={control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notas</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Informações adicionais sobre o contato..."
                      rows={4}
                      {...field}
                      className={errors.notes ? 'border-red-500' : ''}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

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
                disabled={!isValid || isLoading}
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
                    {mode === 'create' ? 'Criar Contato' : 'Salvar Alterações'}
                  </>
                )}
              </Button>
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
                    Formulário válido e pronto para envio
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    Por favor, corrija os erros acima antes de continuar
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
