// Frontend Validation Schemas using Zod
// TypeScript validation schemas for all client applications

import { z } from 'zod';

// ===== ENUMS =====

export const UserRoleEnum = z.enum([
  'super_admin',
  'admin', 
  'enterprise_user',
  'individual_user'
]);

export const MessageStatusEnum = z.enum([
  'pending',
  'sent',
  'delivered', 
  'failed',
  'cancelled'
]);

export const CampaignTypeEnum = z.enum([
  'promotional',
  'informational',
  'transactional',
  'support',
  'welcome',
  'reminder'
]);

export const CampaignStatusEnum = z.enum([
  'draft',
  'scheduled',
  'active',
  'paused',
  'completed',
  'cancelled'
]);

export const ContactStatusEnum = z.enum([
  'active',
  'inactive',
  'blocked'
]);

export const ApprovalStatusEnum = z.enum([
  'pending',
  'approved',
  'rejected'
]);

// ===== CUSTOM VALIDATIONS =====

// Mozambique phone number validation
const mozambiquePhoneRegex = /^(\+258|258)?[8][0-9]{8}$/;
export const phoneValidation = z.string()
  .min(9, 'Phone number too short')
  .max(20, 'Phone number too long')
  .refine((phone) => {
    const cleanPhone = phone.replace(/\D/g, '');
    const phoneDigits = cleanPhone.startsWith('258') 
      ? cleanPhone.slice(3) 
      : cleanPhone.startsWith('+258') 
        ? cleanPhone.slice(4)
        : cleanPhone;
    
    return /^[8][0-9]{8}$/.test(phoneDigits);
  }, {
    message: 'Invalid Mozambique phone number format. Must start with 8 and have 9 digits'
  })
  .transform((phone) => {
    const cleanPhone = phone.replace(/\D/g, '');
    const phoneDigits = cleanPhone.startsWith('258') 
      ? cleanPhone.slice(3) 
      : cleanPhone.startsWith('+258') 
        ? cleanPhone.slice(4)
        : cleanPhone;
    
    return `+258${phoneDigits}`;
  });

// Username validation
export const usernameValidation = z.string()
  .min(3, 'Username must be at least 3 characters')
  .max(50, 'Username must be less than 50 characters')
  .regex(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, underscores and hyphens')
  .transform(val => val.toLowerCase());

// Password validation
export const passwordValidation = z.string()
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password must be less than 128 characters')
  .refine((password) => /[A-Z]/.test(password), {
    message: 'Password must contain at least one uppercase letter'
  })
  .refine((password) => /[a-z]/.test(password), {
    message: 'Password must contain at least one lowercase letter'
  })
  .refine((password) => /\d/.test(password), {
    message: 'Password must contain at least one digit'
  })
  .refine((password) => /[!@#$%^&*(),.?":{}|<>]/.test(password), {
    message: 'Password must contain at least one special character'
  });

// SMS message validation
export const smsMessageValidation = z.string()
  .min(1, 'Message cannot be empty')
  .max(160, 'SMS message cannot exceed 160 characters');

// USSD code validation
export const ussdCodeValidation = z.string()
  .min(2, 'USSD code too short')
  .max(10, 'USSD code too long')
  .regex(/^\*[0-9#*]+\#$/, 'Invalid USSD code format. Must be like *123# or *123*1#');

// ===== USER SCHEMAS =====

export const UserBaseSchema = z.object({
  username: usernameValidation,
  email: z.string().email('Invalid email format'),
  full_name: z.string()
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name must be less than 100 characters'),
  is_active: z.boolean().default(true),
  role: UserRoleEnum.default('individual_user')
});

export const UserCreateSchema = UserBaseSchema.extend({
  password: passwordValidation,
  confirm_password: passwordValidation
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"]
});

export const UserUpdateSchema = UserBaseSchema.partial();

export const UserResponseSchema = UserBaseSchema.extend({
  id: z.number(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  last_login: z.string().datetime().nullable()
});

// ===== CONTACT SCHEMAS =====

export const ContactBaseSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters'),
  phone: phoneValidation,
  email: z.string().email('Invalid email format').optional(),
  company: z.string().max(100, 'Company name too long').optional(),
  position: z.string().max(100, 'Position too long').optional(),
  location: z.string().max(100, 'Location too long').optional(),
  tags: z.array(z.string()).default([]),
  groups: z.array(z.string()).default([]),
  notes: z.string().max(1000, 'Notes too long').optional(),
  custom_fields: z.record(z.string(), z.any()).default({})
});

export const ContactCreateSchema = ContactBaseSchema.extend({
  status: ContactStatusEnum.default('active')
});

export const ContactUpdateSchema = ContactBaseSchema.partial().extend({
  status: ContactStatusEnum.optional()
});

export const ContactResponseSchema = ContactBaseSchema.extend({
  id: z.number(),
  status: ContactStatusEnum,
  sms_sent: z.number().default(0),
  sms_received: z.number().default(0),
  last_contact: z.string().datetime().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  created_by: z.number()
});

// ===== CAMPAIGN SCHEMAS =====

export const CampaignBaseSchema = z.object({
  name: z.string()
    .min(3, 'Campaign name must be at least 3 characters')
    .max(100, 'Campaign name must be less than 100 characters'),
  description: z.string()
    .max(500, 'Description too long')
    .optional(),
  message: smsMessageValidation,
  type: CampaignTypeEnum,
  target_audience: z.string()
    .min(3, 'Target audience must be specified')
    .max(100, 'Target audience name too long'),
  budget: z.number()
    .positive('Budget must be positive')
    .max(1000000, 'Budget too large'),
  scheduled_at: z.string().datetime().optional()
}).refine((data) => {
  if (data.scheduled_at) {
    const scheduledDate = new Date(data.scheduled_at);
    return scheduledDate > new Date();
  }
  return true;
}, {
  message: 'Scheduled time must be in the future',
  path: ['scheduled_at']
});

export const CampaignCreateSchema = CampaignBaseSchema;

export const CampaignUpdateSchema = CampaignBaseSchema.partial().extend({
  status: CampaignStatusEnum.optional()
});

export const CampaignResponseSchema = CampaignBaseSchema.extend({
  id: z.number(),
  status: CampaignStatusEnum,
  approval_status: ApprovalStatusEnum,
  contacts_count: z.number().default(0),
  sent_count: z.number().default(0),
  delivered_count: z.number().default(0),
  failed_count: z.number().default(0),
  cost_per_sms: z.number().default(3.5),
  created_by: z.number(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  approver: z.number().nullable(),
  approved_at: z.string().datetime().nullable()
});

// ===== TEMPLATE SCHEMAS =====

export const TemplateBaseSchema = z.object({
  name: z.string()
    .min(3, 'Template name must be at least 3 characters')
    .max(100, 'Template name must be less than 100 characters'),
  description: z.string()
    .max(500, 'Description too long')
    .optional(),
  content: smsMessageValidation,
  category: CampaignTypeEnum,
  language: z.string()
    .regex(/^[a-z]{2}$/, 'Language must be a 2-letter code')
    .default('pt'),
  tags: z.array(z.string())
    .max(10, 'Maximum 10 tags allowed')
    .default([])
    .transform(tags => tags.map(tag => tag.toLowerCase().trim()).filter(Boolean)),
  is_active: z.boolean().default(true)
});

export const TemplateCreateSchema = TemplateBaseSchema;

export const TemplateUpdateSchema = TemplateBaseSchema.partial();

export const TemplateResponseSchema = TemplateBaseSchema.extend({
  id: z.number(),
  variables: z.array(z.string()).default([]),
  usage_count: z.number().default(0),
  is_favorite: z.boolean().default(false),
  character_count: z.number().default(0),
  estimated_cost: z.number().default(3.5),
  created_by: z.number(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  last_used: z.string().datetime().nullable()
});

// ===== SMS SCHEMAS =====

export const SMSBaseSchema = z.object({
  phone: phoneValidation,
  message: smsMessageValidation
});

export const SMSSendSchema = SMSBaseSchema.extend({
  scheduled_at: z.string().datetime().optional(),
  template_id: z.number().optional(),
  variables: z.record(z.string(), z.string()).default({})
});

export const SMSBulkSendSchema = z.object({
  phones: z.array(phoneValidation)
    .min(1, 'At least one phone number required')
    .max(1000, 'Maximum 1000 phone numbers allowed'),
  message: smsMessageValidation,
  scheduled_at: z.string().datetime().optional(),
  template_id: z.number().optional(),
  contact_groups: z.array(z.string()).default([])
}).transform(data => ({
  ...data,
  phones: [...new Set(data.phones)] // Remove duplicates
}));

export const SMSResponseSchema = SMSBaseSchema.extend({
  id: z.number(),
  status: MessageStatusEnum,
  sent_at: z.string().datetime().nullable(),
  delivered_at: z.string().datetime().nullable(),
  failed_reason: z.string().nullable(),
  cost: z.number().default(3.5),
  campaign_id: z.number().nullable(),
  created_by: z.number(),
  created_at: z.string().datetime()
});

// ===== USSD SCHEMAS =====

export const USSDSessionBaseSchema = z.object({
  phone: phoneValidation,
  code: ussdCodeValidation
});

export const USSDSessionCreateSchema = USSDSessionBaseSchema;

export const USSDSessionResponseSchema = USSDSessionBaseSchema.extend({
  id: z.number(),
  session_id: z.string(),
  step: z.number().default(0),
  is_active: z.boolean().default(true),
  response_data: z.record(z.string(), z.any()).default({}),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  ended_at: z.string().datetime().nullable()
});

// ===== SYSTEM SCHEMAS =====

export const SystemStatsResponseSchema = z.object({
  total_users: z.number(),
  total_contacts: z.number(),
  total_campaigns: z.number(),
  total_templates: z.number(),
  sms_sent_today: z.number(),
  sms_sent_month: z.number(),
  success_rate: z.number(),
  active_campaigns: z.number(),
  system_uptime: z.string(),
  modem_status: z.string(),
  last_backup: z.string().datetime().nullable()
});

export const APIResponseBaseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  data: z.any().optional(),
  errors: z.array(z.string()).optional(),
  timestamp: z.string().datetime()
});

// ===== AUTHENTICATION SCHEMAS =====

export const LoginRequestSchema = z.object({
  username: z.string().min(3, 'Username required'),
  password: z.string().min(1, 'Password required')
});

export const LoginResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string().default('bearer'),
  expires_in: z.number(),
  user: UserResponseSchema
});

export const TokenDataSchema = z.object({
  user_id: z.number(),
  username: z.string(),
  role: UserRoleEnum,
  exp: z.string().datetime()
});

// ===== BULK OPERATIONS SCHEMAS =====

export const BulkContactImportSchema = z.object({
  contacts: z.array(ContactCreateSchema)
    .min(1, 'At least one contact required')
    .max(1000, 'Maximum 1000 contacts allowed'),
  skip_duplicates: z.boolean().default(true),
  default_group: z.string().optional()
});

export const BulkOperationResponseSchema = z.object({
  total_processed: z.number(),
  successful: z.number(),
  failed: z.number(),
  errors: z.array(z.string()).default([]),
  created_ids: z.array(z.number()).default([])
});

// ===== PAGINATION SCHEMAS =====

export const PaginationParamsSchema = z.object({
  page: z.number().min(1).default(1),
  per_page: z.number().min(1).max(100).default(25),
  sort_by: z.string().optional(),
  sort_order: z.enum(['asc', 'desc']).default('desc')
});

export const PaginatedResponseSchema = z.object({
  items: z.array(z.any()),
  total: z.number(),
  page: z.number(),
  per_page: z.number(),
  pages: z.number(),
  has_next: z.boolean(),
  has_prev: z.boolean()
});

// ===== FORM VALIDATION SCHEMAS =====

// Campaign form validation for frontend
export const CampaignFormSchema = z.object({
  name: z.string().min(3, 'Nome deve ter pelo menos 3 caracteres'),
  description: z.string().optional(),
  message: z.string()
    .min(1, 'Mensagem é obrigatória')
    .max(160, 'Mensagem não pode exceder 160 caracteres'),
  type: CampaignTypeEnum,
  target_audience: z.string().min(1, 'Público-alvo é obrigatório'),
  budget: z.number()
    .positive('Orçamento deve ser positivo')
    .max(1000000, 'Orçamento muito alto'),
  scheduled_at: z.date().optional()
}).refine((data) => {
  if (data.scheduled_at) {
    return data.scheduled_at > new Date();
  }
  return true;
}, {
  message: 'Data agendada deve ser no futuro',
  path: ['scheduled_at']
});

// Contact form validation for frontend
export const ContactFormSchema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  phone: z.string()
    .min(9, 'Telefone muito curto')
    .refine((phone) => {
      const cleanPhone = phone.replace(/\D/g, '');
      const phoneDigits = cleanPhone.startsWith('258') 
        ? cleanPhone.slice(3) 
        : cleanPhone.startsWith('+258') 
          ? cleanPhone.slice(4)
          : cleanPhone;
      
      return /^[8][0-9]{8}$/.test(phoneDigits);
    }, {
      message: 'Formato de telefone inválido. Deve começar com 8 e ter 9 dígitos'
    }),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  company: z.string().optional(),
  position: z.string().optional(),
  location: z.string().optional(),
  tags: z.array(z.string()).default([]),
  groups: z.array(z.string()).default([]),
  notes: z.string().optional()
});

// Template form validation for frontend
export const TemplateFormSchema = z.object({
  name: z.string().min(3, 'Nome deve ter pelo menos 3 caracteres'),
  description: z.string().optional(),
  content: z.string()
    .min(1, 'Conteúdo é obrigatório')
    .max(160, 'Conteúdo não pode exceder 160 caracteres'),
  category: CampaignTypeEnum,
  language: z.string().default('pt'),
  tags: z.array(z.string()).default([]),
  is_active: z.boolean().default(true)
});

// SMS send form validation for frontend
export const SMSFormSchema = z.object({
  phone: z.string()
    .min(9, 'Telefone muito curto')
    .refine((phone) => {
      const cleanPhone = phone.replace(/\D/g, '');
      const phoneDigits = cleanPhone.startsWith('258') 
        ? cleanPhone.slice(3) 
        : cleanPhone.startsWith('+258') 
          ? cleanPhone.slice(4)
          : cleanPhone;
      
      return /^[8][0-9]{8}$/.test(phoneDigits);
    }, {
      message: 'Formato de telefone inválido'
    }),
  message: z.string()
    .min(1, 'Mensagem é obrigatória')
    .max(160, 'Mensagem não pode exceder 160 caracteres'),
  template_id: z.number().optional(),
  scheduled_at: z.date().optional()
});

// ===== TYPE EXPORTS =====

export type UserRole = z.infer<typeof UserRoleEnum>;
export type MessageStatus = z.infer<typeof MessageStatusEnum>;
export type CampaignType = z.infer<typeof CampaignTypeEnum>;
export type CampaignStatus = z.infer<typeof CampaignStatusEnum>;
export type ContactStatus = z.infer<typeof ContactStatusEnum>;
export type ApprovalStatus = z.infer<typeof ApprovalStatusEnum>;

export type UserBase = z.infer<typeof UserBaseSchema>;
export type UserCreate = z.infer<typeof UserCreateSchema>;
export type UserUpdate = z.infer<typeof UserUpdateSchema>;
export type UserResponse = z.infer<typeof UserResponseSchema>;

export type ContactBase = z.infer<typeof ContactBaseSchema>;
export type ContactCreate = z.infer<typeof ContactCreateSchema>;
export type ContactUpdate = z.infer<typeof ContactUpdateSchema>;
export type ContactResponse = z.infer<typeof ContactResponseSchema>;

export type CampaignBase = z.infer<typeof CampaignBaseSchema>;
export type CampaignCreate = z.infer<typeof CampaignCreateSchema>;
export type CampaignUpdate = z.infer<typeof CampaignUpdateSchema>;
export type CampaignResponse = z.infer<typeof CampaignResponseSchema>;

export type TemplateBase = z.infer<typeof TemplateBaseSchema>;
export type TemplateCreate = z.infer<typeof TemplateCreateSchema>;
export type TemplateUpdate = z.infer<typeof TemplateUpdateSchema>;
export type TemplateResponse = z.infer<typeof TemplateResponseSchema>;

export type SMSBase = z.infer<typeof SMSBaseSchema>;
export type SMSSend = z.infer<typeof SMSSendSchema>;
export type SMSBulkSend = z.infer<typeof SMSBulkSendSchema>;
export type SMSResponse = z.infer<typeof SMSResponseSchema>;

export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type LoginResponse = z.infer<typeof LoginResponseSchema>;

export type PaginationParams = z.infer<typeof PaginationParamsSchema>;
export type PaginatedResponse<T> = Omit<z.infer<typeof PaginatedResponseSchema>, 'items'> & {
  items: T[];
};

// Form types for frontend
export type CampaignForm = z.infer<typeof CampaignFormSchema>;
export type ContactForm = z.infer<typeof ContactFormSchema>;
export type TemplateForm = z.infer<typeof TemplateFormSchema>;
export type SMSForm = z.infer<typeof SMSFormSchema>;
