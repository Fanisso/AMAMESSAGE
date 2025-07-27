import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Chip,
  useTheme,
  useMediaQuery,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  People,
  Settings,
  Monitoring,
  History,
  Hardware,
  Assessment,
  Security,
  Notifications,
  ExitToApp,
  Person,
  DarkMode,
  LightMode,
  AdminPanelSettings,
} from '@mui/icons-material';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const drawerWidth = 280;

interface MenuItemData {
  id: string;
  label: string;
  path: string;
  icon: React.ReactNode;
  badge?: number;
  adminOnly?: boolean;
}

const menuItems: MenuItemData[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: <Dashboard />,
  },
  {
    id: 'users',
    label: 'Gestão de Utilizadores',
    path: '/users',
    icon: <People />,
    adminOnly: true,
  },
  {
    id: 'config',
    label: 'Configuração do Sistema',
    path: '/system-config',
    icon: <Settings />,
    adminOnly: true,
  },
  {
    id: 'monitoring',
    label: 'Monitorização',
    path: '/monitoring',
    icon: <Monitoring />,
    badge: 3, // Alertas ativos
  },
  {
    id: 'logs',
    label: 'Logs e Auditoria',
    path: '/logs-audit',
    icon: <History />,
  },
  {
    id: 'hardware',
    label: 'Gestão de Hardware',
    path: '/hardware',
    icon: <Hardware />,
    adminOnly: true,
  },
  {
    id: 'reports',
    label: 'Relatórios Globais',
    path: '/reports',
    icon: <Assessment />,
  },
  {
    id: 'security',
    label: 'Gestão de Segurança',
    path: '/security',
    icon: <Security />,
    adminOnly: true,
  },
];

const AdminLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null);
  const [isDarkMode, setIsDarkMode] = useState(true);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    handleProfileMenuClose();
  };

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode);
    // Aqui você implementaria a mudança de tema global
  };

  const isActiveItem = (path: string) => {
    return location.pathname === path;
  };

  const getUserTypeLabel = (userType: string) => {
    switch (userType) {
      case 'super_admin':
        return 'Super Admin';
      case 'admin':
        return 'Admin';
      default:
        return 'Admin';
    }
  };

  const getUserTypeColor = (userType: string) => {
    switch (userType) {
      case 'super_admin':
        return 'error';
      case 'admin':
        return 'warning';
      default:
        return 'primary';
    }
  };

  const filteredMenuItems = menuItems.filter(item => 
    !item.adminOnly || (user && ['super_admin', 'admin'].includes(user.user_type))
  );

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo e Título */}
      <Box sx={{ p: 2, textAlign: 'center', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box display="flex" alignItems="center" justifyContent="center" gap={1} mb={1}>
          <AdminPanelSettings sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h5" fontWeight="bold" color="primary.main">
            AMA MESSAGE
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Interface Administrativa
        </Typography>
      </Box>

      {/* Menu de Navegação */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ pt: 2 }}>
          {filteredMenuItems.map((item) => (
            <ListItem key={item.id} disablePadding sx={{ mb: 0.5, px: 1 }}>
              <ListItemButton
                onClick={() => {
                  navigate(item.path);
                  if (isMobile) setMobileOpen(false);
                }}
                selected={isActiveItem(item.path)}
                sx={{
                  minHeight: 48,
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: 2,
                    justifyContent: 'center',
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
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: isActiveItem(item.path) ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Informações do Utilizador */}
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Box display="flex" alignItems="center" gap={1}>
          <Avatar
            sx={{ 
              width: 40, 
              height: 40, 
              bgcolor: 'primary.main',
              fontSize: '1.2rem',
              fontWeight: 'bold',
            }}
          >
            {user?.full_name?.charAt(0)?.toUpperCase() || 'A'}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight="bold" noWrap>
              {user?.full_name || 'Admin'}
            </Typography>
            <Chip
              label={getUserTypeLabel(user?.user_type || 'admin')}
              size="small"
              color={getUserTypeColor(user?.user_type || 'admin') as any}
              variant="outlined"
              sx={{ height: 20, fontSize: '0.75rem', mt: 0.5 }}
            />
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'primary.main',
          color: theme.palette.mode === 'dark' ? 'text.primary' : 'primary.contrastText',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {filteredMenuItems.find(item => isActiveItem(item.path))?.label || 'Dashboard Administrativo'}
          </Typography>

          {/* Botões do Header */}
          <Box display="flex" alignItems="center" gap={1}>
            {/* Toggle Theme */}
            <Tooltip title="Alternar tema">
              <IconButton color="inherit" onClick={handleThemeToggle}>
                {isDarkMode ? <LightMode /> : <DarkMode />}
              </IconButton>
            </Tooltip>

            {/* Notificações */}
            <Tooltip title="Notificações">
              <IconButton color="inherit">
                <Badge badgeContent={5} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* Menu do Perfil */}
            <Tooltip title="Perfil do utilizador">
              <IconButton
                color="inherit"
                onClick={handleProfileMenuOpen}
                sx={{ ml: 1 }}
              >
                <Avatar
                  sx={{ 
                    width: 32, 
                    height: 32,
                    bgcolor: 'rgba(255,255,255,0.1)',
                    fontSize: '1rem',
                  }}
                >
                  {user?.full_name?.charAt(0)?.toUpperCase() || 'A'}
                </Avatar>
              </IconButton>
            </Tooltip>

            <Menu
              anchorEl={profileMenuAnchor}
              open={Boolean(profileMenuAnchor)}
              onClose={handleProfileMenuClose}
              onClick={handleProfileMenuClose}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem>
                <ListItemIcon>
                  <Person fontSize="small" />
                </ListItemIcon>
                Perfil
              </MenuItem>
              <MenuItem>
                <ListItemIcon>
                  <Security fontSize="small" />
                </ListItemIcon>
                Alterar Password
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <ExitToApp fontSize="small" />
                </ListItemIcon>
                Sair
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
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
            display: { xs: 'none', md: 'block' },
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
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: 'background.default',
        }}
      >
        <Toolbar />
        <Box sx={{ p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default AdminLayout;
