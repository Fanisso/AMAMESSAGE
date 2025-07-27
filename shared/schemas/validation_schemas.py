# Backend Validation Schemas
# Using Pydantic for Python backend validation (equivalent to Zod for TypeScript)

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum
import re

# ===== ENUMS =====

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ENTERPRISE_USER = "enterprise_user"
    INDIVIDUAL_USER = "individual_user"

class MessageStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CampaignType(str, Enum):
    PROMOTIONAL = "promotional"
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    SUPPORT = "support"
    WELCOME = "welcome"
    REMINDER = "reminder"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ContactStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# ===== BASE SCHEMAS =====

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ===== USER SCHEMAS =====

class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    is_active: bool = True
    role: UserRole = UserRole.INDIVIDUAL_USER

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v.lower()

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseSchema):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

# ===== CONTACT SCHEMAS =====

class ContactBase(BaseSchema):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=9, max_length=20)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=1000)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

    @validator('phone')
    def validate_phone(cls, v):
        # Remove all non-digit characters
        phone_digits = re.sub(r'\D', '', v)
        
        # Mozambique phone validation
        if phone_digits.startswith('258'):
            phone_digits = phone_digits[3:]
        elif phone_digits.startswith('+258'):
            phone_digits = phone_digits[4:]
        
        if not re.match(r'^[8][0-9]{8}$', phone_digits):
            raise ValueError('Invalid Mozambique phone number format')
        
        return f"+258{phone_digits}"

class ContactCreate(ContactBase):
    status: ContactStatus = ContactStatus.ACTIVE

class ContactUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=9, max_length=20)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=1000)
    custom_fields: Optional[Dict[str, Any]] = None
    status: Optional[ContactStatus] = None

class ContactResponse(ContactBase):
    id: int
    status: ContactStatus
    sms_sent: int = 0
    sms_received: int = 0
    last_contact: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: int

# ===== CAMPAIGN SCHEMAS =====

class CampaignBase(BaseSchema):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    message: str = Field(..., min_length=1, max_length=160)
    type: CampaignType
    target_audience: str = Field(..., min_length=3, max_length=100)
    budget: float = Field(..., gt=0, le=1000000)
    scheduled_at: Optional[datetime] = None

    @validator('message')
    def validate_message_length(cls, v):
        if len(v) > 160:
            raise ValueError('SMS message cannot exceed 160 characters')
        return v

    @validator('scheduled_at')
    def validate_schedule_time(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Scheduled time must be in the future')
        return v

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = Field(None, min_length=1, max_length=160)
    type: Optional[CampaignType] = None
    target_audience: Optional[str] = Field(None, min_length=3, max_length=100)
    budget: Optional[float] = Field(None, gt=0, le=1000000)
    scheduled_at: Optional[datetime] = None
    status: Optional[CampaignStatus] = None

class CampaignResponse(CampaignBase):
    id: int
    status: CampaignStatus
    approval_status: ApprovalStatus
    contacts_count: int = 0
    sent_count: int = 0
    delivered_count: int = 0
    failed_count: int = 0
    cost_per_sms: float = 3.5
    created_by: int
    created_at: datetime
    updated_at: datetime
    approver: Optional[int] = None
    approved_at: Optional[datetime] = None

# ===== TEMPLATE SCHEMAS =====

class TemplateBase(BaseSchema):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1, max_length=160)
    category: CampaignType
    language: str = Field(default="pt", regex=r'^[a-z]{2}$')
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True

    @validator('content')
    def validate_template_content(cls, v):
        if len(v) > 160:
            raise ValueError('Template content cannot exceed 160 characters')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return [tag.lower().strip() for tag in v if tag.strip()]

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=1, max_length=160)
    category: Optional[CampaignType] = None
    language: Optional[str] = Field(None, regex=r'^[a-z]{2}$')
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class TemplateResponse(TemplateBase):
    id: int
    variables: List[str] = Field(default_factory=list)
    usage_count: int = 0
    is_favorite: bool = False
    character_count: int = 0
    estimated_cost: float = 3.5
    created_by: int
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime] = None

# ===== SMS SCHEMAS =====

class SMSBase(BaseSchema):
    phone: str = Field(..., min_length=9, max_length=20)
    message: str = Field(..., min_length=1, max_length=160)
    
    @validator('phone')
    def validate_phone(cls, v):
        phone_digits = re.sub(r'\D', '', v)
        if phone_digits.startswith('258'):
            phone_digits = phone_digits[3:]
        elif phone_digits.startswith('+258'):
            phone_digits = phone_digits[4:]
        
        if not re.match(r'^[8][0-9]{8}$', phone_digits):
            raise ValueError('Invalid Mozambique phone number format')
        
        return f"+258{phone_digits}"

class SMSSend(SMSBase):
    scheduled_at: Optional[datetime] = None
    template_id: Optional[int] = None
    variables: Optional[Dict[str, str]] = Field(default_factory=dict)

class SMSBulkSend(BaseSchema):
    phones: List[str] = Field(..., min_items=1, max_items=1000)
    message: str = Field(..., min_length=1, max_length=160)
    scheduled_at: Optional[datetime] = None
    template_id: Optional[int] = None
    contact_groups: Optional[List[str]] = Field(default_factory=list)

    @validator('phones')
    def validate_phones(cls, v):
        validated_phones = []
        for phone in v:
            phone_digits = re.sub(r'\D', '', phone)
            if phone_digits.startswith('258'):
                phone_digits = phone_digits[3:]
            elif phone_digits.startswith('+258'):
                phone_digits = phone_digits[4:]
            
            if not re.match(r'^[8][0-9]{8}$', phone_digits):
                raise ValueError(f'Invalid phone number format: {phone}')
            
            validated_phones.append(f"+258{phone_digits}")
        
        return list(set(validated_phones))  # Remove duplicates

class SMSResponse(SMSBase):
    id: int
    status: MessageStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    cost: float = 3.5
    campaign_id: Optional[int] = None
    created_by: int
    created_at: datetime

# ===== USSD SCHEMAS =====

class USSDSessionBase(BaseSchema):
    phone: str = Field(..., min_length=9, max_length=20)
    code: str = Field(..., min_length=2, max_length=10)
    
    @validator('phone')
    def validate_phone(cls, v):
        phone_digits = re.sub(r'\D', '', v)
        if phone_digits.startswith('258'):
            phone_digits = phone_digits[3:]
        elif phone_digits.startswith('+258'):
            phone_digits = phone_digits[4:]
        
        if not re.match(r'^[8][0-9]{8}$', phone_digits):
            raise ValueError('Invalid Mozambique phone number format')
        
        return f"+258{phone_digits}"

    @validator('code')
    def validate_ussd_code(cls, v):
        if not re.match(r'^\*[0-9#*]+\#$', v):
            raise ValueError('Invalid USSD code format. Must be like *123# or *123*1#')
        return v

class USSDSessionCreate(USSDSessionBase):
    pass

class USSDSessionResponse(USSDSessionBase):
    id: int
    session_id: str
    step: int = 0
    is_active: bool = True
    response_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime] = None

# ===== SYSTEM SCHEMAS =====

class SystemStatsResponse(BaseSchema):
    total_users: int
    total_contacts: int
    total_campaigns: int
    total_templates: int
    sms_sent_today: int
    sms_sent_month: int
    success_rate: float
    active_campaigns: int
    system_uptime: str
    modem_status: str
    last_backup: Optional[datetime] = None

class APIResponseBase(BaseSchema):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ===== AUTHENTICATION SCHEMAS =====

class LoginRequest(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

class LoginResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseSchema):
    user_id: int
    username: str
    role: UserRole
    exp: datetime

# ===== BULK OPERATIONS SCHEMAS =====

class BulkContactImport(BaseSchema):
    contacts: List[ContactCreate] = Field(..., min_items=1, max_items=1000)
    skip_duplicates: bool = True
    default_group: Optional[str] = None

class BulkOperationResponse(BaseSchema):
    total_processed: int
    successful: int
    failed: int
    errors: List[str] = Field(default_factory=list)
    created_ids: List[int] = Field(default_factory=list)

# ===== PAGINATION SCHEMAS =====

class PaginationParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Literal["asc", "desc"] = "desc"

class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool
