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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Avatar,
  LinearProgress,
  Menu,
  Alert,
  Fab,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  PlayArrow,
  Pause,
  Stop,
  Schedule,
  Send,
  Group,
  Analytics,
  FilterList,
  Download,
  MoreVert,
  Campaign,
  Preview,
  CheckCircle,
  Error,
  Warning,
  Pending,
} from '@mui/icons-material';
import { DataGrid, GridColDef, GridRowsProp } from '@mui/x-data-grid';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useForm, Controller } from 'react-hook-form';
import { useSnackbar } from 'notistack';

interface CampaignData {
  id: number;
  name: string;
  description: string;
  type: 'promotional' | 'informational' | 'transactional' | 'support';
  status: 'draft' | 'scheduled' | 'active' | 'paused' | 'completed' | 'cancelled';
  message: string;
  target_audience: string;
  contacts_count: number;
  sent_count: number;
  delivered_count: number;
  failed_count: number;
  budget: number;
  cost_per_sms: number;
  scheduled_at: Date | null;
  created_by: string;
  created_at: Date;
  updated_at: Date;
  approval_status: 'pending' | 'approved' | 'rejected';
  approver?: string;
}

interface CampaignFormData {
  name: string;
  description: string;
  type: 'promotional' | 'informational' | 'transactional' | 'support';
  message: string;
  target_audience: string;
  budget: number;
  scheduled_at: Date | null;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

const CampaignManagementPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignData[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignData | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isPreviewDialogOpen, setIsPreviewDialogOpen] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const { enqueueSnackbar } = useSnackbar();
  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<CampaignFormData>();

  const messageLength = watch('message')?.length || 0;
  const maxMessageLength = 160;

  // Dados simulados de campanhas
  const mockCampaigns: CampaignData[] = [
    {
      id: 1,
      name: 'Promoção Fim de Semana',
      description: 'Campanha promocional para produtos em destaque',
      type: 'promotional',
      status: 'active',
      message: 'Oferta especial! 50% de desconto em todos os produtos. Use código FIMDESEMANA. Válido até domingo.',
      target_audience: 'Clientes Premium',
      contacts_count: 1500,
      sent_count: 850,
      delivered_count: 832,
      failed_count: 18,
      budget: 5000,
      cost_per_sms: 3.5,
      scheduled_at: null,
      created_by: 'Maria Silva',
      created_at: new Date('2024-07-25'),
      updated_at: new Date(),
      approval_status: 'approved',
      approver: 'João Diretor',
    },
    {
      id: 2,
      name: 'Lembrete de Pagamento',
      description: 'Lembretes automáticos para pagamentos em atraso',
      type: 'transactional',
      status: 'completed',
      message: 'Prezado cliente, sua fatura vence hoje. Evite juros, pague através do nosso app.',
      target_audience: 'Devedores',
      contacts_count: 2500,
      sent_count: 2500,
      delivered_count: 2478,
      failed_count: 22,
      budget: 8750,
      cost_per_sms: 3.5,
      scheduled_at: null,
      created_by: 'João Santos',
      created_at: new Date('2024-07-20'),
      updated_at: new Date('2024-07-22'),
      approval_status: 'approved',
      approver: 'Ana Gerente',
    },
    {
      id: 3,
      name: 'Novo Produto - Lançamento',
      description: 'Anúncio do lançamento do novo produto da empresa',
      type: 'informational',
      status: 'scheduled',
      message: 'Em breve! Novo produto revolucionário chegando. Seja o primeiro a conhecer em www.empresa.com/novo',
      target_audience: 'Todos os Clientes',
      contacts_count: 5000,
      sent_count: 0,
      delivered_count: 0,
      failed_count: 0,
      budget: 17500,
      cost_per_sms: 3.5,
      scheduled_at: new Date(Date.now() + 86400000), // Amanhã
      created_by: 'Ana Costa',
      created_at: new Date('2024-07-26'),
      updated_at: new Date('2024-07-26'),
      approval_status: 'approved',
      approver: 'João Diretor',
    },
    {
      id: 4,
      name: 'Pesquisa de Satisfação',
      description: 'Pesquisa para avaliar satisfação dos clientes',
      type: 'support',
      status: 'draft',
      message: 'Como foi sua experiência conosco? Avalie de 1 a 5 respondendo a esta mensagem. Sua opinião é importante!',
      target_audience: 'Clientes Recentes',
      contacts_count: 800,
      sent_count: 0,
      delivered_count: 0,
      failed_count: 0,
      budget: 2800,
      cost_per_sms: 3.5,
      scheduled_at: null,
      created_by: 'Carlos Mendes',
      created_at: new Date('2024-07-27'),
      updated_at: new Date('2024-07-27'),
      approval_status: 'pending',
    },
    {
      id: 5,
      name: 'Black Friday - Prévia',
      description: 'Campanha de aquecimento para Black Friday',
      type: 'promotional',
      status: 'paused',
      message: 'ATENÇÃO! Black Friday chegando. Prepare-se para as melhores ofertas do ano. Fique ligado!',
      target_audience: 'Clientes VIP',
      contacts_count: 3200,
      sent_count: 1800,
      delivered_count: 1765,
      failed_count: 35,
      budget: 11200,
      cost_per_sms: 3.5,
      scheduled_at: null,
      created_by: 'Pedro Alves',
      created_at: new Date('2024-07-24'),
      updated_at: new Date('2024-07-26'),
      approval_status: 'approved',
      approver: 'Maria Diretora',
    },
  ];

  useEffect(() => {
    // Simular carregamento
    setTimeout(() => {
      setCampaigns(mockCampaigns);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'info';
      case 'scheduled': return 'warning';
      case 'paused': return 'default';
      case 'draft': return 'default';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Ativa';
      case 'completed': return 'Concluída';
      case 'scheduled': return 'Agendada';
      case 'paused': return 'Pausada';
      case 'draft': return 'Rascunho';
      case 'cancelled': return 'Cancelada';
      default: return status;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'promotional': return 'Promocional';
      case 'informational': return 'Informativa';
      case 'transactional': return 'Transacional';
      case 'support': return 'Suporte';
      default: return type;
    }
  };

  const getApprovalColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getApprovalLabel = (status: string) => {
    switch (status) {
      case 'approved': return 'Aprovada';
      case 'pending': return 'Pendente';
      case 'rejected': return 'Rejeitada';
      default: return status;
    }
  };

  const handleCreateCampaign = (data: CampaignFormData) => {
    const newCampaign: CampaignData = {
      id: campaigns.length + 1,
      ...data,
      status: 'draft',
      contacts_count: 0, // Será calculado baseado no target_audience
      sent_count: 0,
      delivered_count: 0,
      failed_count: 0,
      cost_per_sms: 3.5,
      created_by: 'Utilizador Atual', // Pegar do contexto
      created_at: new Date(),
      updated_at: new Date(),
      approval_status: 'pending',
    };

    setCampaigns([...campaigns, newCampaign]);
    setIsCreateDialogOpen(false);
    reset();
    enqueueSnackbar('Campanha criada com sucesso!', { variant: 'success' });
  };

  const handleEditCampaign = (campaign: CampaignData) => {
    setSelectedCampaign(campaign);
    reset({
      name: campaign.name,
      description: campaign.description,
      type: campaign.type,
      message: campaign.message,
      target_audience: campaign.target_audience,
      budget: campaign.budget,
      scheduled_at: campaign.scheduled_at,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateCampaign = (data: CampaignFormData) => {
    if (!selectedCampaign) return;

    const updatedCampaigns = campaigns.map(campaign =>
      campaign.id === selectedCampaign.id
        ? {
            ...campaign,
            ...data,
            updated_at: new Date(),
            approval_status: 'pending' as const, // Requer nova aprovação
          }
        : campaign
    );

    setCampaigns(updatedCampaigns);
    setIsEditDialogOpen(false);
    setSelectedCampaign(null);
    reset();
    enqueueSnackbar('Campanha atualizada com sucesso!', { variant: 'success' });
  };

  const handleDeleteCampaign = (campaign: CampaignData) => {
    if (window.confirm(`Tem certeza que deseja eliminar a campanha "${campaign.name}"?`)) {
      const updatedCampaigns = campaigns.filter(c => c.id !== campaign.id);
      setCampaigns(updatedCampaigns);
      enqueueSnackbar('Campanha eliminada com sucesso!', { variant: 'success' });
    }
  };

  const handleStartCampaign = (campaign: CampaignData) => {
    const updatedCampaigns = campaigns.map(c =>
      c.id === campaign.id ? { ...c, status: 'active' as const } : c
    );
    setCampaigns(updatedCampaigns);
    enqueueSnackbar(`Campanha "${campaign.name}" iniciada!`, { variant: 'success' });
  };

  const handlePauseCampaign = (campaign: CampaignData) => {
    const updatedCampaigns = campaigns.map(c =>
      c.id === campaign.id ? { ...c, status: 'paused' as const } : c
    );
    setCampaigns(updatedCampaigns);
    enqueueSnackbar(`Campanha "${campaign.name}" pausada!`, { variant: 'info' });
  };

  const handleStopCampaign = (campaign: CampaignData) => {
    if (window.confirm(`Tem certeza que deseja parar a campanha "${campaign.name}"?`)) {
      const updatedCampaigns = campaigns.map(c =>
        c.id === campaign.id ? { ...c, status: 'cancelled' as const } : c
      );
      setCampaigns(updatedCampaigns);
      enqueueSnackbar(`Campanha "${campaign.name}" cancelada!`, { variant: 'warning' });
    }
  };

  const handlePreviewCampaign = (campaign: CampaignData) => {
    setSelectedCampaign(campaign);
    setIsPreviewDialogOpen(true);
  };

  const filteredCampaigns = campaigns.filter(campaign => {
    if (filterStatus === 'all') return true;
    return campaign.status === filterStatus;
  });

  const campaignStats = {
    total: campaigns.length,
    active: campaigns.filter(c => c.status === 'active').length,
    scheduled: campaigns.filter(c => c.status === 'scheduled').length,
    completed: campaigns.filter(c => c.status === 'completed').length,
    pending_approval: campaigns.filter(c => c.approval_status === 'pending').length,
    total_sent: campaigns.reduce((sum, c) => sum + c.sent_count, 0),
    total_budget: campaigns.reduce((sum, c) => sum + c.budget, 0),
  };

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Campanha',
      width: 200,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="bold">
            {params.row.name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {getTypeLabel(params.row.type)}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
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
      field: 'approval_status',
      headerName: 'Aprovação',
      width: 130,
      renderCell: (params) => (
        <Chip
          label={getApprovalLabel(params.value)}
          color={getApprovalColor(params.value) as any}
          size="small"
          variant="filled"
        />
      ),
    },
    {
      field: 'contacts_count',
      headerName: 'Contactos',
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value.toLocaleString()}
        </Typography>
      ),
    },
    {
      field: 'progress',
      headerName: 'Progresso',
      width: 150,
      renderCell: (params) => {
        const progress = params.row.contacts_count > 0 
          ? (params.row.sent_count / params.row.contacts_count) * 100 
          : 0;
        return (
          <Box sx={{ width: '100%' }}>
            <Typography variant="caption">
              {params.row.sent_count} / {params.row.contacts_count}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{ mt: 0.5, height: 4, borderRadius: 2 }}
            />
          </Box>
        );
      },
    },
    {
      field: 'budget',
      headerName: 'Orçamento',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value.toLocaleString()} MT
        </Typography>
      ),
    },
    {
      field: 'created_by',
      headerName: 'Criado por',
      width: 150,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <Avatar sx={{ width: 28, height: 28, mr: 1, fontSize: '0.75rem' }}>
            {params.value.split(' ').map((n: string) => n[0]).join('')}
          </Avatar>
          <Typography variant="body2">
            {params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'actions',
      headerName: 'Ações',
      width: 200,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handlePreviewCampaign(params.row)}
            title="Pré-visualizar"
          >
            <Preview fontSize="small" />
          </IconButton>
          
          <IconButton
            size="small"
            onClick={() => handleEditCampaign(params.row)}
            title="Editar"
          >
            <Edit fontSize="small" />
          </IconButton>

          {params.row.status === 'draft' || params.row.status === 'scheduled' ? (
            <IconButton
              size="small"
              onClick={() => handleStartCampaign(params.row)}
              color="success"
              title="Iniciar"
            >
              <PlayArrow fontSize="small" />
            </IconButton>
          ) : params.row.status === 'active' ? (
            <IconButton
              size="small"
              onClick={() => handlePauseCampaign(params.row)}
              color="warning"
              title="Pausar"
            >
              <Pause fontSize="small" />
            </IconButton>
          ) : null}

          {(params.row.status === 'active' || params.row.status === 'paused') && (
            <IconButton
              size="small"
              onClick={() => handleStopCampaign(params.row)}
              color="error"
              title="Parar"
            >
              <Stop fontSize="small" />
            </IconButton>
          )}

          <IconButton
            size="small"
            onClick={() => handleDeleteCampaign(params.row)}
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
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h3" fontWeight="bold" gutterBottom>
              Gestão de Campanhas
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Crie, gerencie e monitore todas as suas campanhas de SMS
            </Typography>
          </Box>
          
          <Box display="flex" gap={1}>
            <Button variant="outlined" startIcon={<Analytics />}>
              Relatórios
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setIsCreateDialogOpen(true)}
            >
              Nova Campanha
            </Button>
          </Box>
        </Box>

        {/* Alertas */}
        {campaignStats.pending_approval > 0 && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            Tem {campaignStats.pending_approval} campanhas pendentes de aprovação.
          </Alert>
        )}

        {/* Estatísticas */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total de Campanhas
                </Typography>
                <Typography variant="h4" fontWeight="bold">
                  {campaignStats.total}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Campanhas Ativas
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {campaignStats.active}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Enviados
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="primary.main">
                  {campaignStats.total_sent.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Orçamento Total
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="info.main">
                  {campaignStats.total_budget.toLocaleString()} MT
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filtros e Tabs */}
        <Card sx={{ mb: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
              <Tab icon={<Campaign />} label="Todas" />
              <Tab icon={<PlayArrow />} label="Ativas" />
              <Tab icon={<Schedule />} label="Agendadas" />
              <Tab icon={<CheckCircle />} label="Concluídas" />
              <Tab icon={<Pending />} label="Pendentes" />
            </Tabs>
          </Box>

          <CardContent>
            <Box display="flex" gap={2} alignItems="center" mb={2}>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Filtrar Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Filtrar Status"
                >
                  <MenuItem value="all">Todos</MenuItem>
                  <MenuItem value="active">Ativas</MenuItem>
                  <MenuItem value="scheduled">Agendadas</MenuItem>
                  <MenuItem value="completed">Concluídas</MenuItem>
                  <MenuItem value="draft">Rascunhos</MenuItem>
                </Select>
              </FormControl>
              
              <Button startIcon={<Download />} variant="outlined" size="small">
                Exportar
              </Button>
            </Box>

            {/* Tabela de Campanhas */}
            <Box sx={{ height: 600, width: '100%' }}>
              <DataGrid
                rows={filteredCampaigns}
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
          </CardContent>
        </Card>

        {/* Dialog de Criação */}
        <Dialog
          open={isCreateDialogOpen}
          onClose={() => setIsCreateDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <form onSubmit={handleSubmit(handleCreateCampaign)}>
            <DialogTitle>Criar Nova Campanha</DialogTitle>
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
                        label="Nome da Campanha"
                        error={!!errors.name}
                        helperText={errors.name?.message}
                      />
                    )}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Controller
                    name="type"
                    control={control}
                    rules={{ required: 'Tipo é obrigatório' }}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.type}>
                        <InputLabel>Tipo de Campanha</InputLabel>
                        <Select {...field} label="Tipo de Campanha">
                          <MenuItem value="promotional">Promocional</MenuItem>
                          <MenuItem value="informational">Informativa</MenuItem>
                          <MenuItem value="transactional">Transacional</MenuItem>
                          <MenuItem value="support">Suporte</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Controller
                    name="description"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Descrição"
                        multiline
                        rows={2}
                      />
                    )}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Controller
                    name="message"
                    control={control}
                    rules={{ 
                      required: 'Mensagem é obrigatória',
                      maxLength: { value: maxMessageLength, message: `Máximo ${maxMessageLength} caracteres` }
                    }}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Mensagem SMS"
                        multiline
                        rows={3}
                        error={!!errors.message}
                        helperText={
                          errors.message?.message || 
                          `${messageLength}/${maxMessageLength} caracteres`
                        }
                      />
                    )}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Controller
                    name="target_audience"
                    control={control}
                    rules={{ required: 'Público-alvo é obrigatório' }}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.target_audience}>
                        <InputLabel>Público-alvo</InputLabel>
                        <Select {...field} label="Público-alvo">
                          <MenuItem value="Todos os Clientes">Todos os Clientes</MenuItem>
                          <MenuItem value="Clientes Premium">Clientes Premium</MenuItem>
                          <MenuItem value="Clientes VIP">Clientes VIP</MenuItem>
                          <MenuItem value="Novos Clientes">Novos Clientes</MenuItem>
                          <MenuItem value="Clientes Inativos">Clientes Inativos</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Controller
                    name="budget"
                    control={control}
                    rules={{ required: 'Orçamento é obrigatório', min: { value: 1, message: 'Orçamento deve ser maior que 0' } }}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Orçamento (MT)"
                        type="number"
                        error={!!errors.budget}
                        helperText={errors.budget?.message}
                      />
                    )}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Controller
                    name="scheduled_at"
                    control={control}
                    render={({ field }) => (
                      <DateTimePicker
                        {...field}
                        label="Agendar Envio (Opcional)"
                        renderInput={(props) => <TextField {...props} fullWidth />}
                        minDateTime={new Date()}
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
                Criar Campanha
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Dialog de Pré-visualização */}
        <Dialog
          open={isPreviewDialogOpen}
          onClose={() => setIsPreviewDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          {selectedCampaign && (
            <>
              <DialogTitle>
                Pré-visualização: {selectedCampaign.name}
              </DialogTitle>
              <DialogContent>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Tipo: {getTypeLabel(selectedCampaign.type)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {selectedCampaign.description}
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.100', borderRadius: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Mensagem SMS:
                  </Typography>
                  <Typography variant="body2">
                    {selectedCampaign.message}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedCampaign.message.length} caracteres
                  </Typography>
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Público-alvo:</Typography>
                    <Typography variant="body2">{selectedCampaign.target_audience}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Contactos:</Typography>
                    <Typography variant="body2">{selectedCampaign.contacts_count.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Orçamento:</Typography>
                    <Typography variant="body2">{selectedCampaign.budget.toLocaleString()} MT</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Custo estimado:</Typography>
                    <Typography variant="body2">
                      {(selectedCampaign.contacts_count * selectedCampaign.cost_per_sms).toLocaleString()} MT
                    </Typography>
                  </Grid>
                </Grid>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setIsPreviewDialogOpen(false)}>
                  Fechar
                </Button>
                {selectedCampaign.status === 'draft' && (
                  <Button
                    variant="contained"
                    startIcon={<Send />}
                    onClick={() => {
                      handleStartCampaign(selectedCampaign);
                      setIsPreviewDialogOpen(false);
                    }}
                  >
                    Enviar Agora
                  </Button>
                )}
              </DialogActions>
            </>
          )}
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
    </LocalizationProvider>
  );
};

export default CampaignManagementPage;
