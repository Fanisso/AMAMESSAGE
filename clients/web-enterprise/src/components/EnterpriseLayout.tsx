import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Badge,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Campaign,
  Contacts,
  Message,
  Group,
  Analytics,
  Send,
  Code,
  Settings,
  ExpandLess,
  ExpandMore,
  Notifications,
  AccountCircle,
  Logout,
  Help,
  Brightness4,
  Brightness7,
  Business,
  AutoAwesome,
  Api,
  Receipt,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 280;

interface EnterpriseLayoutProps {
  children: React.ReactNode;
}

interface NavItem {
  text: string;
  icon: React.ReactElement;
  path?: string;
  children?: NavItem[];
  badge?: number;
}

const EnterpriseLayout: React.FC<EnterpriseLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('lg'));
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>(['campaigns', 'sms', 'reports']);

  const navItems: NavItem[] = [
    {
      text: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard',
    },
    {
      text: 'Campanhas',
      icon: <Campaign />,
      children: [
        { text: 'Todas as Campanhas', icon: <Campaign />, path: '/campaigns' },
        { text: 'Nova Campanha', icon: <Campaign />, path: '/campaigns/new' },
        { text: 'Templates', icon: <Message />, path: '/templates' },
      ],
    },
    {
      text: 'Contactos',
      icon: <Contacts />,
      children: [
        { text: 'Todos os Contactos', icon: <Contacts />, path: '/contacts' },
        { text: 'Grupos', icon: <Group />, path: '/contacts/groups' },
        { text: 'Importar', icon: <Contacts />, path: '/contacts/import' },
      ],
    },
    {
      text: 'SMS',
      icon: <Send />,
      children: [
        { text: 'Enviar SMS', icon: <Send />, path: '/sms/send' },
        { text: 'Envio em Massa', icon: <Send />, path: '/sms/bulk' },
        { text: 'Histórico', icon: <Send />, path: '/sms/history' },
      ],
    },
    {
      text: 'USSD',
      icon: <Code />,
      children: [
        { text: 'Códigos USSD', icon: <Code />, path: '/ussd/codes' },
        { text: 'Sessões', icon: <Code />, path: '/ussd/sessions' },
      ],
    },
    {
      text: 'Automação',
      icon: <AutoAwesome />,
      children: [
        { text: 'Fluxos', icon: <AutoAwesome />, path: '/automation/workflows' },
        { text: 'Gatilhos', icon: <AutoAwesome />, path: '/automation/triggers' },
      ],
    },
    {
      text: 'Equipe',
      icon: <Group />,
      children: [
        { text: 'Membros', icon: <Group />, path: '/team/members' },
        { text: 'Funções', icon: <Group />, path: '/team/roles' },
      ],
    },
    {
      text: 'Relatórios',
      icon: <Analytics />,
      children: [
        { text: 'Campanhas', icon: <Analytics />, path: '/reports/campaigns' },
        { text: 'Contactos', icon: <Analytics />, path: '/reports/contacts' },
        { text: 'Uso do Sistema', icon: <Analytics />, path: '/reports/usage' },
        { text: 'Analytics', icon: <Analytics />, path: '/analytics' },
      ],
    },
    {
      text: 'Integrações',
      icon: <Api />,
      children: [
        { text: 'API', icon: <Api />, path: '/integrations/api' },
        { text: 'Webhooks', icon: <Api />, path: '/integrations/webhooks' },
        { text: 'Terceiros', icon: <Api />, path: '/integrations/third-party' },
      ],
    },
    {
      text: 'Configurações',
      icon: <Settings />,
      children: [
        { text: 'Conta', icon: <Settings />, path: '/settings/account' },
        { text: 'Faturação', icon: <Receipt />, path: '/settings/billing' },
        { text: 'Notificações', icon: <Notifications />, path: '/settings/notifications' },
        { text: 'Segurança', icon: <Settings />, path: '/settings/security' },
      ],
    },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleExpandClick = (itemText: string) => {
    setExpandedItems(prev =>
      prev.includes(itemText)
        ? prev.filter(item => item !== itemText)
        : [...prev, itemText]
    );
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  const renderNavItem = (item: NavItem, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.includes(item.text.toLowerCase());
    const isActive = item.path ? isActiveRoute(item.path) : false;

    return (
      <React.Fragment key={item.text}>
        <ListItem disablePadding sx={{ display: 'block' }}>
          <ListItemButton
            onClick={() => {
              if (hasChildren) {
                handleExpandClick(item.text.toLowerCase());
              } else if (item.path) {
                handleNavigation(item.path);
              }
            }}
            sx={{
              minHeight: 48,
              justifyContent: 'initial',
              px: 2.5,
              pl: level > 0 ? 4 : 2.5,
              backgroundColor: isActive ? 'primary.main' : 'transparent',
              color: isActive ? 'primary.contrastText' : 'inherit',
              '&:hover': {
                backgroundColor: isActive ? 'primary.dark' : 'action.hover',
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: 3,
                justifyContent: 'center',
                color: isActive ? 'primary.contrastText' : 'inherit',
              }}
            >
              {item.badge ? (
                <Badge badgeContent={item.badge} color="error">
                  {item.icon}
                </Badge>
              ) : (
                item.icon
              )}
            </ListItemIcon>
            <ListItemText
              primary={item.text}
              sx={{
                opacity: 1,
                '& .MuiTypography-root': {
                  fontSize: level > 0 ? '0.875rem' : '1rem',
                  fontWeight: isActive ? 600 : 400,
                },
              }}
            />
            {hasChildren && (
              isExpanded ? <ExpandLess /> : <ExpandMore />
            )}
          </ListItemButton>
        </ListItem>

        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map((child) => renderNavItem(child, level + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawer = (
    <Box>
      {/* Logo */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Business color="primary" sx={{ fontSize: 32 }} />
        <Box>
          <Typography variant="h6" noWrap component="div" fontWeight="bold">
            AMA ENTERPRISE
          </Typography>
          <Typography variant="caption" color="text.secondary">
            SMS & Communication
          </Typography>
        </Box>
      </Box>

      {/* User Info */}
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'primary.contrastText', mb: 1 }}>
        <Box display="flex" alignItems="center" gap={2}>
          <Avatar sx={{ bgcolor: 'primary.dark' }}>
            <Business />
          </Avatar>
          <Box>
            <Typography variant="subtitle2" fontWeight="bold">
              Tech Solutions Ltd
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              João Silva - Administrador
            </Typography>
          </Box>
        </Box>
        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            Créditos: 15.240 MT
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            Plan: Business
          </Typography>
        </Box>
      </Box>

      <Divider />

      {/* Navigation */}
      <List sx={{ pt: 1 }}>
        {navItems.map((item) => renderNavItem(item))}
      </List>

      <Divider sx={{ mt: 2 }} />

      {/* Support Links */}
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={() => handleNavigation('/help')}>
            <ListItemIcon>
              <Help />
            </ListItemIcon>
            <ListItemText primary="Ajuda & Suporte" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { lg: `calc(100% - ${drawerWidth}px)` },
          ml: { lg: `${drawerWidth}px` },
          bgcolor: 'background.default',
          color: 'text.primary',
          boxShadow: 1,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { lg: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Box sx={{ flexGrow: 1 }} />

          {/* Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Notificações">
              <IconButton color="inherit">
                <Badge badgeContent={3} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>

            <Tooltip title="Alternar tema">
              <IconButton color="inherit">
                <Brightness4 />
              </IconButton>
            </Tooltip>

            <Tooltip title="Conta">
              <IconButton
                color="inherit"
                onClick={handleUserMenuOpen}
                sx={{ ml: 1 }}
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                  JS
                </Avatar>
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        PaperProps={{
          sx: { width: 220, mt: 1.5 },
        }}
      >
        <MenuItem onClick={() => { handleNavigation('/profile'); handleUserMenuClose(); }}>
          <ListItemIcon>
            <AccountCircle fontSize="small" />
          </ListItemIcon>
          Perfil
        </MenuItem>
        <MenuItem onClick={() => { handleNavigation('/account'); handleUserMenuClose(); }}>
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          Configurações da Conta
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleUserMenuClose}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Sair
        </MenuItem>
      </Menu>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { lg: drawerWidth }, flexShrink: { lg: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', lg: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', lg: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { lg: `calc(100% - ${drawerWidth}px)` },
          bgcolor: 'background.default',
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default EnterpriseLayout;
