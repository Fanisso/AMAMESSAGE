# Validation Schemas Documentation

Este documento descreve os schemas de validação implementados no sistema AMAMESSAGE usando Pydantic (Python) e Zod (TypeScript).

## Estrutura

### Backend (Python/Pydantic)
- **Arquivo**: `shared/schemas/validation_schemas.py`
- **Biblioteca**: Pydantic v2
- **Funcionalidade**: Validação de dados no backend API

### Frontend (TypeScript/Zod)
- **Arquivo**: `shared/schemas/zod-schemas.ts`  
- **Biblioteca**: Zod
- **Funcionalidade**: Validação de dados no frontend e tipagem TypeScript

## Schemas Implementados

### 1. Validações Personalizadas

#### Telefone (Moçambique)
```python
# Python (Pydantic)
@field_validator('phone')
def validate_phone(cls, v):
    # Formato: +258XXXXXXXXX (9 dígitos começando com 8)
```

```typescript
// TypeScript (Zod)
const phoneValidation = z.string()
  .refine((phone) => mozambiquePhoneRegex.test(phone))
  .transform((phone) => `+258${phoneDigits}`);
```

#### Senha Forte
- Mínimo 8 caracteres
- Pelo menos 1 maiúscula
- Pelo menos 1 minúscula  
- Pelo menos 1 dígito
- Pelo menos 1 caractere especial

#### Mensagem SMS
- Máximo 160 caracteres
- Não pode estar vazia

#### Código USSD
- Formato: `*123#` ou `*123*1#`
- Entre 2-10 caracteres

### 2. Schemas de Usuário

#### UserBaseSchema
```typescript
{
  username: string (3-50 chars, alfanumérico)
  email: string (formato email válido)
  full_name: string (2-100 chars)
  is_active: boolean (default: true)
  role: 'super_admin' | 'admin' | 'enterprise_user' | 'individual_user'
}
```

#### UserCreateSchema
- Extends UserBaseSchema
- Adiciona: `password` e `confirm_password`
- Validação: senhas devem coincidir

#### UserUpdateSchema
- Todos os campos opcionais do UserBaseSchema

### 3. Schemas de Contato

#### ContactBaseSchema
```typescript
{
  name: string (2-100 chars)
  phone: string (validação Moçambique)
  email?: string (formato email)
  company?: string (max 100 chars)
  position?: string (max 100 chars)
  location?: string (max 100 chars)
  tags: string[] (default: [])
  groups: string[] (default: [])
  notes?: string (max 1000 chars)
  custom_fields: Record<string, any> (default: {})
}
```

### 4. Schemas de Campanha

#### CampaignBaseSchema
```typescript
{
  name: string (3-100 chars)
  description?: string (max 500 chars)
  message: string (1-160 chars)
  type: 'promotional' | 'informational' | 'transactional' | 'support' | 'welcome' | 'reminder'
  target_audience: string (3-100 chars)
  budget: number (positivo, max 1000000)
  scheduled_at?: datetime (deve ser futuro)
}
```

### 5. Schemas de Template

#### TemplateBaseSchema
```typescript
{
  name: string (3-100 chars)
  description?: string (max 500 chars)
  content: string (1-160 chars)
  category: CampaignType
  language: string (código 2 letras, default: 'pt')
  tags: string[] (max 10, transformadas para lowercase)
  is_active: boolean (default: true)
}
```

### 6. Schemas de SMS

#### SMSSendSchema
```typescript
{
  phone: string (validação Moçambique)
  message: string (1-160 chars)
  scheduled_at?: datetime
  template_id?: number
  variables: Record<string, string> (default: {})
}
```

#### SMSBulkSendSchema
```typescript
{
  phones: string[] (1-1000 números, remove duplicatas)
  message: string (1-160 chars)
  scheduled_at?: datetime
  template_id?: number
  contact_groups: string[] (default: [])
}
```

### 7. Schemas de Autenticação

#### LoginRequestSchema
```typescript
{
  username: string (min 3 chars)
  password: string (obrigatório)
}
```

#### LoginResponseSchema
```typescript
{
  access_token: string
  token_type: string (default: 'bearer')
  expires_in: number
  user: UserResponse
}
```

### 8. Schemas de Sistema

#### SystemStatsResponseSchema
```typescript
{
  total_users: number
  total_contacts: number
  total_campaigns: number
  total_templates: number
  sms_sent_today: number
  sms_sent_month: number
  success_rate: number
  active_campaigns: number
  system_uptime: string
  modem_status: string
  last_backup?: datetime
}
```

### 9. Schemas de Paginação

#### PaginationParamsSchema
```typescript
{
  page: number (min 1, default: 1)
  per_page: number (1-100, default: 25)
  sort_by?: string
  sort_order: 'asc' | 'desc' (default: 'desc')
}
```

#### PaginatedResponseSchema
```typescript
{
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
  has_next: boolean
  has_prev: boolean
}
```

### 10. Schemas para Formulários (Frontend)

Schemas específicos para validação de formulários com mensagens em português:

- **CampaignFormSchema**: Validação de criação de campanhas
- **ContactFormSchema**: Validação de criação de contatos
- **TemplateFormSchema**: Validação de criação de templates
- **SMSFormSchema**: Validação de envio de SMS

## Enums Disponíveis

```typescript
// Roles de usuário
UserRoleEnum: 'super_admin' | 'admin' | 'enterprise_user' | 'individual_user'

// Status de mensagem
MessageStatusEnum: 'pending' | 'sent' | 'delivered' | 'failed' | 'cancelled'

// Tipos de campanha
CampaignTypeEnum: 'promotional' | 'informational' | 'transactional' | 'support' | 'welcome' | 'reminder'

// Status de campanha
CampaignStatusEnum: 'draft' | 'scheduled' | 'active' | 'paused' | 'completed' | 'cancelled'

// Status de contato
ContactStatusEnum: 'active' | 'inactive' | 'blocked'

// Status de aprovação
ApprovalStatusEnum: 'pending' | 'approved' | 'rejected'
```

## Transformações Automáticas

### Telefone
- Remove caracteres não numéricos
- Adiciona prefixo +258
- Valida formato moçambicano

### Username
- Converte para lowercase
- Remove espaços

### Tags
- Converte para lowercase
- Remove espaços em branco
- Remove duplicatas
- Filtra strings vazias

## Validações de Negócio

### Horário Agendado
- Deve ser no futuro
- Aplicado em campanhas e SMS

### Orçamento
- Deve ser positivo
- Máximo de 1.000.000 MT

### Telefones em Lote
- Máximo 1000 números
- Remove duplicatas automaticamente

### Mensagens SMS
- Máximo 160 caracteres (padrão SMS)
- Não pode estar vazia

## Uso nos Projetos

### Backend (FastAPI)
```python
from shared.schemas.validation_schemas import UserCreateSchema

@app.post("/users/")
async def create_user(user_data: UserCreateSchema):
    # Dados já validados pelo Pydantic
    pass
```

### Frontend (React/TypeScript)
```typescript
import { CampaignFormSchema, type CampaignForm } from '@/shared/schemas/zod-schemas';

const formData = CampaignFormSchema.parse(rawFormData);
// ou
const result = CampaignFormSchema.safeParse(rawFormData);
if (result.success) {
  const validData: CampaignForm = result.data;
}
```

## Mensagens de Erro

As mensagens de erro são contextualizadas:
- **Backend**: Em inglês para logs e APIs
- **Frontend**: Em português para formulários de usuário

## Consistência entre Backend e Frontend

Os schemas Pydantic e Zod são mantidos sincronizados para garantir:
- Mesmas regras de validação
- Mesmos tipos de dados
- Mesma lógica de negócio
- Transformações consistentes

Esta documentação deve ser atualizada sempre que novos schemas forem adicionados ou modificados.
