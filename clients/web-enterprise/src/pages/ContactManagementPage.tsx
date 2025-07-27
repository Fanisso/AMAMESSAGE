import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Avatar,
  Checkbox,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Paper,
  InputAdornment,
  Menu,
  Alert,
  Fab,
  Autocomplete,
  Switch,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Upload,
  Download,
  Search,
  FilterList,
  Group,
  Person,
  Business,
  LocationOn,
  Phone,
  Email,
  MoreVert,
  Label,
  Send,
  Visibility,
  ContactPhone,
  ImportContacts,
  GroupAdd,
  Analytics,
  Sync,
} from '@mui/icons-material';
import { DataGrid, GridColDef, GridRowsProp, GridSelectionModel } from '@mui/x-data-grid';
import { useForm, Controller } from 'react-hook-form';
import { useSnackbar } from 'notistack';

interface ContactData {
  id: number;
  name: string;
  phone: string;
  email?: string;
  company?: string;
  position?: string;
  location?: string;
  tags: string[];
  groups: string[];
  status: 'active' | 'inactive' | 'blocked';
  last_contact?: Date;
  sms_sent: number;
  sms_received: number;
  created_at: Date;
  updated_at: Date;
  notes?: string;
  custom_fields: Record<string, any>;
}

interface ContactGroup {
  id: number;
  name: string;
  description: string;
  contacts_count: number;
  created_at: Date;
  color: string;
}

interface ContactFormData {
  name: string;
  phone: string;
  email?: string;
  company?: string;
  position?: string;
  location?: string;
  tags: string[];
  groups: string[];
  notes?: string;
  custom_fields: Record<string, any>;
}

interface ImportResult {
  total: number;
  success: number;
  errors: string[];
}

const ContactManagementPage: React.FC = () => {
  const [contacts, setContacts] = useState<ContactData[]>([]);
  const [groups, setGroups] = useState<ContactGroup[]>([]);
  const [selectedContacts, setSelectedContacts] = useState<GridSelectionModel>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedContact, setSelectedContact] = useState<ContactData | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [isGroupDialogOpen, setIsGroupDialogOpen] = useState(false);
  const [isBulkActionDialogOpen, setIsBulkActionDialogOpen] = useState(false);
  const [filterGroup, setFilterGroup] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);

  const { enqueueSnackbar } = useSnackbar();
  const {
    control,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ContactFormData>();

  // Tags disponíveis
  const availableTags = [
    'Cliente Premium',
    'Prospect',
    'VIP',
    'Novo Cliente',
    'Inativo',
    'Parceiro',
    'Fornecedor',
    'Colaborador',
    'Mídia',
    'Investidor',
  ];

  // Dados simulados
  const mockContacts: ContactData[] = [
    {
      id: 1,
      name: 'João Silva',
      phone: '+258 84 123 4567',
      email: 'joao.silva@empresa.com',
      company: 'Tech Solutions Ltd',
      position: 'CEO',
      location: 'Maputo',
      tags: ['Cliente Premium', 'VIP'],
      groups: ['Clientes Corporativos', 'VIP'],
      status: 'active',
      last_contact: new Date('2024-07-26'),
      sms_sent: 25,
      sms_received: 8,
      created_at: new Date('2024-01-15'),
      updated_at: new Date('2024-07-26'),
      notes: 'Cliente muito importante, sempre responde rapidamente.',
      custom_fields: {
        birthday: '1985-03-12',
        preferred_contact_time: 'Manhã',
      },
    },
    {
      id: 2,
      name: 'Maria Santos',
      phone: '+258 87 987 6543',
      email: 'maria.santos@gmail.com',
      company: 'Freelancer',
      position: 'Designer Gráfica',
      location: 'Matola',
      tags: ['Novo Cliente', 'Prospect'],
      groups: ['Freelancers'],
      status: 'active',
      last_contact: new Date('2024-07-25'),
      sms_sent: 5,
      sms_received: 2,
      created_at: new Date('2024-07-20'),
      updated_at: new Date('2024-07-25'),
      notes: 'Interessada em parcerias de design.',
      custom_fields: {
        skills: 'Photoshop, Illustrator, Figma',
      },
    },
    {
      id: 3,
      name: 'Pedro Machel',
      phone: '+258 82 555 7788',
      email: 'pedro@construcoes.co.mz',
      company: 'Construções do Sul',
      position: 'Diretor de Obras',
      location: 'Beira',
      tags: ['Parceiro', 'Cliente Premium'],
      groups: ['Parceiros', 'Construção'],
      status: 'active',
      last_contact: new Date('2024-07-24'),
      sms_sent: 45,
      sms_received: 18,
      created_at: new Date('2023-11-08'),
      updated_at: new Date('2024-07-24'),
      notes: 'Excelente parceiro para projetos de construção.',
      custom_fields: {
        company_size: '150 funcionários',
        projects_completed: '35',
      },
    },
    {
      id: 4,
      name: 'Ana Costa',
      phone: '+258 86 333 2211',
      email: 'ana.costa@hotmail.com',
      location: 'Nampula',
      tags: ['Inativo'],
      groups: ['Prospects'],
      status: 'inactive',
      last_contact: new Date('2024-06-15'),
      sms_sent: 12,
      sms_received: 1,
      created_at: new Date('2024-05-10'),
      updated_at: new Date('2024-06-15'),
      notes: 'Não respondeu aos últimos contactos.',
      custom_fields: {},
    },
    {
      id: 5,
      name: 'Carlos Manuel',
      phone: '+258 84 777 9999',
      email: 'carlos@logistica.mz',
      company: 'Logística Rápida',
      position: 'Gestor de Frotas',
      location: 'Maputo',
      tags: ['Fornecedor', 'Parceiro'],
      groups: ['Fornecedores', 'Logística'],
      status: 'active',
      last_contact: new Date('2024-07-27'),
      sms_sent: 30,
      sms_received: 12,
      created_at: new Date('2024-02-20'),
      updated_at: new Date('2024-07-27'),
      notes: 'Fornecedor confiável de serviços logísticos.',
      custom_fields: {
        fleet_size: '25 veículos',
        coverage_area: 'Todo o país',
      },
    },
  ];

  const mockGroups: ContactGroup[] = [
    { id: 1, name: 'Clientes Corporativos', description: 'Grandes empresas clientes', contacts_count: 45, created_at: new Date('2024-01-01'), color: '#1976d2' },
    { id: 2, name: 'VIP', description: 'Clientes VIP com atendimento especial', contacts_count: 12, created_at: new Date('2024-01-01'), color: '#f57c00' },
    { id: 3, name: 'Prospects', description: 'Potenciais clientes', contacts_count: 88, created_at: new Date('2024-01-01'), color: '#388e3c' },
    { id: 4, name: 'Parceiros', description: 'Parceiros comerciais', contacts_count: 23, created_at: new Date('2024-01-01'), color: '#7b1fa2' },
    { id: 5, name: 'Fornecedores', description: 'Fornecedores de serviços', contacts_count: 34, created_at: new Date('2024-01-01'), color: '#d32f2f' },
    { id: 6, name: 'Freelancers', description: 'Profissionais freelancers', contacts_count: 67, created_at: new Date('2024-01-01'), color: '#0288d1' },
  ];

  useEffect(() => {
    // Simular carregamento
    setTimeout(() => {
      setContacts(mockContacts);
      setGroups(mockGroups);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'warning';
      case 'blocked': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Ativo';
      case 'inactive': return 'Inativo';
      case 'blocked': return 'Bloqueado';
      default: return status;
    }
  };

  const handleCreateContact = (data: ContactFormData) => {
    const newContact: ContactData = {
      id: contacts.length + 1,
      ...data,
      status: 'active',
      sms_sent: 0,
      sms_received: 0,
      created_at: new Date(),
      updated_at: new Date(),
      custom_fields: data.custom_fields || {},
    };

    setContacts([...contacts, newContact]);
    setIsCreateDialogOpen(false);
    reset();
    enqueueSnackbar('Contacto criado com sucesso!', { variant: 'success' });
  };

  const handleEditContact = (contact: ContactData) => {
    setSelectedContact(contact);
    reset({
      name: contact.name,
      phone: contact.phone,
      email: contact.email,
      company: contact.company,
      position: contact.position,
      location: contact.location,
      tags: contact.tags,
      groups: contact.groups,
      notes: contact.notes,
      custom_fields: contact.custom_fields,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateContact = (data: ContactFormData) => {
    if (!selectedContact) return;

    const updatedContacts = contacts.map(contact =>
      contact.id === selectedContact.id
        ? {
            ...contact,
            ...data,
            updated_at: new Date(),
          }
        : contact
    );

    setContacts(updatedContacts);
    setIsEditDialogOpen(false);
    setSelectedContact(null);
    reset();
    enqueueSnackbar('Contacto atualizado com sucesso!', { variant: 'success' });
  };

  const handleDeleteContact = (contact: ContactData) => {
    if (window.confirm(`Tem certeza que deseja eliminar o contacto "${contact.name}"?`)) {
      const updatedContacts = contacts.filter(c => c.id !== contact.id);
      setContacts(updatedContacts);
      enqueueSnackbar('Contacto eliminado com sucesso!', { variant: 'success' });
    }
  };

  const handleBulkDelete = () => {
    if (selectedContacts.length === 0) return;
    
    if (window.confirm(`Tem certeza que deseja eliminar ${selectedContacts.length} contactos?`)) {
      const updatedContacts = contacts.filter(c => !selectedContacts.includes(c.id));
      setContacts(updatedContacts);
      setSelectedContacts([]);
      enqueueSnackbar(`${selectedContacts.length} contactos eliminados!`, { variant: 'success' });
    }
  };

  const handleBulkAddToGroup = (groupName: string) => {
    if (selectedContacts.length === 0) return;

    const updatedContacts = contacts.map(contact => {
      if (selectedContacts.includes(contact.id)) {
        return {
          ...contact,
          groups: [...new Set([...contact.groups, groupName])],
          updated_at: new Date(),
        };
      }
      return contact;
    });

    setContacts(updatedContacts);
    setSelectedContacts([]);
    enqueueSnackbar(`${selectedContacts.length} contactos adicionados ao grupo "${groupName}"!`, { variant: 'success' });
  };

  const handleImportContacts = (file: File) => {
    // Simular importação
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const csv = e.target?.result as string;
        const lines = csv.split('\n');
        const headers = lines[0].split(',');
        
        const newContacts: ContactData[] = [];
        const errors: string[] = [];

        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',');
          if (values.length >= 2) {
            const newContact: ContactData = {
              id: contacts.length + newContacts.length + 1,
              name: values[0]?.trim() || 'Sem Nome',
              phone: values[1]?.trim() || '',
              email: values[2]?.trim(),
              company: values[3]?.trim(),
              location: values[4]?.trim(),
              tags: [],
              groups: ['Importados'],
              status: 'active',
              sms_sent: 0,
              sms_received: 0,
              created_at: new Date(),
              updated_at: new Date(),
              custom_fields: {},
            };
            newContacts.push(newContact);
          } else {
            errors.push(`Linha ${i + 1}: Formato inválido`);
          }
        }

        setContacts([...contacts, ...newContacts]);
        enqueueSnackbar(`${newContacts.length} contactos importados com sucesso!`, { variant: 'success' });
        
        if (errors.length > 0) {
          console.warn('Erros na importação:', errors);
        }
      } catch (error) {
        enqueueSnackbar('Erro ao importar contactos!', { variant: 'error' });
      }
    };
    reader.readAsText(file);
    setIsImportDialogOpen(false);
  };

  const handleExportContacts = () => {
    const csv = [
      'Nome,Telefone,Email,Empresa,Posição,Localização,Tags,Grupos,Status',
      ...contacts.map(contact => [
        contact.name,
        contact.phone,
        contact.email || '',
        contact.company || '',
        contact.position || '',
        contact.location || '',
        contact.tags.join(';'),
        contact.groups.join(';'),
        contact.status,
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contactos-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const filteredContacts = contacts.filter(contact => {
    const matchesSearch = contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.phone.includes(searchTerm) ||
                         contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.company?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesGroup = filterGroup === 'all' || contact.groups.includes(filterGroup);
    const matchesStatus = filterStatus === 'all' || contact.status === filterStatus;
    
    return matchesSearch && matchesGroup && matchesStatus;
  });

  const contactStats = {
    total: contacts.length,
    active: contacts.filter(c => c.status === 'active').length,
    inactive: contacts.filter(c => c.status === 'inactive').length,
    blocked: contacts.filter(c => c.status === 'blocked').length,
    total_groups: groups.length,
    recent_contacts: contacts.filter(c => {
      const daysDiff = (new Date().getTime() - c.created_at.getTime()) / (1000 * 3600 * 24);
      return daysDiff <= 7;
    }).length,
  };

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Contacto',
      width: 200,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <Avatar sx={{ width: 32, height: 32, mr: 1, fontSize: '0.8rem' }}>
            {params.row.name.split(' ').map((n: string) => n[0]).join('')}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="bold">
              {params.row.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.phone}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'company',
      headerName: 'Empresa',
      width: 150,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2">
            {params.row.company || '-'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {params.row.position || ''}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'location',
      headerName: 'Localização',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.row.location || '-'}
        </Typography>
      ),
    },
    {
      field: 'tags',
      headerName: 'Tags',
      width: 200,
      renderCell: (params) => (
        <Box display="flex" gap={0.5} flexWrap="wrap">
          {params.row.tags.slice(0, 2).map((tag: string) => (
            <Chip
              key={tag}
              label={tag}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.7rem', height: 20 }}
            />
          ))}
          {params.row.tags.length > 2 && (
            <Chip
              label={`+${params.row.tags.length - 2}`}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.7rem', height: 20 }}
            />
          )}
        </Box>
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={getStatusLabel(params.value)}
          color={getStatusColor(params.value) as any}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'sms_stats',
      headerName: 'SMS',
      width: 120,
      renderCell: (params) => (
        <Box>
          <Typography variant="caption" color="success.main">
            ↑ {params.row.sms_sent}
          </Typography>
          <br />
          <Typography variant="caption" color="info.main">
            ↓ {params.row.sms_received}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'last_contact',
      headerName: 'Último Contacto',
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.row.last_contact 
            ? new Date(params.row.last_contact).toLocaleDateString('pt-PT')
            : 'Nunca'
          }
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
          <IconButton
            size="small"
            onClick={() => handleEditContact(params.row)}
            title="Editar"
          >
            <Edit fontSize="small" />
          </IconButton>
          
          <IconButton
            size="small"
            color="success"
            title="Enviar SMS"
          >
            <Send fontSize="small" />
          </IconButton>

          <IconButton
            size="small"
            onClick={() => handleDeleteContact(params.row)}
            color="error"
            title="Eliminar"
          >
            <Delete fontSize="small" />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Gestão de Contactos
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Organize e gerencie todos os seus contactos empresariais
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<Upload />} onClick={() => setIsImportDialogOpen(true)}>
            Importar
          </Button>
          <Button variant="outlined" startIcon={<Download />} onClick={handleExportContacts}>
            Exportar
          </Button>
          <Button variant="outlined" startIcon={<Group />} onClick={() => setIsGroupDialogOpen(true)}>
            Grupos
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            Novo Contacto
          </Button>
        </Box>
      </Box>

      {/* Estatísticas */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Contactos
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {contactStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Ativos
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {contactStats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Inativos
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="warning.main">
                {contactStats.inactive}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Grupos
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="info.main">
                {contactStats.total_groups}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Novos (7 dias)
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="primary.main">
                {contactStats.recent_contacts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Ações em massa */}
      {selectedContacts.length > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography>
              {selectedContacts.length} contactos selecionados
            </Typography>
            <Box>
              <Button size="small" onClick={handleBulkDelete} color="error">
                Eliminar
              </Button>
              <Button size="small" onClick={() => setIsBulkActionDialogOpen(true)}>
                Adicionar ao Grupo
              </Button>
              <Button size="small">
                Enviar SMS
              </Button>
            </Box>
          </Box>
        </Alert>
      )}

      {/* Filtros e Pesquisa */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Pesquisar contactos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
                size="small"
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Filtrar por Grupo</InputLabel>
                <Select
                  value={filterGroup}
                  onChange={(e) => setFilterGroup(e.target.value)}
                  label="Filtrar por Grupo"
                >
                  <MenuItem value="all">Todos os Grupos</MenuItem>
                  {groups.map(group => (
                    <MenuItem key={group.id} value={group.name}>
                      {group.name} ({group.contacts_count})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Filtrar por Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Filtrar por Status"
                >
                  <MenuItem value="all">Todos os Status</MenuItem>
                  <MenuItem value="active">Ativo</MenuItem>
                  <MenuItem value="inactive">Inativo</MenuItem>
                  <MenuItem value="blocked">Bloqueado</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <Button fullWidth variant="outlined" startIcon={<Analytics />}>
                Relatórios
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabela de Contactos */}
      <Card>
        <CardContent>
          <Box sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={filteredContacts}
              columns={columns}
              loading={loading}
              pageSize={25}
              rowsPerPageOptions={[10, 25, 50, 100]}
              checkboxSelection
              disableSelectionOnClick
              selectionModel={selectedContacts}
              onSelectionModelChange={(newSelection) => {
                setSelectedContacts(newSelection);
              }}
              sx={{
                '& .MuiDataGrid-root': {
                  border: 'none',
                },
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Dialog de Criação/Edição */}
      <Dialog
        open={isCreateDialogOpen || isEditDialogOpen}
        onClose={() => {
          setIsCreateDialogOpen(false);
          setIsEditDialogOpen(false);
          setSelectedContact(null);
          reset();
        }}
        maxWidth="md"
        fullWidth
      >
        <form onSubmit={handleSubmit(isCreateDialogOpen ? handleCreateContact : handleUpdateContact)}>
          <DialogTitle>
            {isCreateDialogOpen ? 'Criar Novo Contacto' : 'Editar Contacto'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="name"
                  control={control}
                  rules={{ required: 'Nome é obrigatório' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Nome Completo"
                      error={!!errors.name}
                      helperText={errors.name?.message}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Person />
                          </InputAdornment>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="phone"
                  control={control}
                  rules={{ required: 'Telefone é obrigatório' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Telefone"
                      placeholder="+258 XX XXX XXXX"
                      error={!!errors.phone}
                      helperText={errors.phone?.message}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Phone />
                          </InputAdornment>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="email"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Email"
                      type="email"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Email />
                          </InputAdornment>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="location"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Localização"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LocationOn />
                          </InputAdornment>
                        ),
                      }}
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
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Business />
                          </InputAdornment>
                        ),
                      }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="position"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Posição/Cargo"
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="tags"
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      {...field}
                      multiple
                      options={availableTags}
                      freeSolo
                      value={field.value || []}
                      onChange={(_, newValue) => field.onChange(newValue)}
                      renderTags={(value, getTagProps) =>
                        value.map((option, index) => (
                          <Chip
                            variant="outlined"
                            label={option}
                            {...getTagProps({ index })}
                          />
                        ))
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Tags"
                          placeholder="Adicionar tags..."
                        />
                      )}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="groups"
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      {...field}
                      multiple
                      options={groups.map(g => g.name)}
                      value={field.value || []}
                      onChange={(_, newValue) => field.onChange(newValue)}
                      renderTags={(value, getTagProps) =>
                        value.map((option, index) => (
                          <Chip
                            variant="outlined"
                            label={option}
                            {...getTagProps({ index })}
                          />
                        ))
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Grupos"
                          placeholder="Selecionar grupos..."
                        />
                      )}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Controller
                  name="notes"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Notas"
                      multiline
                      rows={3}
                      placeholder="Adicionar notas sobre este contacto..."
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setIsCreateDialogOpen(false);
              setIsEditDialogOpen(false);
              setSelectedContact(null);
              reset();
            }}>
              Cancelar
            </Button>
            <Button type="submit" variant="contained">
              {isCreateDialogOpen ? 'Criar Contacto' : 'Atualizar Contacto'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Dialog de Importação */}
      <Dialog
        open={isImportDialogOpen}
        onClose={() => setIsImportDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Importar Contactos</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Selecione um arquivo CSV com os contactos. O formato deve ser:
          </Typography>
          <Typography variant="caption" component="pre" sx={{ bgcolor: 'grey.100', p: 1, borderRadius: 1, display: 'block', mt: 1 }}>
Nome,Telefone,Email,Empresa,Localização{'\n'}
João Silva,+258841234567,joao@email.com,Tech Corp,Maputo
          </Typography>
          
          <Box sx={{ mt: 3 }}>
            <input
              type="file"
              accept=".csv,.txt"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  handleImportContacts(file);
                }
              }}
              style={{ display: 'none' }}
              id="csv-upload"
            />
            <label htmlFor="csv-upload">
              <Button
                component="span"
                variant="outlined"
                startIcon={<Upload />}
                fullWidth
              >
                Selecionar Arquivo CSV
              </Button>
            </label>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsImportDialogOpen(false)}>
            Cancelar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Fab para ação rápida */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => setIsCreateDialogOpen(true)}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default ContactManagementPage;
