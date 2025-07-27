// Layout Principal da Aplicação Enterprise
// Sistema de navegação e layout responsivo com sidebar

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { 
  Menu, 
  X, 
  Home, 
  Users, 
  MessageSquare, 
  Target, 
  Mail, 
  BarChart3, 
  Settings, 
  Bell, 
  Search,
  User,
  LogOut,
  ChevronDown,
  ChevronRight,
  Zap,
  Phone,
  Calendar,
  FileText,
  Shield,
  Database,
  Wifi,
  WifiOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {
  Sheet,
  SheetContent,
  SheetTrigger
} from '@/components/ui/sheet';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useAuth } from '@/hooks/useAuth';
import { useSystemStatus, useNotifications } from '@/hooks/api-hooks';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

// ===== TIPOS =====

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string | number;
  children?: NavigationItem[];
}

interface LayoutProps {
  children: React.ReactNode;
}

// ===== CONFIGURAÇÃO DE NAVEGAÇÃO =====

const navigation: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home
  },
  {
    name: 'SMS',
    href: '/sms',
    icon: MessageSquare,
    children: [
      { name: 'Enviar SMS', href: '/sms/send', icon: Zap },
      { name: 'Envio Rápido', href: '/sms/quick', icon: Zap },
      { name: 'Histórico', href: '/sms/history', icon: FileText },
      { name: 'Relatórios', href: '/sms/reports', icon: BarChart3 }
    ]
  },
  {
    name: 'Contatos',
    href: '/contacts',
    icon: Users,
    children: [
      { name: 'Lista de Contatos', href: '/contacts', icon: Users },
      { name: 'Novo Contato', href: '/contacts/new', icon: User },
      { name: 'Importar', href: '/contacts/import', icon: Database },
      { name: 'Grupos', href: '/contacts/groups', icon: Users }
    ]
  },
  {
    name: 'Campanhas',
    href: '/campaigns',
    icon: Target,
    children: [
      { name: 'Minhas Campanhas', href: '/campaigns', icon: Target },
      { name: 'Nova Campanha', href: '/campaigns/new', icon: Target },
      { name: 'Templates', href: '/campaigns/templates', icon: Mail },
      { name: 'Agendamentos', href: '/campaigns/scheduled', icon: Calendar }
    ]
  },
  {
    name: 'Templates',
    href: '/templates',
    icon: Mail,
    children: [
      { name: 'Meus Templates', href: '/templates', icon: Mail },
      { name: 'Novo Template', href: '/templates/new', icon: Mail },
      { name: 'Biblioteca', href: '/templates/library', icon: FileText }
    ]
  },
  {
    name: 'Relatórios',
    href: '/reports',
    icon: BarChart3,
    children: [
      { name: 'Visão Geral', href: '/reports', icon: BarChart3 },
      { name: 'SMS Enviados', href: '/reports/sms', icon: MessageSquare },
      { name: 'Campanhas', href: '/reports/campaigns', icon: Target },
      { name: 'Custos', href: '/reports/costs', icon: BarChart3 }
    ]
  },
  {
    name: 'Configurações',
    href: '/settings',
    icon: Settings,
    children: [
      { name: 'Perfil', href: '/settings/profile', icon: User },
      { name: 'Conta', href: '/settings/account', icon: Settings },
      { name: 'Notificações', href: '/settings/notifications', icon: Bell },
      { name: 'Segurança', href: '/settings/security', icon: Shield },
      { name: 'API', href: '/settings/api', icon: Database }
    ]
  }
];

// ===== COMPONENTE DE ITEM DE NAVEGAÇÃO =====

interface NavigationItemProps {
  item: NavigationItem;
  isActive: boolean;
  isMobile?: boolean;
  onItemClick?: () => void;
}

function NavigationItemComponent({ 
  item, 
  isActive, 
  isMobile = false,
  onItemClick 
}: NavigationItemProps) {
  const router = useRouter();
  const [isExpanded, setIsExpanded] = useState(false);
  const hasChildren = item.children && item.children.length > 0;
  
  // Verificar se algum filho está ativo
  const hasActiveChild = hasChildren && item.children?.some(child => 
    router.pathname.startsWith(child.href)
  );

  // Expandir automaticamente se tiver filho ativo
  useEffect(() => {
    if (hasActiveChild) {
      setIsExpanded(true);
    }
  }, [hasActiveChild]);

  const handleClick = () => {
    if (hasChildren) {
      setIsExpanded(!isExpanded);
    } else {
      router.push(item.href);
      onItemClick?.();
    }
  };

  const Icon = item.icon;

  return (
    <div className="space-y-1">
      {/* Item Principal */}
      <button
        onClick={handleClick}
        className={cn(
          'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          isActive || hasActiveChild
            ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-600'
            : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
        )}
      >
        <div className="flex items-center space-x-3">
          <Icon className="h-5 w-5" />
          <span>{item.name}</span>
        </div>
        
        <div className="flex items-center space-x-1">
          {item.badge && (
            <Badge variant="secondary" className="text-xs">
              {item.badge}
            </Badge>
          )}
          
          {hasChildren && (
            <div className="transition-transform duration-200">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </div>
          )}
        </div>
      </button>

      {/* Subitens */}
      {hasChildren && isExpanded && (
        <div className="ml-6 space-y-1">
          {item.children?.map((child) => {
            const ChildIcon = child.icon;
            const isChildActive = router.pathname === child.href;
            
            return (
              <Link
                key={child.href}
                href={child.href}
                onClick={onItemClick}
                className={cn(
                  'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-colors',
                  isChildActive
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <ChildIcon className="h-4 w-4" />
                <span>{child.name}</span>
                {child.badge && (
                  <Badge variant="outline" className="text-xs ml-auto">
                    {child.badge}
                  </Badge>
                )}
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ===== SIDEBAR DESKTOP =====

function Sidebar() {
  const router = useRouter();

  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
      <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white border-r border-gray-200 px-6 pb-4">
        {/* Logo */}
        <div className="flex h-16 shrink-0 items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <MessageSquare className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">AMA MESSAGE</h2>
              <p className="text-xs text-gray-500">Enterprise</p>
            </div>
          </div>
        </div>

        {/* Navegação */}
        <nav className="flex flex-1 flex-col">
          <ul className="flex flex-1 flex-col gap-y-7">
            <li>
              <div className="space-y-1">
                {navigation.map((item) => (
                  <NavigationItemComponent
                    key={item.name}
                    item={item}
                    isActive={router.pathname === item.href}
                  />
                ))}
              </div>
            </li>
          </ul>
        </nav>

        {/* Status do Sistema */}
        <SystemStatusIndicator />
      </div>
    </div>
  );
}

// ===== SIDEBAR MOBILE =====

function MobileSidebar() {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="lg:hidden">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      
      <SheetContent side="left" className="w-72 p-0">
        <div className="flex h-full flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <MessageSquare className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">AMA MESSAGE</h2>
                <p className="text-xs text-gray-500">Enterprise</p>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="icon"
              className="ml-auto"
              onClick={() => setOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navegação */}
          <nav className="flex flex-1 flex-col">
            <div className="space-y-1">
              {navigation.map((item) => (
                <NavigationItemComponent
                  key={item.name}
                  item={item}
                  isActive={router.pathname === item.href}
                  isMobile={true}
                  onItemClick={() => setOpen(false)}
                />
              ))}
            </div>
          </nav>

          {/* Status do Sistema */}
          <SystemStatusIndicator />
        </div>
      </SheetContent>
    </Sheet>
  );
}

// ===== INDICADOR DE STATUS DO SISTEMA =====

function SystemStatusIndicator() {
  const { data: systemStatus } = useSystemStatus();

  if (!systemStatus) return null;

  const isHealthy = systemStatus.status === 'healthy';

  return (
    <div className="border-t border-gray-200 pt-4">
      <div className="flex items-center space-x-3 px-3 py-2 rounded-lg bg-gray-50">
        <div className="flex items-center space-x-2">
          {isHealthy ? (
            <Wifi className="h-4 w-4 text-green-600" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-600" />
          )}
          <span className="text-xs font-medium text-gray-700">
            {isHealthy ? 'Sistema Online' : 'Sistema Offline'}
          </span>
        </div>
        
        <div className={cn(
          'w-2 h-2 rounded-full',
          isHealthy ? 'bg-green-500' : 'bg-red-500'
        )} />
      </div>
      
      {systemStatus.modem_status && (
        <div className="mt-2 text-xs text-gray-500 px-3">
          Modem: {systemStatus.modem_status}
        </div>
      )}
    </div>
  );
}

// ===== HEADER DA APLICAÇÃO =====

function Header() {
  const { user, logout } = useAuth();
  const { data: notifications } = useNotifications({ unread_only: true });
  const [searchQuery, setSearchQuery] = useState('');

  const unreadCount = notifications?.length || 0;

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logout realizado com sucesso!');
    } catch (error) {
      toast.error('Erro ao fazer logout');
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Implementar busca global
      toast.info('Busca global em desenvolvimento');
    }
  };

  return (
    <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      {/* Mobile menu button */}
      <MobileSidebar />

      <div className="h-6 w-px bg-gray-900/10 lg:hidden" />

      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        {/* Busca */}
        <form className="relative flex flex-1" onSubmit={handleSearch}>
          <label htmlFor="search-field" className="sr-only">
            Buscar
          </label>
          <Search className="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400 pl-3" />
          <Input
            id="search-field"
            className="block h-full w-full border-0 py-0 pl-10 pr-0 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm"
            placeholder="Buscar contatos, SMS, campanhas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>

        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Notificações */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
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
            </DropdownMenuTrigger>
            
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel>Notificações</DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              {notifications && notifications.length > 0 ? (
                notifications.slice(0, 5).map((notification) => (
                  <DropdownMenuItem key={notification.id} className="flex flex-col items-start p-3">
                    <p className="font-medium text-sm">{notification.title}</p>
                    <p className="text-xs text-gray-500 mt-1">{notification.message}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {notification.created_at && new Date(notification.created_at).toLocaleString('pt-BR')}
                    </p>
                  </DropdownMenuItem>
                ))
              ) : (
                <DropdownMenuItem disabled>
                  Nenhuma notificação
                </DropdownMenuItem>
              )}
              
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/notifications" className="w-full text-center">
                  Ver todas as notificações
                </Link>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Separador */}
          <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-900/10" />

          {/* Menu do usuário */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center space-x-2 px-2">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.avatar_url} alt={user?.name} />
                  <AvatarFallback>
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden lg:block text-left">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.name || 'Usuário'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.email}
                  </p>
                </div>
                <ChevronDown className="h-4 w-4 text-gray-400" />
              </Button>
            </DropdownMenuTrigger>
            
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>Minha Conta</DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              <DropdownMenuItem asChild>
                <Link href="/settings/profile">
                  <User className="h-4 w-4 mr-2" />
                  Perfil
                </Link>
              </DropdownMenuItem>
              
              <DropdownMenuItem asChild>
                <Link href="/settings">
                  <Settings className="h-4 w-4 mr-2" />
                  Configurações
                </Link>
              </DropdownMenuItem>
              
              <DropdownMenuSeparator />
              
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
}

// ===== LAYOUT PRINCIPAL =====

export function AppLayout({ children }: LayoutProps) {
  return (
    <>
      <Sidebar />
      
      <div className="lg:pl-72">
        <Header />
        
        <main className="py-8">
          <div className="px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </>
  );
}

// ===== LAYOUT DE AUTENTICAÇÃO =====

export function AuthLayout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gray-50">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
            <MessageSquare className="h-7 w-7 text-white" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
          AMA MESSAGE
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Sistema de SMS Enterprise
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {children}
        </div>
      </div>
    </div>
  );
}

export default AppLayout;
