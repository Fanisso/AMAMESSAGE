import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tooltip,
} from '@mui/material';
import { DataGrid, GridColDef, GridRowsProp } from '@mui/x-data-grid';
import {
  Add,
  Edit,
  Delete,
  Block,
  CheckCircle,
  Search,
  FilterList,
  Download,
  Refresh,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { useSnackbar } from 'notistack';

// Importar tipos partilhados
import { UserResponse, UserCreateRequest, UserType } from '@/shared/types';

interface UserFormData {
  email: string;
  password: string;
  full_name: string;
  user_type: UserType;
  phone_number?: string;
  company?: string;
  is_active: boolean;
}

const UsersManagementPage: React.FC = () => {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const { enqueueSnackbar } = useSnackbar();
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UserFormData>();

  // Simular dados de utilizadores (substituir por chamada à API)
  const mockUsers: UserResponse[] = [
    {
      id: 1,
      email: 'admin@amamessage.com',
      full_name: 'Administrador Principal',
      user_type: 'super_admin' as UserType,
      is_active: true,
      created_at: new Date('2024-01-15'),
      last_login: new Date('2024-07-27'),
      phone_number: '+258823456789',
      company: 'AMA MESSAGE',
      timezone: 'Africa/Maputo',
      language: 'pt',
    },
    {
      id: 2,
      email: 'empresa@cliente.com',
      full_name: 'Gestor Empresarial',
      user_type: 'enterprise_user' as UserType,
      is_active: true,
      created_at: new Date('2024-03-10'),
      last_login: new Date('2024-07-26'),
      phone_number: '+258843567890',
      company: 'Cliente Empresarial Lda',
      timezone: 'Africa/Maputo',
      language: 'pt',
    },
    {
      id: 3,
      email: 'individual@user.com',
      full_name: 'Utilizador Individual',
      user_type: 'individual_user' as UserType,
      is_active: true,
      created_at: new Date('2024-05-20'),
      last_login: new Date('2024-07-25'),
      phone_number: '+258856789012',
      company: null,
      timezone: 'Africa/Maputo',
      language: 'pt',
    },
    {
      id: 4,
      email: 'inactive@user.com',
      full_name: 'Utilizador Inativo',
      user_type: 'individual_user' as UserType,
      is_active: false,
      created_at: new Date('2024-02-01'),
      last_login: new Date('2024-06-01'),
      phone_number: '+258867890123',
      company: null,
      timezone: 'Africa/Maputo',
      language: 'pt',
    },
  ];

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setUsers(mockUsers);
      setLoading(false);
    }, 1000);
  }, []);

  const getUserTypeColor = (type: UserType) => {
    switch (type) {
      case 'super_admin':
        return { color: 'error', label: 'Super Admin' };
      case 'admin':
        return { color: 'warning', label: 'Admin' };
      case 'enterprise_user':
        return { color: 'primary', label: 'Empresa' };
      case 'individual_user':
        return { color: 'info', label: 'Individual' };
      default:
        return { color: 'default', label: 'Desconhecido' };
    }
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive 
      ? { color: 'success', label: 'Ativo' }
      : { color: 'error', label: 'Inativo' };
  };

  const formatDate = (date: Date | null) => {
    if (!date) return 'Nunca';
    return date.toLocaleDateString('pt-PT') + ' ' + date.toLocaleTimeString('pt-PT', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const columns: GridColDef[] = [
    {
      field: 'id',
      headerName: 'ID',
      width: 80,
    },
    {
      field: 'full_name',
      headerName: 'Nome Completo',
      width: 200,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="bold">
            {params.value}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {params.row.email}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'user_type',
      headerName: 'Tipo',
      width: 130,
      renderCell: (params) => {
        const { color, label } = getUserTypeColor(params.value);
        return (
          <Chip
            label={label}
            color={color as any}
            size="small"
            variant="outlined"
          />
        );
      },
    },
    {
      field: 'company',
      headerName: 'Empresa',
      width: 150,
      renderCell: (params) => params.value || '-',
    },
    {
      field: 'phone_number',
      headerName: 'Telefone',
      width: 130,
    },
    {
      field: 'is_active',
      headerName: 'Status',
      width: 100,
      renderCell: (params) => {
        const { color, label } = getStatusColor(params.value);
        return (
          <Chip
            label={label}
            color={color as any}
            size="small"
            variant="filled"
          />
        );
      },
    },
    {
      field: 'last_login',
      headerName: 'Último Login',
      width: 160,
      renderCell: (params) => (
        <Typography variant="caption">
          {formatDate(params.value)}
        </Typography>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Criado em',
      width: 160,
      renderCell: (params) => (
        <Typography variant="caption">
          {formatDate(params.value)}
        </Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Ações',
      width: 150,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Editar">
            <IconButton
              size="small"
              onClick={() => handleEditUser(params.row)}
            >
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={params.row.is_active ? 'Desativar' : 'Ativar'}>
            <IconButton
              size="small"
              onClick={() => handleToggleStatus(params.row)}
              color={params.row.is_active ? 'error' : 'success'}
            >
              {params.row.is_active ? <Block fontSize="small" /> : <CheckCircle fontSize="small" />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Eliminar">
            <IconButton
              size="small"
              onClick={() => handleDeleteUser(params.row)}
              color="error"
            >
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  const handleCreateUser = (data: UserFormData) => {
    // Simular criação de utilizador
    const newUser: UserResponse = {
      id: users.length + 1,
      email: data.email,
      full_name: data.full_name,
      user_type: data.user_type,
      is_active: data.is_active,
      created_at: new Date(),
      last_login: null,
      phone_number: data.phone_number || null,
      company: data.company || null,
      timezone: 'Africa/Maputo',
      language: 'pt',
    };

    setUsers([...users, newUser]);
    setIsCreateDialogOpen(false);
    reset();
    enqueueSnackbar('Utilizador criado com sucesso!', { variant: 'success' });
  };

  const handleEditUser = (user: UserResponse) => {
    setSelectedUser(user);
    reset({
      email: user.email,
      full_name: user.full_name,
      user_type: user.user_type,
      phone_number: user.phone_number || '',
      company: user.company || '',
      is_active: user.is_active,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateUser = (data: UserFormData) => {
    if (!selectedUser) return;

    const updatedUsers = users.map(user =>
      user.id === selectedUser.id
        ? {
            ...user,
            full_name: data.full_name,
            user_type: data.user_type,
            phone_number: data.phone_number || null,
            company: data.company || null,
            is_active: data.is_active,
          }
        : user
    );

    setUsers(updatedUsers);
    setIsEditDialogOpen(false);
    setSelectedUser(null);
    reset();
    enqueueSnackbar('Utilizador atualizado com sucesso!', { variant: 'success' });
  };

  const handleToggleStatus = (user: UserResponse) => {
    const updatedUsers = users.map(u =>
      u.id === user.id ? { ...u, is_active: !u.is_active } : u
    );
    setUsers(updatedUsers);
    enqueueSnackbar(
      `Utilizador ${user.is_active ? 'desativado' : 'ativado'} com sucesso!`,
      { variant: 'info' }
    );
  };

  const handleDeleteUser = (user: UserResponse) => {
    if (window.confirm(`Tem certeza que deseja eliminar o utilizador "${user.full_name}"?`)) {
      const updatedUsers = users.filter(u => u.id !== user.id);
      setUsers(updatedUsers);
      enqueueSnackbar('Utilizador eliminado com sucesso!', { variant: 'success' });
    }
  };

  const handleExportUsers = () => {
    // Simular exportação
    enqueueSnackbar('Exportação iniciada! Será enviada por email.', { variant: 'info' });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (user.company && user.company.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = filterType === 'all' || user.user_type === filterType;
    const matchesStatus = filterStatus === 'all' || 
                         (filterStatus === 'active' && user.is_active) ||
                         (filterStatus === 'inactive' && !user.is_active);

    return matchesSearch && matchesType && matchesStatus;
  });

  const userStats = {
    total: users.length,
    active: users.filter(u => u.is_active).length,
    inactive: users.filter(u => !u.is_active).length,
    superAdmin: users.filter(u => u.user_type === 'super_admin').length,
    admin: users.filter(u => u.user_type === 'admin').length,
    enterprise: users.filter(u => u.user_type === 'enterprise_user').length,
    individual: users.filter(u => u.user_type === 'individual_user').length,
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Gestão de Utilizadores
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Administração completa de todos os utilizadores do sistema
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExportUsers}
          >
            Exportar
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            Novo Utilizador
          </Button>
        </Box>
      </Box>

      {/* Estatísticas */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total de Utilizadores
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {userStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Utilizadores Ativos
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {userStats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Empresariais
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="primary.main">
                {userStats.enterprise}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Individuais
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="info.main">
                {userStats.individual}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filtros */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Pesquisar utilizadores..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Utilizador</InputLabel>
                <Select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  label="Tipo de Utilizador"
                >
                  <MenuItem value="all">Todos os Tipos</MenuItem>
                  <MenuItem value="super_admin">Super Admin</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="enterprise_user">Empresarial</MenuItem>
                  <MenuItem value="individual_user">Individual</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">Todos</MenuItem>
                  <MenuItem value="active">Ativos</MenuItem>
                  <MenuItem value="inactive">Inativos</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {
                  setSearchTerm('');
                  setFilterType('all');
                  setFilterStatus('all');
                }}
              >
                Limpar
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabela de utilizadores */}
      <Card>
        <Box sx={{ height: 600, width: '100%' }}>
          <DataGrid
            rows={filteredUsers}
            columns={columns}
            loading={loading}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            disableSelectionOnClick
            sx={{
              '& .MuiDataGrid-root': {
                border: 'none',
              },
            }}
          />
        </Box>
      </Card>

      {/* Dialog de criação */}
      <Dialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <form onSubmit={handleSubmit(handleCreateUser)}>
          <DialogTitle>Criar Novo Utilizador</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="email"
                  control={control}
                  rules={{ required: 'Email é obrigatório' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Email"
                      type="email"
                      error={!!errors.email}
                      helperText={errors.email?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="password"
                  control={control}
                  rules={{ required: 'Password é obrigatória', minLength: { value: 8, message: 'Mínimo 8 caracteres' } }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Password"
                      type="password"
                      error={!!errors.password}
                      helperText={errors.password?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="full_name"
                  control={control}
                  rules={{ required: 'Nome é obrigatório' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Nome Completo"
                      error={!!errors.full_name}
                      helperText={errors.full_name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="user_type"
                  control={control}
                  rules={{ required: 'Tipo é obrigatório' }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.user_type}>
                      <InputLabel>Tipo de Utilizador</InputLabel>
                      <Select {...field} label="Tipo de Utilizador">
                        <MenuItem value="admin">Admin</MenuItem>
                        <MenuItem value="enterprise_user">Empresarial</MenuItem>
                        <MenuItem value="individual_user">Individual</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="phone_number"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Telefone"
                      placeholder="+258..."
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="company"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Empresa"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsCreateDialogOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" variant="contained">
              Criar Utilizador
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Dialog de edição */}
      <Dialog
        open={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <form onSubmit={handleSubmit(handleUpdateUser)}>
          <DialogTitle>Editar Utilizador</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="email"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Email"
                      disabled
                      helperText="Email não pode ser alterado"
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="user_type"
                  control={control}
                  rules={{ required: 'Tipo é obrigatório' }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.user_type}>
                      <InputLabel>Tipo de Utilizador</InputLabel>
                      <Select {...field} label="Tipo de Utilizador">
                        <MenuItem value="admin">Admin</MenuItem>
                        <MenuItem value="enterprise_user">Empresarial</MenuItem>
                        <MenuItem value="individual_user">Individual</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="full_name"
                  control={control}
                  rules={{ required: 'Nome é obrigatório' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Nome Completo"
                      error={!!errors.full_name}
                      helperText={errors.full_name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="phone_number"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Telefone"
                      placeholder="+258..."
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="company"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Empresa"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditDialogOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" variant="contained">
              Atualizar
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default UsersManagementPage;
