// Utilitários para Formatação e Transformação de Dados
// Funções auxiliares para trabalhar com dados validados

// ===== FORMATAÇÃO DE TELEFONE =====

export class PhoneFormatter {
  // Limpar telefone removendo caracteres não numéricos
  static clean(phone: string): string {
    return phone.replace(/\D/g, '');
  }

  // Formatar telefone para exibição (+258 XX XXX XXXX)
  static display(phone: string): string {
    const cleaned = this.clean(phone);
    
    // Se já tem código do país
    if (cleaned.startsWith('258')) {
      const number = cleaned.slice(3);
      return `+258 ${number.slice(0, 2)} ${number.slice(2, 5)} ${number.slice(5)}`;
    }
    
    // Se começa com 8 (formato local)
    if (cleaned.startsWith('8') && cleaned.length === 9) {
      return `+258 ${cleaned.slice(0, 2)} ${cleaned.slice(2, 5)} ${cleaned.slice(5)}`;
    }
    
    return phone; // Retorna original se não conseguir formatar
  }

  // Formatar para envio (sempre +258XXXXXXXXX)
  static forSending(phone: string): string {
    const cleaned = this.clean(phone);
    
    // Se já tem código do país
    if (cleaned.startsWith('258')) {
      return `+${cleaned}`;
    }
    
    // Se começa com 8 (formato local)
    if (cleaned.startsWith('8') && cleaned.length === 9) {
      return `+258${cleaned}`;
    }
    
    // Se tem + no início mas sem código
    if (phone.startsWith('+')) {
      return phone;
    }
    
    throw new Error('Invalid phone number format');
  }

  // Validar formato moçambicano
  static isValid(phone: string): boolean {
    const cleaned = this.clean(phone);
    
    // Com código do país: 258XXXXXXXXX
    if (cleaned.startsWith('258') && cleaned.length === 12) {
      const localNumber = cleaned.slice(3);
      return localNumber.startsWith('8') && localNumber.length === 9;
    }
    
    // Formato local: XXXXXXXXX
    if (cleaned.length === 9) {
      return cleaned.startsWith('8');
    }
    
    return false;
  }

  // Extrair operadora baseado no número
  static getOperator(phone: string): string {
    const cleaned = this.clean(phone);
    const localNumber = cleaned.startsWith('258') ? cleaned.slice(3) : cleaned;
    
    if (localNumber.startsWith('82') || localNumber.startsWith('83')) {
      return 'Vodacom';
    } else if (localNumber.startsWith('84') || localNumber.startsWith('85')) {
      return 'Tmcel';
    } else if (localNumber.startsWith('86') || localNumber.startsWith('87')) {
      return 'Movitel';
    }
    
    return 'Unknown';
  }
}

// ===== FORMATAÇÃO DE DATAS =====

export class DateFormatter {
  // Formatar data para exibição (DD/MM/YYYY HH:mm)
  static display(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    
    return d.toLocaleDateString('pt-MZ', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // Formatar apenas data (DD/MM/YYYY)
  static dateOnly(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    
    return d.toLocaleDateString('pt-MZ', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  // Formatar apenas hora (HH:mm)
  static timeOnly(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    
    return d.toLocaleTimeString('pt-MZ', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // Formatar data relativa (há 2 horas, ontem, etc.)
  static relative(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) {
      return 'Agora mesmo';
    } else if (diffMinutes < 60) {
      return `Há ${diffMinutes} minuto${diffMinutes !== 1 ? 's' : ''}`;
    } else if (diffHours < 24) {
      return `Há ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
    } else if (diffDays < 7) {
      return `Há ${diffDays} dia${diffDays !== 1 ? 's' : ''}`;
    } else {
      return this.dateOnly(d);
    }
  }

  // Formatar para input datetime-local
  static forInput(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    
    return d.toISOString().slice(0, 16);
  }

  // Verificar se data é hoje
  static isToday(date: Date | string): boolean {
    const d = typeof date === 'string' ? new Date(date) : date;
    const today = new Date();
    
    return d.toDateString() === today.toDateString();
  }

  // Verificar se data é esta semana
  static isThisWeek(date: Date | string): boolean {
    const d = typeof date === 'string' ? new Date(date) : date;
    const today = new Date();
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - today.getDay());
    weekStart.setHours(0, 0, 0, 0);
    
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);
    weekEnd.setHours(23, 59, 59, 999);
    
    return d >= weekStart && d <= weekEnd;
  }
}

// ===== FORMATAÇÃO DE NÚMEROS =====

export class NumberFormatter {
  // Formatar moeda (Metical)
  static currency(amount: number): string {
    return new Intl.NumberFormat('pt-MZ', {
      style: 'currency',
      currency: 'MZN',
      minimumFractionDigits: 2
    }).format(amount);
  }

  // Formatar percentagem
  static percentage(value: number, decimals: number = 1): string {
    return `${value.toFixed(decimals)}%`;
  }

  // Formatar número com separadores
  static number(value: number): string {
    return new Intl.NumberFormat('pt-MZ').format(value);
  }

  // Formatar bytes para tamanho de arquivo
  static fileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  }

  // Abreviar números grandes (1K, 1M, etc.)
  static abbreviate(value: number): string {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    
    return value.toString();
  }
}

// ===== FORMATAÇÃO DE TEXTO =====

export class TextFormatter {
  // Truncar texto com reticências
  static truncate(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return `${text.slice(0, maxLength - 3)}...`;
  }

  // Capitalizar primeira letra
  static capitalize(text: string): string {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  }

  // Capitalizar cada palavra
  static titleCase(text: string): string {
    return text
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  // Formatar para slug (URL-friendly)
  static slug(text: string): string {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove acentos
      .replace(/[^a-z0-9 ]/g, '') // Remove caracteres especiais
      .replace(/\s+/g, '-') // Substitui espaços por hífens
      .replace(/-+/g, '-') // Remove hífens duplicados
      .trim();
  }

  // Remover HTML tags
  static stripHtml(html: string): string {
    return html.replace(/<[^>]*>/g, '');
  }

  // Extrair iniciais do nome
  static initials(name: string): string {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }
}

// ===== TRANSFORMAÇÕES DE DADOS =====

export class DataTransformer {
  // Converter array para opções de select
  static toSelectOptions<T>(
    items: T[],
    labelKey: keyof T,
    valueKey: keyof T
  ): Array<{ label: string; value: any }> {
    return items.map(item => ({
      label: String(item[labelKey]),
      value: item[valueKey]
    }));
  }

  // Agrupar array por propriedade
  static groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
    return array.reduce((groups, item) => {
      const groupKey = String(item[key]);
      
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      
      groups[groupKey].push(item);
      return groups;
    }, {} as Record<string, T[]>);
  }

  // Contar ocorrências por propriedade
  static countBy<T>(array: T[], key: keyof T): Record<string, number> {
    return array.reduce((counts, item) => {
      const countKey = String(item[key]);
      counts[countKey] = (counts[countKey] || 0) + 1;
      return counts;
    }, {} as Record<string, number>);
  }

  // Converter objeto flat para nested
  static unflatten(obj: Record<string, any>): Record<string, any> {
    const result: Record<string, any> = {};
    
    Object.entries(obj).forEach(([key, value]) => {
      const keys = key.split('.');
      let current = result;
      
      keys.forEach((k, index) => {
        if (index === keys.length - 1) {
          current[k] = value;
        } else {
          if (!current[k] || typeof current[k] !== 'object') {
            current[k] = {};
          }
          current = current[k];
        }
      });
    });
    
    return result;
  }

  // Converter nested object para flat
  static flatten(obj: Record<string, any>, prefix = ''): Record<string, any> {
    const result: Record<string, any> = {};
    
    Object.entries(obj).forEach(([key, value]) => {
      const newKey = prefix ? `${prefix}.${key}` : key;
      
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        Object.assign(result, this.flatten(value, newKey));
      } else {
        result[newKey] = value;
      }
    });
    
    return result;
  }

  // Remover propriedades com valores falsy
  static compact<T extends Record<string, any>>(obj: T): Partial<T> {
    const result: Partial<T> = {};
    
    Object.entries(obj).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        result[key as keyof T] = value;
      }
    });
    
    return result;
  }
}

// ===== VALIDAÇÃO DE DADOS =====

export class DataValidator {
  // Verificar se string é JSON válido
  static isValidJson(str: string): boolean {
    try {
      JSON.parse(str);
      return true;
    } catch {
      return false;
    }
  }

  // Verificar se URL é válida
  static isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  // Verificar se email é válido (básico)
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Verificar força da senha
  static getPasswordStrength(password: string): {
    score: number;
    feedback: string[];
    isStrong: boolean;
  } {
    const feedback: string[] = [];
    let score = 0;

    if (password.length >= 8) {
      score += 1;
    } else {
      feedback.push('Deve ter pelo menos 8 caracteres');
    }

    if (/[a-z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Deve conter letras minúsculas');
    }

    if (/[A-Z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Deve conter letras maiúsculas');
    }

    if (/\d/.test(password)) {
      score += 1;
    } else {
      feedback.push('Deve conter números');
    }

    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Deve conter caracteres especiais');
    }

    return {
      score,
      feedback,
      isStrong: score >= 4
    };
  }

  // Verificar se CPF é válido (adaptado para Moçambique - BI)
  static isValidBI(bi: string): boolean {
    // Formato básico para BI moçambicano: 12 dígitos + 1 letra
    const biRegex = /^\d{12}[A-Z]$/;
    return biRegex.test(bi.replace(/\s/g, '').toUpperCase());
  }
}

// ===== UTILITÁRIOS DE ARQUIVO =====

export class FileUtils {
  // Obter extensão do arquivo
  static getExtension(filename: string): string {
    return filename.split('.').pop()?.toLowerCase() || '';
  }

  // Verificar se arquivo é imagem
  static isImage(filename: string): boolean {
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
    return imageExtensions.includes(this.getExtension(filename));
  }

  // Verificar se arquivo é documento
  static isDocument(filename: string): boolean {
    const docExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'];
    return docExtensions.includes(this.getExtension(filename));
  }

  // Gerar nome único para arquivo
  static generateUniqueFilename(filename: string): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    const extension = this.getExtension(filename);
    const baseName = filename.replace(`.${extension}`, '');
    
    return `${baseName}-${timestamp}-${random}.${extension}`;
  }

  // Converter base64 para blob
  static base64ToBlob(base64: string, mimeType: string): Blob {
    const byteCharacters = atob(base64.split(',')[1]);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }
}

// ===== CONSTANTS =====

export const FORMAT_CONSTANTS = {
  PHONE_DISPLAY_REGEX: /(\+258)(\d{2})(\d{3})(\d{4})/,
  SMS_MAX_LENGTH: 160,
  MOZAMBIQUE_PHONE_LENGTH: 9,
  COUNTRY_CODE: '+258',
  DATE_FORMAT: 'DD/MM/YYYY',
  DATETIME_FORMAT: 'DD/MM/YYYY HH:mm',
  CURRENCY_SYMBOL: 'MT',
  OPERATORS: {
    VODACOM: ['82', '83'],
    TMCEL: ['84', '85'],
    MOVITEL: ['86', '87']
  }
} as const;
