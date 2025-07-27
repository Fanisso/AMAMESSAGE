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
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Divider,
  Paper,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Alert,
  Fab,
  Menu,
  ListItemIcon,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  ContentCopy,
  Preview,
  Send,
  Search,
  FilterList,
  ExpandMore,
  Message,
  Campaign,
  Business,
  Support,
  Info,
  Star,
  StarBorder,
  Schedule,
  PersonAdd,
  Language,
  MoreVert,
  Share,
  Download,
  Analytics,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { useSnackbar } from 'notistack';

interface TemplateData {
  id: number;
  name: string;
  description: string;
  content: string;
  category: 'promotional' | 'informational' | 'transactional' | 'support' | 'welcome' | 'reminder';
  language: string;
  variables: string[];
  usage_count: number;
  is_favorite: boolean;
  is_active: boolean;
  created_by: string;
  created_at: Date;
  updated_at: Date;
  last_used?: Date;
  tags: string[];
  character_count: number;
  estimated_cost: number;
}

interface TemplateFormData {
  name: string;
  description: string;
  content: string;
  category: 'promotional' | 'informational' | 'transactional' | 'support' | 'welcome' | 'reminder';
  language: string;
  tags: string[];
  is_active: boolean;
}

interface TemplateVariable {
  name: string;
  description: string;
  example: string;
  required: boolean;
}

const MessageTemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<TemplateData[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateData | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isPreviewDialogOpen, setIsPreviewDialogOpen] = useState(false);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterLanguage, setFilterLanguage] = useState<string>('all');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedTemplateForMenu, setSelectedTemplateForMenu] = useState<TemplateData | null>(null);

  const { enqueueSnackbar } = useSnackbar();
  const {
    control,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<TemplateFormData>();

  const templateContent = watch('content') || '';
  const maxLength = 160;
  const characterCount = templateContent.length;

  // Variáveis disponíveis para templates
  const availableVariables: TemplateVariable[] = [
    { name: '{{nome}}', description: 'Nome do contacto', example: 'João Silva', required: false },
    { name: '{{empresa}}', description: 'Nome da empresa', example: 'Tech Solutions', required: false },
    { name: '{{produto}}', description: 'Nome do produto', example: 'Software Premium', required: false },
    { name: '{{valor}}', description: 'Valor ou preço', example: '1.500 MT', required: false },
    { name: '{{data}}', description: 'Data atual', example: '27/07/2024', required: false },
    { name: '{{hora}}', description: 'Hora atual', example: '14:30', required: false },
    { name: '{{codigo}}', description: 'Código promocional', example: 'DESC50', required: false },
    { name: '{{link}}', description: 'Link/URL', example: 'https://empresa.com/oferta', required: false },
    { name: '{{telefone}}', description: 'Telefone da empresa', example: '+258 21 123 456', required: false },
    { name: '{{endereco}}', description: 'Endereço da empresa', example: 'Av. Julius Nyerere, Maputo', required: false },
  ];

  // Dados simulados
  const mockTemplates: TemplateData[] = [
    {
      id: 1,
      name: 'Boas-vindas Novo Cliente',
      description: 'Mensagem de boas-vindas para novos clientes',
      content: 'Olá {{nome}}! Bem-vindo à {{empresa}}. Estamos felizes em tê-lo conosco. Para dúvidas: {{telefone}}',
      category: 'welcome',
      language: 'pt',
      variables: ['{{nome}}', '{{empresa}}', '{{telefone}}'],
      usage_count: 245,
      is_favorite: true,
      is_active: true,
      created_by: 'Maria Silva',
      created_at: new Date('2024-01-15'),
      updated_at: new Date('2024-07-20'),
      last_used: new Date('2024-07-27'),
      tags: ['novo-cliente', 'boas-vindas'],
      character_count: 95,
      estimated_cost: 3.5,
    },
    {
      id: 2,
      name: 'Promoção Fim de Semana',
      description: 'Template para promoções de fim de semana',
      content: 'OFERTA ESPECIAL! {{nome}}, aproveite 50% OFF em {{produto}}. Use código {{codigo}} até domingo. {{link}}',
      category: 'promotional',
      language: 'pt',
      variables: ['{{nome}}', '{{produto}}', '{{codigo}}', '{{link}}'],
      usage_count: 156,
      is_favorite: true,
      is_active: true,
      created_by: 'João Santos',
      created_at: new Date('2024-02-10'),
      updated_at: new Date('2024-07-25'),
      last_used: new Date('2024-07-26'),
      tags: ['promocao', 'desconto', 'fim-de-semana'],
      character_count: 102,
      estimated_cost: 3.5,
    },
    {
      id: 3,
      name: 'Lembrete de Pagamento',
      description: 'Lembrete automático para faturas em atraso',
      content: 'Prezado {{nome}}, sua fatura de {{valor}} vence hoje. Evite juros, pague em {{link}} ou ligue {{telefone}}',
      category: 'reminder',
      language: 'pt',
      variables: ['{{nome}}', '{{valor}}', '{{link}}', '{{telefone}}'],
      usage_count: 523,
      is_favorite: false,
      is_active: true,
      created_by: 'Ana Costa',
      created_at: new Date('2024-01-20'),
      updated_at: new Date('2024-07-15'),
      last_used: new Date('2024-07-27'),
      tags: ['pagamento', 'fatura', 'lembrete'],
      character_count: 108,
      estimated_cost: 3.5,
    },
    {
      id: 4,
      name: 'Confirmação de Agendamento',
      description: 'Confirmação de agendamento de serviços',
      content: 'Olá {{nome}}! Confirmamos seu agendamento para {{data}} às {{hora}} na {{empresa}}. {{endereco}}',
      category: 'transactional',
      language: 'pt',
      variables: ['{{nome}}', '{{data}}', '{{hora}}', '{{empresa}}', '{{endereco}}'],
      usage_count: 89,
      is_favorite: false,
      is_active: true,
      created_by: 'Pedro Alves',
      created_at: new Date('2024-03-05'),
      updated_at: new Date('2024-06-20'),
      last_used: new Date('2024-07-24'),
      tags: ['agendamento', 'confirmacao'],
      character_count: 96,
      estimated_cost: 3.5,
    },
    {
      id: 5,
      name: 'Suporte - Ticket Resolvido',
      description: 'Notificação de resolução de ticket de suporte',
      content: 'Olá {{nome}}! Seu ticket foi resolvido. Avalie nosso atendimento de 1 a 5 respondendo esta mensagem.',
      category: 'support',
      language: 'pt',
      variables: ['{{nome}}'],
      usage_count: 67,
      is_favorite: false,
      is_active: true,
      created_by: 'Carlos Mendes',
      created_at: new Date('2024-04-10'),
      updated_at: new Date('2024-07-10'),
      last_used: new Date('2024-07-23'),
      tags: ['suporte', 'ticket', 'avaliacao'],
      character_count: 105,
      estimated_cost: 3.5,
    },
    {
      id: 6,
      name: 'Newsletter Mensal',
      description: 'Template para newsletter mensal',
      content: 'Novidades da {{empresa}}! Confira nossos produtos e ofertas especiais em {{link}}. Obrigado, {{nome}}!',
      category: 'informational',
      language: 'pt',
      variables: ['{{empresa}}', '{{link}}', '{{nome}}'],
      usage_count: 34,
      is_favorite: true,
      is_active: false,
      created_by: 'Luisa Fernandes',
      created_at: new Date('2024-05-15'),
      updated_at: new Date('2024-07-01'),
      last_used: new Date('2024-07-01'),
      tags: ['newsletter', 'novidades'],
      character_count: 98,
      estimated_cost: 3.5,
    },
  ];

  useEffect(() => {
    // Simular carregamento
    setTimeout(() => {
      setTemplates(mockTemplates);
      setLoading(false);
    }, 1000);
  }, []);

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'promotional': return 'error';
      case 'informational': return 'info';
      case 'transactional': return 'success';
      case 'support': return 'warning';
      case 'welcome': return 'primary';
      case 'reminder': return 'secondary';
      default: return 'default';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'promotional': return 'Promocional';
      case 'informational': return 'Informativa';
      case 'transactional': return 'Transacional';
      case 'support': return 'Suporte';
      case 'welcome': return 'Boas-vindas';
      case 'reminder': return 'Lembrete';
      default: return category;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'promotional': return <Campaign />;
      case 'informational': return <Info />;
      case 'transactional': return <Business />;
      case 'support': return <Support />;
      case 'welcome': return <PersonAdd />;
      case 'reminder': return <Schedule />;
      default: return <Message />;
    }
  };

  const extractVariables = (content: string): string[] => {
    const regex = /\{\{([^}]+)\}\}/g;
    const matches = [];
    let match;
    while ((match = regex.exec(content)) !== null) {
      matches.push(`{{${match[1]}}}`);
    }
    return [...new Set(matches)];
  };

  const handleCreateTemplate = (data: TemplateFormData) => {
    const variables = extractVariables(data.content);
    const newTemplate: TemplateData = {
      id: templates.length + 1,
      ...data,
      variables,
      usage_count: 0,
      is_favorite: false,
      created_by: 'Utilizador Atual',
      created_at: new Date(),
      updated_at: new Date(),
      character_count: data.content.length,
      estimated_cost: 3.5,
    };

    setTemplates([...templates, newTemplate]);
    setIsCreateDialogOpen(false);
    reset();
    enqueueSnackbar('Template criado com sucesso!', { variant: 'success' });
  };

  const handleEditTemplate = (template: TemplateData) => {
    setSelectedTemplate(template);
    reset({
      name: template.name,
      description: template.description,
      content: template.content,
      category: template.category,
      language: template.language,
      tags: template.tags,
      is_active: template.is_active,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateTemplate = (data: TemplateFormData) => {
    if (!selectedTemplate) return;

    const variables = extractVariables(data.content);
    const updatedTemplates = templates.map(template =>
      template.id === selectedTemplate.id
        ? {
            ...template,
            ...data,
            variables,
            updated_at: new Date(),
            character_count: data.content.length,
          }
        : template
    );

    setTemplates(updatedTemplates);
    setIsEditDialogOpen(false);
    setSelectedTemplate(null);
    reset();
    enqueueSnackbar('Template atualizado com sucesso!', { variant: 'success' });
  };

  const handleDeleteTemplate = (template: TemplateData) => {
    if (window.confirm(`Tem certeza que deseja eliminar o template "${template.name}"?`)) {
      const updatedTemplates = templates.filter(t => t.id !== template.id);
      setTemplates(updatedTemplates);
      enqueueSnackbar('Template eliminado com sucesso!', { variant: 'success' });
    }
  };

  const handleToggleFavorite = (template: TemplateData) => {
    const updatedTemplates = templates.map(t =>
      t.id === template.id
        ? { ...t, is_favorite: !t.is_favorite }
        : t
    );
    setTemplates(updatedTemplates);
    enqueueSnackbar(
      `Template ${template.is_favorite ? 'removido dos' : 'adicionado aos'} favoritos!`,
      { variant: 'success' }
    );
  };

  const handleToggleActive = (template: TemplateData) => {
    const updatedTemplates = templates.map(t =>
      t.id === template.id
        ? { ...t, is_active: !t.is_active }
        : t
    );
    setTemplates(updatedTemplates);
    enqueueSnackbar(
      `Template ${template.is_active ? 'desativado' : 'ativado'}!`,
      { variant: 'success' }
    );
  };

  const handleDuplicateTemplate = (template: TemplateData) => {
    const duplicatedTemplate: TemplateData = {
      ...template,
      id: templates.length + 1,
      name: `${template.name} (Cópia)`,
      usage_count: 0,
      is_favorite: false,
      created_at: new Date(),
      updated_at: new Date(),
    };

    setTemplates([...templates, duplicatedTemplate]);
    enqueueSnackbar('Template duplicado com sucesso!', { variant: 'success' });
  };

  const handlePreviewTemplate = (template: TemplateData) => {
    setSelectedTemplate(template);
    setIsPreviewDialogOpen(true);
  };

  const insertVariable = (variable: string) => {
    const currentContent = watch('content') || '';
    const newContent = currentContent + variable;
    setValue('content', newContent);
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = filterCategory === 'all' || template.category === filterCategory;
    const matchesLanguage = filterLanguage === 'all' || template.language === filterLanguage;
    const matchesFavorites = !showFavoritesOnly || template.is_favorite;
    
    return matchesSearch && matchesCategory && matchesLanguage && matchesFavorites;
  });

  const templateStats = {
    total: templates.length,
    active: templates.filter(t => t.is_active).length,
    favorites: templates.filter(t => t.is_favorite).length,
    most_used: templates.reduce((prev, current) => 
      (prev.usage_count > current.usage_count) ? prev : current, templates[0]),
    total_usage: templates.reduce((sum, t) => sum + t.usage_count, 0),
  };

  const categoryStats = templates.reduce((acc, template) => {
    acc[template.category] = (acc[template.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Templates de Mensagens
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Crie e gerencie templates reutilizáveis para suas campanhas SMS
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<Analytics />}>
            Relatórios
          </Button>
          <Button variant="outlined" startIcon={<Download />}>
            Exportar
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            Novo Template
          </Button>
        </Box>
      </Box>

      {/* Estatísticas */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Templates
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {templateStats.total}
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
                {templateStats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Favoritos
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="warning.main">
                {templateStats.favorites}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Uso Total
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="primary.main">
                {templateStats.total_usage}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Mais Usado
              </Typography>
              <Typography variant="body2" fontWeight="bold" color="info.main">
                {templateStats.most_used?.name || 'N/A'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {templateStats.most_used?.usage_count || 0} usos
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filtros e Pesquisa */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Pesquisar templates..."
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
            
            <Grid item xs={12} md={2.5}>
              <FormControl fullWidth size="small">
                <InputLabel>Categoria</InputLabel>
                <Select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  label="Categoria"
                >
                  <MenuItem value="all">Todas</MenuItem>
                  <MenuItem value="promotional">Promocional</MenuItem>
                  <MenuItem value="informational">Informativa</MenuItem>
                  <MenuItem value="transactional">Transacional</MenuItem>
                  <MenuItem value="support">Suporte</MenuItem>
                  <MenuItem value="welcome">Boas-vindas</MenuItem>
                  <MenuItem value="reminder">Lembrete</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2.5}>
              <FormControl fullWidth size="small">
                <InputLabel>Idioma</InputLabel>
                <Select
                  value={filterLanguage}
                  onChange={(e) => setFilterLanguage(e.target.value)}
                  label="Idioma"
                >
                  <MenuItem value="all">Todos</MenuItem>
                  <MenuItem value="pt">Português</MenuItem>
                  <MenuItem value="en">Inglês</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Box display="flex" gap={1} alignItems="center">
                <FormControlLabel
                  control={
                    <Switch
                      checked={showFavoritesOnly}
                      onChange={(e) => setShowFavoritesOnly(e.target.checked)}
                      color="warning"
                    />
                  }
                  label="Só Favoritos"
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Templates List */}
      <Grid container spacing={2}>
        {filteredTemplates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card sx={{ height: '100%', position: 'relative' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      {getCategoryIcon(template.category)}
                      <Typography variant="h6" fontWeight="bold">
                        {template.name}
                      </Typography>
                      {template.is_favorite && (
                        <Star color="warning" fontSize="small" />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {template.description}
                    </Typography>
                  </Box>
                  
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      setMenuAnchor(e.currentTarget);
                      setSelectedTemplateForMenu(template);
                    }}
                  >
                    <MoreVert />
                  </IconButton>
                </Box>

                <Box mb={2}>
                  <Typography variant="body2" sx={{ 
                    bgcolor: 'grey.100', 
                    p: 1.5, 
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                    lineHeight: 1.4,
                  }}>
                    {template.content}
                  </Typography>
                </Box>

                <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                  <Chip
                    label={getCategoryLabel(template.category)}
                    color={getCategoryColor(template.category) as any}
                    size="small"
                    variant="outlined"
                  />
                  {template.tags.slice(0, 2).map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.7rem' }}
                    />
                  ))}
                  {template.tags.length > 2 && (
                    <Chip
                      label={`+${template.tags.length - 2}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.7rem' }}
                    />
                  )}
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="caption" color="text.secondary">
                    {template.character_count} caracteres • {template.usage_count} usos
                  </Typography>
                  <Box display="flex" alignItems="center">
                    {template.is_active ? (
                      <Chip label="Ativo" color="success" size="small" />
                    ) : (
                      <Chip label="Inativo" color="default" size="small" />
                    )}
                  </Box>
                </Box>

                {template.variables.length > 0 && (
                  <Box mb={2}>
                    <Typography variant="caption" color="text.secondary" gutterBottom>
                      Variáveis:
                    </Typography>
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {template.variables.map((variable) => (
                        <Chip
                          key={variable}
                          label={variable}
                          size="small"
                          variant="filled"
                          color="primary"
                          sx={{ fontSize: '0.65rem', height: 18 }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                <Box display="flex" gap={1}>
                  <Button
                    size="small"
                    startIcon={<Preview />}
                    onClick={() => handlePreviewTemplate(template)}
                  >
                    Pré-visualizar
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => handleEditTemplate(template)}
                  >
                    Editar
                  </Button>
                  <IconButton
                    size="small"
                    onClick={() => handleToggleFavorite(template)}
                    color={template.is_favorite ? 'warning' : 'default'}
                  >
                    {template.is_favorite ? <Star /> : <StarBorder />}
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredTemplates.length === 0 && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Message sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Nenhum template encontrado
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            {searchTerm || filterCategory !== 'all' || filterLanguage !== 'all' || showFavoritesOnly
              ? 'Tente ajustar os filtros de pesquisa'
              : 'Crie seu primeiro template de mensagem'
            }
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            Criar Template
          </Button>
        </Paper>
      )}

      {/* Menu de Ações */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => {
          setMenuAnchor(null);
          setSelectedTemplateForMenu(null);
        }}
      >
        {selectedTemplateForMenu && (
          <>
            <MenuItem onClick={() => {
              handleEditTemplate(selectedTemplateForMenu);
              setMenuAnchor(null);
            }}>
              <ListItemIcon>
                <Edit fontSize="small" />
              </ListItemIcon>
              <ListItemText>Editar</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => {
              handleDuplicateTemplate(selectedTemplateForMenu);
              setMenuAnchor(null);
            }}>
              <ListItemIcon>
                <ContentCopy fontSize="small" />
              </ListItemIcon>
              <ListItemText>Duplicar</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => {
              handleToggleActive(selectedTemplateForMenu);
              setMenuAnchor(null);
            }}>
              <ListItemIcon>
                {selectedTemplateForMenu.is_active ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
              </ListItemIcon>
              <ListItemText>
                {selectedTemplateForMenu.is_active ? 'Desativar' : 'Ativar'}
              </ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => {
              handleDeleteTemplate(selectedTemplateForMenu);
              setMenuAnchor(null);
            }}>
              <ListItemIcon>
                <Delete fontSize="small" />
              </ListItemIcon>
              <ListItemText>Eliminar</ListItemText>
            </MenuItem>
          </>
        )}
      </Menu>

      {/* Dialog de Criação/Edição */}
      <Dialog
        open={isCreateDialogOpen || isEditDialogOpen}
        onClose={() => {
          setIsCreateDialogOpen(false);
          setIsEditDialogOpen(false);
          setSelectedTemplate(null);
          reset();
        }}
        maxWidth="md"
        fullWidth
      >
        <form onSubmit={handleSubmit(isCreateDialogOpen ? handleCreateTemplate : handleUpdateTemplate)}>
          <DialogTitle>
            {isCreateDialogOpen ? 'Criar Novo Template' : 'Editar Template'}
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
                      label="Nome do Template"
                      error={!!errors.name}
                      helperText={errors.name?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="category"
                  control={control}
                  rules={{ required: 'Categoria é obrigatória' }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.category}>
                      <InputLabel>Categoria</InputLabel>
                      <Select {...field} label="Categoria">
                        <MenuItem value="promotional">Promocional</MenuItem>
                        <MenuItem value="informational">Informativa</MenuItem>
                        <MenuItem value="transactional">Transacional</MenuItem>
                        <MenuItem value="support">Suporte</MenuItem>
                        <MenuItem value="welcome">Boas-vindas</MenuItem>
                        <MenuItem value="reminder">Lembrete</MenuItem>
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
                  name="content"
                  control={control}
                  rules={{ 
                    required: 'Conteúdo é obrigatório',
                    maxLength: { value: maxLength, message: `Máximo ${maxLength} caracteres` }
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Conteúdo da Mensagem"
                      multiline
                      rows={4}
                      error={!!errors.content}
                      helperText={
                        errors.content?.message || 
                        `${characterCount}/${maxLength} caracteres`
                      }
                    />
                  )}
                />
              </Grid>

              {/* Variáveis Disponíveis */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Variáveis Disponíveis:
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                  {availableVariables.map((variable) => (
                    <Chip
                      key={variable.name}
                      label={variable.name}
                      size="small"
                      clickable
                      onClick={() => insertVariable(variable.name)}
                      title={`${variable.description} (Ex: ${variable.example})`}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="language"
                  control={control}
                  defaultValue="pt"
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Idioma</InputLabel>
                      <Select {...field} label="Idioma">
                        <MenuItem value="pt">Português</MenuItem>
                        <MenuItem value="en">Inglês</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="is_active"
                  control={control}
                  defaultValue={true}
                  render={({ field }) => (
                    <FormControlLabel
                      control={
                        <Switch
                          checked={field.value}
                          onChange={field.onChange}
                          color="success"
                        />
                      }
                      label="Template Ativo"
                    />
                  )}
                />
              </Grid>
            </Grid>

            {/* Pré-visualização em Tempo Real */}
            {templateContent && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Pré-visualização:
                </Typography>
                <Paper sx={{ 
                  p: 2, 
                  bgcolor: 'grey.50',
                  border: '1px dashed',
                  borderColor: 'grey.300',
                }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {templateContent}
                  </Typography>
                </Paper>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setIsCreateDialogOpen(false);
              setIsEditDialogOpen(false);
              setSelectedTemplate(null);
              reset();
            }}>
              Cancelar
            </Button>
            <Button type="submit" variant="contained">
              {isCreateDialogOpen ? 'Criar Template' : 'Atualizar Template'}
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
        {selectedTemplate && (
          <>
            <DialogTitle>
              Pré-visualização: {selectedTemplate.name}
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Categoria: {getCategoryLabel(selectedTemplate.category)}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {selectedTemplate.description}
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.100', borderRadius: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Mensagem SMS:
                </Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {selectedTemplate.content}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {selectedTemplate.character_count} caracteres
                </Typography>
              </Box>
              
              {selectedTemplate.variables.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Variáveis utilizadas:
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {selectedTemplate.variables.map((variable) => (
                      <Chip
                        key={variable}
                        label={variable}
                        size="small"
                        color="primary"
                        variant="filled"
                      />
                    ))}
                  </Box>
                </Box>
              )}
              
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Usado {selectedTemplate.usage_count} vezes • 
                  Custo estimado: {selectedTemplate.estimated_cost} MT por SMS
                </Typography>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setIsPreviewDialogOpen(false)}>
                Fechar
              </Button>
              <Button
                variant="contained"
                startIcon={<Send />}
              >
                Usar em Campanha
              </Button>
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
  );
};

export default MessageTemplatesPage;
