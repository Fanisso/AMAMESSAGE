import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
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
  Alert,
  LinearProgress,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Refresh,
  PlayArrow,
  Stop,
  Settings,
  NetworkCheck,
  Smartphone,
  Computer,
  Router,
  Signal,
  Battery,
  SimCard,
  Warning,
  CheckCircle,
  Error,
  WifiOff,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { useSnackbar } from 'notistack';

interface ModemDevice {
  id: number;
  name: string;
  type: 'usb_modem' | 'gsm_module' | 'virtual_modem' | 'sim_card_reader';
  port: string;
  baudrate: number;
  status: 'online' | 'offline' | 'error' | 'connecting';
  signal_strength: number; // 0-100
  network_operator: string;
  sim_card_status: 'active' | 'inactive' | 'missing' | 'locked';
  balance: number | null; // Saldo do cartão (se aplicável)
  last_activity: Date;
  messages_sent_today: number;
  messages_failed_today: number;
  auto_start: boolean;
  max_concurrent_sms: number;
  created_at: Date;
  updated_at: Date;
}

interface ModemFormData {
  name: string;
  type: 'usb_modem' | 'gsm_module' | 'virtual_modem' | 'sim_card_reader';
  port: string;
  baudrate: number;
  auto_start: boolean;
  max_concurrent_sms: number;
}

const HardwareManagementPage: React.FC = () => {
  const [modems, setModems] = useState<ModemDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModem, setSelectedModem] = useState<ModemDevice | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDetailsDialogOpen, setIsDetailsDialogOpen] = useState(false);
  const [scanning, setScanning] = useState(false);

  const { enqueueSnackbar } = useSnackbar();
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ModemFormData>();

  // Dados simulados de modems
  const mockModems: ModemDevice[] = [
    {
      id: 1,
      name: 'Modem USB Principal',
      type: 'usb_modem',
      port: 'COM3',
      baudrate: 9600,
      status: 'online',
      signal_strength: 85,
      network_operator: 'Vodacom',
      sim_card_status: 'active',
      balance: 125.50,
      last_activity: new Date(),
      messages_sent_today: 234,
      messages_failed_today: 3,
      auto_start: true,
      max_concurrent_sms: 5,
      created_at: new Date('2024-01-15'),
      updated_at: new Date(),
    },
    {
      id: 2,
      name: 'Modem GSM Secundário',
      type: 'gsm_module',
      port: 'COM4',
      baudrate: 115200,
      status: 'offline',
      signal_strength: 0,
      network_operator: '',
      sim_card_status: 'missing',
      balance: null,
      last_activity: new Date(Date.now() - 3600000),
      messages_sent_today: 0,
      messages_failed_today: 15,
      auto_start: false,
      max_concurrent_sms: 3,
      created_at: new Date('2024-02-10'),
      updated_at: new Date(Date.now() - 3600000),
    },
    {
      id: 3,
      name: 'Leitor SIM Backup',
      type: 'sim_card_reader',
      port: '/dev/ttyUSB0',
      baudrate: 9600,
      status: 'error',
      signal_strength: 12,
      network_operator: 'mCel',
      sim_card_status: 'locked',
      balance: null,
      last_activity: new Date(Date.now() - 1800000),
      messages_sent_today: 45,
      messages_failed_today: 12,
      auto_start: true,
      max_concurrent_sms: 2,
      created_at: new Date('2024-03-05'),
      updated_at: new Date(Date.now() - 1800000),
    },
    {
      id: 4,
      name: 'Modem Virtual (Twilio)',
      type: 'virtual_modem',
      port: 'virtual://twilio',
      baudrate: 0,
      status: 'online',
      signal_strength: 100,
      network_operator: 'Twilio Cloud',
      sim_card_status: 'active',
      balance: null,
      last_activity: new Date(),
      messages_sent_today: 456,
      messages_failed_today: 1,
      auto_start: true,
      max_concurrent_sms: 50,
      created_at: new Date('2024-01-01'),
      updated_at: new Date(),
    },
  ];

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setModems(mockModems);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'success';
      case 'offline': return 'default';
      case 'error': return 'error';
      case 'connecting': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle color="success" />;
      case 'offline': return <WifiOff color="disabled" />;
      case 'error': return <Error color="error" />;
      case 'connecting': return <NetworkCheck color="warning" />;
      default: return <WifiOff />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'usb_modem': return <Smartphone />;
      case 'gsm_module': return <Router />;
      case 'virtual_modem': return <Computer />;
      case 'sim_card_reader': return <SimCard />;
      default: return <Smartphone />;
    }
  };

  const getSignalBars = (strength: number) => {
    if (strength === 0) return 0;
    if (strength < 25) return 1;
    if (strength < 50) return 2;
    if (strength < 75) return 3;
    return 4;
  };

  const formatBalance = (balance: number | null) => {
    if (balance === null) return 'N/A';
    return `${balance.toFixed(2)} MT`;
  };

  const handleCreateModem = (data: ModemFormData) => {
    const newModem: ModemDevice = {
      id: modems.length + 1,
      ...data,
      status: 'offline',
      signal_strength: 0,
      network_operator: '',
      sim_card_status: 'inactive',
      balance: null,
      last_activity: new Date(),
      messages_sent_today: 0,
      messages_failed_today: 0,
      created_at: new Date(),
      updated_at: new Date(),
    };

    setModems([...modems, newModem]);
    setIsCreateDialogOpen(false);
    reset();
    enqueueSnackbar('Modem adicionado com sucesso!', { variant: 'success' });
  };

  const handleEditModem = (modem: ModemDevice) => {
    setSelectedModem(modem);
    reset({
      name: modem.name,
      type: modem.type,
      port: modem.port,
      baudrate: modem.baudrate,
      auto_start: modem.auto_start,
      max_concurrent_sms: modem.max_concurrent_sms,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateModem = (data: ModemFormData) => {
    if (!selectedModem) return;

    const updatedModems = modems.map(modem =>
      modem.id === selectedModem.id
        ? {
            ...modem,
            ...data,
            updated_at: new Date(),
          }
        : modem
    );

    setModems(updatedModems);
    setIsEditDialogOpen(false);
    setSelectedModem(null);
    reset();
    enqueueSnackbar('Modem atualizado com sucesso!', { variant: 'success' });
  };

  const handleDeleteModem = (modem: ModemDevice) => {
    if (window.confirm(`Tem certeza que deseja remover o modem "${modem.name}"?`)) {
      const updatedModems = modems.filter(m => m.id !== modem.id);
      setModems(updatedModems);
      enqueueSnackbar('Modem removido com sucesso!', { variant: 'success' });
    }
  };

  const handleStartModem = (modem: ModemDevice) => {
    const updatedModems = modems.map(m =>
      m.id === modem.id
        ? { ...m, status: 'connecting' as const }
        : m
    );
    setModems(updatedModems);

    // Simular conexão
    setTimeout(() => {
      const finalModems = modems.map(m =>
        m.id === modem.id
          ? {
              ...m,
              status: 'online' as const,
              signal_strength: Math.floor(Math.random() * 100),
              network_operator: ['Vodacom', 'mCel', 'Movitel'][Math.floor(Math.random() * 3)],
              sim_card_status: 'active' as const,
              last_activity: new Date(),
            }
          : m
      );
      setModems(finalModems);
      enqueueSnackbar(`Modem "${modem.name}" iniciado com sucesso!`, { variant: 'success' });
    }, 2000);
  };

  const handleStopModem = (modem: ModemDevice) => {
    const updatedModems = modems.map(m =>
      m.id === modem.id
        ? {
            ...m,
            status: 'offline' as const,
            signal_strength: 0,
            network_operator: '',
            sim_card_status: 'inactive' as const,
          }
        : m
    );
    setModems(updatedModems);
    enqueueSnackbar(`Modem "${modem.name}" parado!`, { variant: 'info' });
  };

  const handleScanModems = () => {
    setScanning(true);
    enqueueSnackbar('Procurando novos modems...', { variant: 'info' });

    // Simular scan
    setTimeout(() => {
      setScanning(false);
      enqueueSnackbar('Scan concluído. Nenhum novo modem encontrado.', { variant: 'info' });
    }, 3000);
  };

  const handleTestModem = (modem: ModemDevice) => {
    enqueueSnackbar(`Testando modem "${modem.name}"...`, { variant: 'info' });

    // Simular teste
    setTimeout(() => {
      const success = modem.status === 'online';
      enqueueSnackbar(
        `Teste do modem "${modem.name}": ${success ? 'Sucesso' : 'Falha'}`,
        { variant: success ? 'success' : 'error' }
      );
    }, 1500);
  };

  const totalStats = {
    total: modems.length,
    online: modems.filter(m => m.status === 'online').length,
    offline: modems.filter(m => m.status === 'offline').length,
    errors: modems.filter(m => m.status === 'error').length,
    messagesSent: modems.reduce((sum, m) => sum + m.messages_sent_today, 0),
    messagesFailed: modems.reduce((sum, m) => sum + m.messages_failed_today, 0),
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Gestão de Hardware
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Administração de modems, dispositivos GSM e equipamentos físicos
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleScanModems}
            disabled={scanning}
          >
            {scanning ? 'Procurando...' : 'Scan Modems'}
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            Adicionar Modem
          </Button>
        </Box>
      </Box>

      {/* Estatísticas */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total de Modems
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {totalStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Modems Online
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {totalStats.online}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                SMS Enviados Hoje
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="primary.main">
                {totalStats.messagesSent}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                SMS Falharam
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="error.main">
                {totalStats.messagesFailed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Lista de Modems */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Dispositivos Cadastrados
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Dispositivo</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Sinal</TableCell>
                  <TableCell>Operadora</TableCell>
                  <TableCell>SIM</TableCell>
                  <TableCell>SMS Hoje</TableCell>
                  <TableCell>Saldo</TableCell>
                  <TableCell>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {modems.map((modem) => (
                  <TableRow key={modem.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getTypeIcon(modem.type)}
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {modem.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {modem.port} • {modem.baudrate} baud
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getStatusIcon(modem.status)}
                        <Chip
                          label={modem.status.toUpperCase()}
                          color={getStatusColor(modem.status) as any}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Signal />
                        <Box>
                          <Typography variant="body2">
                            {modem.signal_strength}%
                          </Typography>
                          <Box display="flex" gap={0.5}>
                            {[1, 2, 3, 4].map((i) => (
                              <Box
                                key={i}
                                width={4}
                                height={8 + i * 2}
                                bgcolor={
                                  i <= getSignalBars(modem.signal_strength)
                                    ? 'primary.main'
                                    : 'grey.300'
                                }
                                borderRadius={0.5}
                              />
                            ))}
                          </Box>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {modem.network_operator || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={modem.sim_card_status.toUpperCase()}
                        color={modem.sim_card_status === 'active' ? 'success' : 'error'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" color="success.main">
                          ✓ {modem.messages_sent_today}
                        </Typography>
                        <Typography variant="body2" color="error.main">
                          ✗ {modem.messages_failed_today}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatBalance(modem.balance)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5}>
                        {modem.status === 'online' ? (
                          <Tooltip title="Parar">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleStopModem(modem)}
                            >
                              <Stop />
                            </IconButton>
                          </Tooltip>
                        ) : (
                          <Tooltip title="Iniciar">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleStartModem(modem)}
                            >
                              <PlayArrow />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        <Tooltip title="Testar">
                          <IconButton
                            size="small"
                            onClick={() => handleTestModem(modem)}
                          >
                            <NetworkCheck />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Configurar">
                          <IconButton
                            size="small"
                            onClick={() => handleEditModem(modem)}
                          >
                            <Settings />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Detalhes">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedModem(modem);
                              setIsDetailsDialogOpen(true);
                            }}
                          >
                            <Settings />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Remover">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteModem(modem)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Dialog de criação */}
      <Dialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <form onSubmit={handleSubmit(handleCreateModem)}>
          <DialogTitle>Adicionar Novo Modem</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Controller
                  name="name"
                  control={control}
                  rules={{ required: 'Nome é obrigatório' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Nome do Modem"
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
                      <InputLabel>Tipo de Dispositivo</InputLabel>
                      <Select {...field} label="Tipo de Dispositivo">
                        <MenuItem value="usb_modem">Modem USB</MenuItem>
                        <MenuItem value="gsm_module">Módulo GSM</MenuItem>
                        <MenuItem value="sim_card_reader">Leitor SIM</MenuItem>
                        <MenuItem value="virtual_modem">Modem Virtual</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="port"
                  control={control}
                  rules={{ required: 'Porta é obrigatória' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Porta"
                      placeholder="COM3, /dev/ttyUSB0, virtual://..."
                      error={!!errors.port}
                      helperText={errors.port?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="baudrate"
                  control={control}
                  rules={{ required: 'Baud rate é obrigatório' }}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Baud Rate</InputLabel>
                      <Select {...field} label="Baud Rate">
                        <MenuItem value={9600}>9600</MenuItem>
                        <MenuItem value={19200}>19200</MenuItem>
                        <MenuItem value={38400}>38400</MenuItem>
                        <MenuItem value={57600}>57600</MenuItem>
                        <MenuItem value={115200}>115200</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="max_concurrent_sms"
                  control={control}
                  defaultValue={5}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Máximo SMS Simultâneos"
                      type="number"
                      inputProps={{ min: 1, max: 50 }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Controller
                  name="auto_start"
                  control={control}
                  defaultValue={true}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch {...field} checked={field.value} />}
                      label="Iniciar automaticamente com o sistema"
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
              Adicionar Modem
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
        <form onSubmit={handleSubmit(handleUpdateModem)}>
          <DialogTitle>Configurar Modem</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Controller
                  name="name"
                  control={control}
                  rules={{ required: 'Nome é obrigatório' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Nome do Modem"
                      error={!!errors.name}
                      helperText={errors.name?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="port"
                  control={control}
                  rules={{ required: 'Porta é obrigatória' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Porta"
                      error={!!errors.port}
                      helperText={errors.port?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="baudrate"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Baud Rate</InputLabel>
                      <Select {...field} label="Baud Rate">
                        <MenuItem value={9600}>9600</MenuItem>
                        <MenuItem value={19200}>19200</MenuItem>
                        <MenuItem value={38400}>38400</MenuItem>
                        <MenuItem value={57600}>57600</MenuItem>
                        <MenuItem value={115200}>115200</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="max_concurrent_sms"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Máximo SMS Simultâneos"
                      type="number"
                      inputProps={{ min: 1, max: 50 }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Controller
                  name="auto_start"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch {...field} checked={field.value} />}
                      label="Iniciar automaticamente com o sistema"
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
              Salvar Alterações
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Dialog de detalhes */}
      <Dialog
        open={isDetailsDialogOpen}
        onClose={() => setIsDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedModem && (
          <>
            <DialogTitle>
              Detalhes do Modem: {selectedModem.name}
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Informações Básicas
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2"><strong>Tipo:</strong> {selectedModem.type}</Typography>
                    <Typography variant="body2"><strong>Porta:</strong> {selectedModem.port}</Typography>
                    <Typography variant="body2"><strong>Baud Rate:</strong> {selectedModem.baudrate}</Typography>
                    <Typography variant="body2"><strong>Status:</strong> {selectedModem.status}</Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Rede e SIM
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2"><strong>Operadora:</strong> {selectedModem.network_operator || '-'}</Typography>
                    <Typography variant="body2"><strong>Sinal:</strong> {selectedModem.signal_strength}%</Typography>
                    <Typography variant="body2"><strong>SIM:</strong> {selectedModem.sim_card_status}</Typography>
                    <Typography variant="body2"><strong>Saldo:</strong> {formatBalance(selectedModem.balance)}</Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Estatísticas Hoje
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2" color="success.main">
                      <strong>SMS Enviados:</strong> {selectedModem.messages_sent_today}
                    </Typography>
                    <Typography variant="body2" color="error.main">
                      <strong>SMS Falharam:</strong> {selectedModem.messages_failed_today}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Taxa Sucesso:</strong> {
                        selectedModem.messages_sent_today + selectedModem.messages_failed_today > 0
                          ? ((selectedModem.messages_sent_today / (selectedModem.messages_sent_today + selectedModem.messages_failed_today)) * 100).toFixed(1)
                          : 0
                      }%
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Configurações
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2">
                      <strong>Auto Start:</strong> {selectedModem.auto_start ? 'Sim' : 'Não'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>SMS Simultâneos:</strong> {selectedModem.max_concurrent_sms}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Criado em:</strong> {selectedModem.created_at.toLocaleDateString()}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Última Atividade:</strong> {selectedModem.last_activity.toLocaleString()}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setIsDetailsDialogOpen(false)}>
                Fechar
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default HardwareManagementPage;
