# Formulários com Validação Zod - Documentação

Esta documentação descreve os componentes de formulário implementados com validação Zod integrada no sistema AMAMESSAGE.

## Componentes Implementados

### 1. ContactForm
**Arquivo**: `clients/web-enterprise/src/components/forms/ContactForm.tsx`

#### Funcionalidades
- ✅ Validação de telefone moçambicano em tempo real
- ✅ Preview do telefone formatado (+258 XX XXX XXXX)
- ✅ Sistema de tags predefinidas e personalizadas
- ✅ Seleção de grupos de contato
- ✅ Campos opcionais: empresa, cargo, localização
- ✅ Validação de email opcional
- ✅ Notas com limite de caracteres
- ✅ Status de validação visual

#### Validações Implementadas
```typescript
// Telefone moçambicano
phone: z.string().refine((phone) => mozambiquePhoneRegex.test(phone))

// Nome obrigatório
name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres')

// Email opcional válido
email: z.string().email('Email inválido').optional()
```

#### Props Interface
```typescript
interface ContactFormProps {
  initialData?: Partial<ContactForm>;
  onSubmit: (data: ContactForm) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}
```

### 2. CampaignForm
**Arquivo**: `clients/web-enterprise/src/components/forms/CampaignForm.tsx`

#### Funcionalidades
- ✅ Validação de mensagem SMS (160 caracteres)
- ✅ Contador de caracteres em tempo real
- ✅ Cálculo de custo estimado (3.5 MT por SMS)
- ✅ Seleção de tipo de campanha com descrições
- ✅ Validação de orçamento
- ✅ Agendamento opcional com validação de data futura
- ✅ Preview do SMS
- ✅ Métricas em tempo real

#### Validações Implementadas
```typescript
// Mensagem SMS limitada
message: z.string().max(160, 'Mensagem não pode exceder 160 caracteres')

// Orçamento positivo
budget: z.number().positive('Orçamento deve ser positivo')

// Data futura para agendamento
scheduled_at: z.date().refine(date => date > new Date(), 'Data deve ser no futuro')
```

#### Tipos de Campanha
- 🎯 Promocional - Promoções e ofertas especiais
- ℹ️ Informativa - Comunicados e informações gerais
- 💳 Transacional - Confirmações de transações
- 🎧 Suporte - Atendimento ao cliente
- 👋 Boas-vindas - Mensagens para novos clientes
- ⏰ Lembrete - Lembretes de compromissos

### 3. TemplateForm
**Arquivo**: `clients/web-enterprise/src/components/forms/TemplateForm.tsx`

#### Funcionalidades
- ✅ Editor de templates com variáveis {{variable}}
- ✅ Detecção automática de variáveis
- ✅ Preview com substituição de variáveis
- ✅ Sistema de tags avançado
- ✅ Categorização por tipo
- ✅ Suporte a múltiplos idiomas
- ✅ Templates sugeridos por categoria
- ✅ Status ativo/inativo
- ✅ Métricas do template

#### Sistema de Variáveis
```typescript
// Detecção automática de variáveis
const templateVariables = useMemo(() => {
  const matches = content.match(/\{\{([^}]+)\}\}/g);
  return matches ? matches.map(match => match.replace(/[{}]/g, '')) : [];
}, [content]);
```

#### Templates Sugeridos
- **Promocional**: `Oferta especial! {{desconto}}% de desconto em {{produto}}`
- **Boas-vindas**: `Bem-vindo(a) {{nome}}! Obrigado por se juntar à {{empresa}}`
- **Lembrete**: `Lembrete: Você tem um agendamento em {{data}} às {{hora}}`
- **Transacional**: `Transação confirmada! Valor: {{valor}} MT`

### 4. SMSForm
**Arquivo**: `clients/web-enterprise/src/components/forms/SMSForm.tsx`

#### Funcionalidades
- ✅ Envio individual de SMS
- ✅ Seleção de contatos existentes
- ✅ Uso de templates com variáveis
- ✅ Mensagens rápidas predefinidas
- ✅ Agendamento opcional
- ✅ Preview do SMS
- ✅ Cálculo de custo automático
- ✅ Suporte a SMS longos (múltiplos)
- ✅ Modo rápido para envios frequentes

#### Modos de Operação
```typescript
mode?: 'single' | 'quick'
```

#### Mensagens Rápidas
- "Obrigado pelo seu contacto. Entraremos em contacto em breve."
- "Confirmamos o seu agendamento para hoje às {{hora}}."
- "A sua encomenda foi processada com sucesso."
- "Lembrete: Reunião marcada para amanhã às {{hora}}."
- "Promoção especial! {{desconto}}% de desconto até {{data}}."

## Recursos Compartilhados

### Hook useZodForm
```typescript
const form = useZodForm({
  schema: ContactFormSchema,
  defaultValues: { ... },
  mode: 'onChange' // Validação em tempo real
});
```

### Utilitários de Formatação
```typescript
// Telefone moçambicano
PhoneFormatter.display(phone) // +258 XX XXX XXXX
PhoneFormatter.forSending(phone) // +258XXXXXXXXX

// Datas
DateFormatter.display(date) // DD/MM/YYYY HH:mm
DateFormatter.forInput(date) // YYYY-MM-DDTHH:mm

// Números/Moeda
NumberFormatter.currency(value) // 3,50 MT
```

### Validações Comuns

#### Telefone Moçambicano
```typescript
const phoneValidation = z.string()
  .refine((phone) => {
    const cleanPhone = phone.replace(/\D/g, '');
    const phoneDigits = cleanPhone.startsWith('258') 
      ? cleanPhone.slice(3) 
      : cleanPhone;
    return /^[8][0-9]{8}$/.test(phoneDigits);
  })
  .transform((phone) => `+258${phoneDigits}`);
```

#### Mensagem SMS
```typescript
const smsMessageValidation = z.string()
  .min(1, 'Mensagem não pode estar vazia')
  .max(160, 'SMS não pode exceder 160 caracteres');
```

#### Data Futura
```typescript
const futureDateValidation = z.date()
  .refine(date => date > new Date(), 'Data deve ser no futuro');
```

## Estados de Validação

### Visual Feedback
- ✅ **Verde**: Campo válido
- ⚠️ **Amarelo**: Aviso (ex: próximo do limite)
- ❌ **Vermelho**: Erro de validação
- 🔵 **Azul**: Informação adicional

### Status do Formulário
```typescript
{isDirty && (
  <div className={`p-3 rounded-md ${
    isValid 
      ? 'bg-green-50 text-green-700 border-green-200'
      : 'bg-yellow-50 text-yellow-700 border-yellow-200'
  }`}>
    {isValid ? (
      <CheckCircle /> Formulário válido
    ) : (
      <AlertCircle /> Corrija os erros
    )}
  </div>
)}
```

## Integração com Backend

### Transformação de Dados
Todos os formulários aplicam transformações antes do envio:

```typescript
const sanitizedData = {
  ...data,
  name: TextFormatter.titleCase(data.name.trim()),
  phone: PhoneFormatter.forSending(data.phone),
  email: data.email?.trim().toLowerCase(),
  tags: data.tags.filter(tag => tag.trim().length > 0)
};
```

### Tratamento de Erros
```typescript
try {
  await onSubmit(sanitizedData);
  toast.success('Operação realizada com sucesso!');
} catch (error) {
  toast.error('Erro ao salvar. Tente novamente.');
  console.error('Form submission error:', error);
}
```

## Personalização

### Temas e Estilos
Os formulários seguem o design system da interface enterprise:
- Cores: Azul corporativo (#1e40af)
- Componentes: shadcn/ui
- Ícones: Lucide React
- Notificações: Sonner

### Responsividade
```typescript
// Grid responsivo
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

// Layout móvel first
<div className="space-y-4 md:space-y-0 md:grid md:grid-cols-2 md:gap-4">
```

## Exemplos de Uso

### Formulário de Contato
```tsx
<ContactForm
  mode="create"
  onSubmit={async (data) => {
    await api.contacts.create(data);
  }}
  onCancel={() => navigate('/contacts')}
  isLoading={isSubmitting}
/>
```

### Formulário de Campanha
```tsx
<CampaignForm
  initialData={campaign}
  mode="edit"
  onSubmit={async (data) => {
    await api.campaigns.update(campaignId, data);
  }}
/>
```

### Formulário de SMS
```tsx
<SMSForm
  mode="quick"
  templates={templates}
  contacts={recentContacts}
  onSubmit={async (data) => {
    await api.sms.send(data);
  }}
/>
```

## Próximos Desenvolvimentos

1. **Formulário Multi-etapa**: Campanhas complexas
2. **Formulário em Massa**: Importação de contatos via CSV
3. **Formulário de Configurações**: Preferências do usuário
4. **Validação Offline**: Suporte a modo offline
5. **Auto-save**: Salvamento automático de rascunhos

Esta implementação garante uma experiência de usuário robusta com validação em tempo real, feedback visual claro e integração perfeita com o backend usando schemas Zod/Pydantic consistentes.
