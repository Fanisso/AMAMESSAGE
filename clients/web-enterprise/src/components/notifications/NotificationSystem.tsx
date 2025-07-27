// Sistema de Notificações em Tempo Real
// Componentes para toasts, alertas e notificações push

import React, { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { toast, Toaster, ExternalToast } from 'sonner';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  X,
  Bell,
  BellRing,
  Volume2,
  VolumeX,
  Settings,
  Trash2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger
} from '@/components/ui/sheet';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { formatDistance } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useNotifications, useMarkNotificationAsRead, useDeleteNotification } from '@/hooks/api-hooks';

// ===== TIPOS =====

interface NotificationType {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  category: 'sms' | 'campaign' | 'system' | 'user' | 'billing';
  is_read: boolean;
  created_at: string;
  action_url?: string;
  action_label?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  metadata?: {
    sms_id?: number;
    campaign_id?: number;
    contact_id?: number;
    [key: string]: any;
  };
}

interface NotificationSettings {
  sound_enabled: boolean;
  browser_notifications: boolean;
  email_notifications: boolean;
  sms_notifications: boolean;
  categories: {
    sms: boolean;
    campaign: boolean;
    system: boolean;
    user: boolean;
    billing: boolean;
  };
  quiet_hours: {
    enabled: boolean;
    start: string;
    end: string;
  };
}

interface NotificationContextType {
  notifications: NotificationType[];
  unreadCount: number;
  settings: NotificationSettings;
  showNotification: (notification: Omit<NotificationType, 'id' | 'created_at' | 'is_read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  deleteNotification: (id: string) => void;
  updateSettings: (settings: Partial<NotificationSettings>) => void;
  requestPermission: () => Promise<boolean>;
}

// ===== CONTEXT =====

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function useNotificationSystem() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotificationSystem deve ser usado dentro de NotificationProvider');
  }
  return context;
}

// ===== FUNÇÕES DE TOAST CUSTOMIZADAS =====

export const showToast = {
  success: (message: string, options?: ExternalToast) => {
    toast.success(message, {
      icon: <CheckCircle className="h-4 w-4" />,
      className: 'bg-green-50 border-green-200 text-green-800',
      ...options
    });
  },

  error: (message: string, options?: ExternalToast) => {
    toast.error(message, {
      icon: <XCircle className="h-4 w-4" />,
      className: 'bg-red-50 border-red-200 text-red-800',
      ...options
    });
  },

  warning: (message: string, options?: ExternalToast) => {
    toast.warning(message, {
      icon: <AlertCircle className="h-4 w-4" />,
      className: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      ...options
    });
  },

  info: (message: string, options?: ExternalToast) => {
    toast.info(message, {
      icon: <Info className="h-4 w-4" />,
      className: 'bg-blue-50 border-blue-200 text-blue-800',
      ...options
    });
  },

  sms: (message: string, count?: number) => {
    toast.success(`SMS ${count ? `(${count})` : ''} ${message}`, {
      icon: <Bell className="h-4 w-4" />,
      className: 'bg-green-50 border-green-200 text-green-800',
      action: {
        label: 'Ver Detalhes',
        onClick: () => window.open('/sms/history', '_blank')
      }
    });
  },

  campaign: (message: string, campaignName?: string) => {
    toast.info(`Campanha ${campaignName ? `"${campaignName}"` : ''}: ${message}`, {
      icon: <BellRing className="h-4 w-4" />,
      className: 'bg-blue-50 border-blue-200 text-blue-800',
      action: {
        label: 'Ver Campanha',
        onClick: () => window.open('/campaigns', '_blank')
      }
    });
  },

  system: (message: string, isError = false) => {
    const toastFn = isError ? toast.error : toast.info;
    toastFn(`Sistema: ${message}`, {
      icon: <AlertCircle className="h-4 w-4" />,
      className: isError 
        ? 'bg-red-50 border-red-200 text-red-800'
        : 'bg-gray-50 border-gray-200 text-gray-800'
    });
  }
};

// ===== PROVIDER DE NOTIFICAÇÕES =====

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<NotificationSettings>({
    sound_enabled: true,
    browser_notifications: false,
    email_notifications: true,
    sms_notifications: false,
    categories: {
      sms: true,
      campaign: true,
      system: true,
      user: true,
      billing: true
    },
    quiet_hours: {
      enabled: false,
      start: '22:00',
      end: '08:00'
    }
  });

  // API hooks
  const { data: apiNotifications, refetch } = useNotifications();
  const markAsReadMutation = useMarkNotificationAsRead();
  const deleteNotificationMutation = useDeleteNotification();

  const notifications = apiNotifications?.items || [];
  const unreadCount = notifications.filter(n => !n.is_read).length;

  // ===== FUNÇÕES =====

  const playNotificationSound = useCallback(() => {
    if (settings.sound_enabled && !isQuietTime()) {
      // Criar um som de notificação simples
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.value = 0.1;
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.3);
    }
  }, [settings.sound_enabled]);

  const isQuietTime = useCallback(() => {
    if (!settings.quiet_hours.enabled) return false;
    
    const now = new Date();
    const currentTime = now.getHours() * 100 + now.getMinutes();
    const startTime = parseInt(settings.quiet_hours.start.replace(':', ''));
    const endTime = parseInt(settings.quiet_hours.end.replace(':', ''));
    
    if (startTime < endTime) {
      return currentTime >= startTime && currentTime <= endTime;
    } else {
      return currentTime >= startTime || currentTime <= endTime;
    }
  }, [settings.quiet_hours]);

  const showBrowserNotification = useCallback((notification: NotificationType) => {
    if (!settings.browser_notifications || isQuietTime()) return;
    
    if ('Notification' in window && Notification.permission === 'granted') {
      const browserNotification = new Notification(notification.title, {
        body: notification.message,
        icon: '/icons/notification-icon.png',
        tag: notification.id,
        requireInteraction: notification.priority === 'urgent'
      });

      browserNotification.onclick = () => {
        window.focus();
        if (notification.action_url) {
          window.open(notification.action_url, '_blank');
        }
        browserNotification.close();
      };

      // Auto-fechar após 5 segundos (exceto urgentes)
      if (notification.priority !== 'urgent') {
        setTimeout(() => browserNotification.close(), 5000);
      }
    }
  }, [settings.browser_notifications, isQuietTime]);

  const showNotification = useCallback((
    notification: Omit<NotificationType, 'id' | 'created_at' | 'is_read'>
  ) => {
    const fullNotification: NotificationType = {
      ...notification,
      id: Date.now().toString(),
      created_at: new Date().toISOString(),
      is_read: false
    };

    // Verificar se a categoria está habilitada
    if (!settings.categories[notification.category]) return;

    // Mostrar toast
    const toastOptions: ExternalToast = {
      duration: notification.priority === 'urgent' ? Infinity : 5000,
      action: notification.action_url ? {
        label: notification.action_label || 'Ver',
        onClick: () => window.open(notification.action_url, '_blank')
      } : undefined
    };

    switch (notification.type) {
      case 'success':
        showToast.success(notification.message, toastOptions);
        break;
      case 'error':
        showToast.error(notification.message, toastOptions);
        break;
      case 'warning':
        showToast.warning(notification.message, toastOptions);
        break;
      case 'info':
        showToast.info(notification.message, toastOptions);
        break;
    }

    // Som de notificação
    playNotificationSound();

    // Notificação do browser
    showBrowserNotification(fullNotification);

    // Refresh das notificações da API
    refetch();
  }, [settings, playNotificationSound, showBrowserNotification, refetch]);

  const markAsRead = useCallback(async (id: string) => {
    try {
      await markAsReadMutation.mutateAsync(parseInt(id));
    } catch (error) {
      showToast.error('Erro ao marcar notificação como lida');
    }
  }, [markAsReadMutation]);

  const markAllAsRead = useCallback(async () => {
    try {
      const unreadIds = notifications
        .filter(n => !n.is_read)
        .map(n => n.id);
      
      await Promise.all(
        unreadIds.map(id => markAsReadMutation.mutateAsync(parseInt(id)))
      );
      
      showToast.success('Todas as notificações foram marcadas como lidas');
    } catch (error) {
      showToast.error('Erro ao marcar notificações como lidas');
    }
  }, [notifications, markAsReadMutation]);

  const deleteNotification = useCallback(async (id: string) => {
    try {
      await deleteNotificationMutation.mutateAsync(parseInt(id));
      showToast.success('Notificação removida');
    } catch (error) {
      showToast.error('Erro ao remover notificação');
    }
  }, [deleteNotificationMutation]);

  const updateSettings = useCallback((newSettings: Partial<NotificationSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
    
    // Salvar no localStorage
    const updatedSettings = { ...settings, ...newSettings };
    localStorage.setItem('notification_settings', JSON.stringify(updatedSettings));
    
    showToast.success('Configurações de notificação atualizadas');
  }, [settings]);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!('Notification' in window)) {
      showToast.error('Seu navegador não suporta notificações');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission === 'denied') {
      showToast.error('Notificações foram negadas. Ative nas configurações do navegador.');
      return false;
    }

    const permission = await Notification.requestPermission();
    
    if (permission === 'granted') {
      updateSettings({ browser_notifications: true });
      showToast.success('Notificações do navegador ativadas!');
      return true;
    } else {
      showToast.error('Permissão para notificações negada');
      return false;
    }
  }, [updateSettings]);

  // ===== EFEITOS =====

  // Carregar configurações do localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('notification_settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error('Erro ao carregar configurações de notificação:', error);
      }
    }
  }, []);

  // WebSocket para notificações em tempo real (simulado)
  useEffect(() => {
    // Simular recebimento de notificações via WebSocket
    const interval = setInterval(() => {
      // Este seria substituído por uma conexão WebSocket real
      refetch();
    }, 30000); // Verificar a cada 30 segundos

    return () => clearInterval(interval);
  }, [refetch]);

  const value: NotificationContextType = {
    notifications,
    unreadCount,
    settings,
    showNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    updateSettings,
    requestPermission
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      {/* Toaster global */}
      <Toaster
        position="top-right"
        expand={true}
        richColors={true}
        closeButton={true}
        toastOptions={{
          duration: 4000,
          style: {
            background: 'white',
            border: '1px solid #e5e7eb',
            color: '#374151',
          },
        }}
      />
    </NotificationContext.Provider>
  );
}

// ===== COMPONENTE PAINEL DE NOTIFICAÇÕES =====

export function NotificationPanel() {
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification
  } = useNotificationSystem();

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      case 'info':
      default:
        return <Info className="h-4 w-4 text-blue-600" />;
    }
  };

  const getPriorityBadge = (priority: string) => {
    const config = {
      low: { label: 'Baixa', variant: 'secondary' as const },
      medium: { label: 'Média', variant: 'outline' as const },
      high: { label: 'Alta', variant: 'default' as const },
      urgent: { label: 'Urgente', variant: 'destructive' as const }
    };

    const { label, variant } = config[priority as keyof typeof config] || config.medium;
    
    return (
      <Badge variant={variant} className="text-xs">
        {label}
      </Badge>
    );
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </Button>
      </SheetTrigger>

      <SheetContent className="w-96 p-0">
        <div className="flex flex-col h-full">
          {/* Header */}
          <SheetHeader className="p-6 pb-0">
            <div className="flex items-center justify-between">
              <div>
                <SheetTitle className="flex items-center space-x-2">
                  <Bell className="h-5 w-5" />
                  <span>Notificações</span>
                </SheetTitle>
                <SheetDescription>
                  {unreadCount > 0 ? `${unreadCount} não lidas` : 'Todas lidas'}
                </SheetDescription>
              </div>

              {unreadCount > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={markAllAsRead}
                >
                  Marcar todas como lidas
                </Button>
              )}
            </div>
          </SheetHeader>

          {/* Lista de Notificações */}
          <ScrollArea className="flex-1 px-6">
            {notifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Bell className="h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-600 font-medium mb-2">
                  Nenhuma notificação
                </p>
                <p className="text-sm text-gray-500">
                  Você está em dia com tudo!
                </p>
              </div>
            ) : (
              <div className="space-y-4 py-4">
                {notifications.map((notification) => (
                  <Card
                    key={notification.id}
                    className={`cursor-pointer transition-colors ${
                      !notification.is_read
                        ? 'bg-blue-50 border-blue-200'
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => !notification.is_read && markAsRead(notification.id)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between space-x-3">
                        <div className="flex items-start space-x-3 flex-1">
                          <div className="mt-0.5">
                            {getNotificationIcon(notification.type)}
                          </div>
                          
                          <div className="flex-1 space-y-1">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium text-gray-900">
                                {notification.title}
                              </p>
                              {!notification.is_read && (
                                <div className="w-2 h-2 bg-blue-600 rounded-full" />
                              )}
                            </div>
                            
                            <p className="text-sm text-gray-600">
                              {notification.message}
                            </p>
                            
                            <div className="flex items-center justify-between">
                              <p className="text-xs text-gray-500">
                                {formatDistance(new Date(notification.created_at), new Date(), {
                                  addSuffix: true,
                                  locale: ptBR
                                })}
                              </p>
                              
                              {getPriorityBadge(notification.priority)}
                            </div>

                            {notification.action_url && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="mt-2"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  window.open(notification.action_url, '_blank');
                                }}
                              >
                                {notification.action_label || 'Ver Detalhes'}
                              </Button>
                            )}
                          </div>
                        </div>

                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 text-gray-400 hover:text-gray-600"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>

          {/* Footer */}
          <Separator />
          <div className="p-6">
            <NotificationSettings />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

// ===== CONFIGURAÇÕES DE NOTIFICAÇÃO =====

export function NotificationSettings() {
  const {
    settings,
    updateSettings,
    requestPermission
  } = useNotificationSystem();

  const [isExpanded, setIsExpanded] = useState(false);

  const handleBrowserNotificationToggle = async (enabled: boolean) => {
    if (enabled) {
      const granted = await requestPermission();
      if (granted) {
        updateSettings({ browser_notifications: true });
      }
    } else {
      updateSettings({ browser_notifications: false });
    }
  };

  if (!isExpanded) {
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsExpanded(true)}
        className="w-full"
      >
        <Settings className="h-4 w-4 mr-2" />
        Configurar Notificações
      </Button>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium">Configurações</Label>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(false)}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Som */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {settings.sound_enabled ? (
            <Volume2 className="h-4 w-4 text-gray-600" />
          ) : (
            <VolumeX className="h-4 w-4 text-gray-600" />
          )}
          <Label className="text-sm">Som</Label>
        </div>
        <Switch
          checked={settings.sound_enabled}
          onCheckedChange={(enabled) => updateSettings({ sound_enabled: enabled })}
        />
      </div>

      {/* Notificações do Browser */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BellRing className="h-4 w-4 text-gray-600" />
          <Label className="text-sm">Browser</Label>
        </div>
        <Switch
          checked={settings.browser_notifications}
          onCheckedChange={handleBrowserNotificationToggle}
        />
      </div>

      {/* Categorias */}
      <div className="space-y-2">
        <Label className="text-sm font-medium">Categorias</Label>
        {Object.entries(settings.categories).map(([category, enabled]) => (
          <div key={category} className="flex items-center justify-between">
            <Label className="text-sm capitalize">{category}</Label>
            <Switch
              checked={enabled}
              onCheckedChange={(checked) =>
                updateSettings({
                  categories: { ...settings.categories, [category]: checked }
                })
              }
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default NotificationProvider;
