// Componentes de Lista com Integração Total às APIs
// Listas otimizadas para exibição e operações em massa

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/router';
import {
  useContacts,
  useDeleteContact,
  useBulkDeleteContacts,
  useExportContacts,
  useCampaigns,
  useDeleteCampaign,
  useBulkDeleteCampaigns,
  useExportCampaigns,
  useTemplates,
  useDeleteTemplate,
  useBulkDeleteTemplates,
  useExportTemplates,
  useSMSHistory,
  useDeleteSMS,
  useBulkDeleteSMS,
  useExportSMS
} from '@/hooks/api-hooks';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog';
import {
  Search,
  Plus,
  MoreHorizontal,
  Edit,
  Trash2,
  Download,
  Phone,
  MessageSquare,
  Calendar,
  Filter,
  RefreshCw,
  CheckSquare,
  Square,
  Eye,
  Send,
  Copy,
  Archive,
  User,
  Mail,
  Tag,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { formatDistance } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { PhoneFormatter, DateFormatter } from '@/shared/utils/formatters';

// ===== TIPOS COMUNS =====

interface ListPageProps {
  title: string;
  description: string;
  createRoute: string;
  createLabel: string;
}

interface SelectionState {
  selectedIds: number[];
  isAllSelected: boolean;
}

// ===== LISTA DE CONTATOS =====

export function ContactsList() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [selection, setSelection] = useState<SelectionState>({
    selectedIds: [],
    isAllSelected: false
  });
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    contactId?: number;
    contactName?: string;
  }>({ open: false });

  // API Hooks
  const {
    data: contactsData,
    isLoading,
    error,
    refetch
  } = useContacts({
    search: search || undefined,
    per_page: 20
  });

  const deleteContactMutation = useDeleteContact();
  const bulkDeleteMutation = useBulkDeleteContacts();
  const exportMutation = useExportContacts();

  const contacts = contactsData?.items || [];
  const pagination = contactsData?.pagination;

  // Seleção de itens
  const toggleSelection = (contactId: number) => {
    setSelection(prev => ({
      ...prev,
      selectedIds: prev.selectedIds.includes(contactId)
        ? prev.selectedIds.filter(id => id !== contactId)
        : [...prev.selectedIds, contactId]
    }));
  };

  const toggleSelectAll = () => {
    setSelection(prev => ({
      isAllSelected: !prev.isAllSelected,
      selectedIds: !prev.isAllSelected 
        ? contacts.map(contact => contact.id)
        : []
    }));
  };

  // Operações
  const handleDelete = async (contactId: number) => {
    try {
      await deleteContactMutation.mutateAsync(contactId);
      setDeleteDialog({ open: false });
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleBulkDelete = async () => {
    if (selection.selectedIds.length === 0) return;
    
    try {
      await bulkDeleteMutation.mutateAsync(selection.selectedIds);
      setSelection({ selectedIds: [], isAllSelected: false });
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleExport = async () => {
    try {
      const blob = await exportMutation.mutateAsync({
        format: 'csv',
        ids: selection.selectedIds.length > 0 ? selection.selectedIds : undefined
      });
      
      // Download do arquivo
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `contatos_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const selectedCount = selection.selectedIds.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Contatos</h1>
          <p className="text-gray-600">
            Gerencie sua lista de contatos
          </p>
        </div>
        
        <Button 
          onClick={() => router.push('/contacts/new')}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Novo Contato
        </Button>
      </div>

      {/* Filtros e Ações */}
      <Card>
        <CardContent className="p-4">
          <div className="flex justify-between items-center space-x-4">
            {/* Busca */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Buscar por nome, telefone ou email..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Ações */}
            <div className="flex items-center space-x-2">
              {selectedCount > 0 && (
                <>
                  <Badge variant="secondary">
                    {selectedCount} selecionado{selectedCount > 1 ? 's' : ''}
                  </Badge>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleBulkDelete}
                    disabled={bulkDeleteMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Excluir
                  </Button>
                </>
              )}

              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
                disabled={exportMutation.isPending}
              >
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p>Carregando contatos...</p>
            </div>
          ) : error ? (
            <div className="p-8 text-center">
              <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
              <p className="text-red-600">Erro ao carregar contatos</p>
              <Button variant="outline" onClick={() => refetch()} className="mt-4">
                Tentar Novamente
              </Button>
            </div>
          ) : contacts.length === 0 ? (
            <div className="p-8 text-center">
              <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Nenhum contato encontrado
              </h3>
              <p className="text-gray-600 mb-4">
                {search ? 'Tente ajustar sua busca' : 'Comece adicionando um novo contato'}
              </p>
              <Button onClick={() => router.push('/contacts/new')}>
                <Plus className="h-4 w-4 mr-2" />
                Criar Primeiro Contato
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox
                      checked={selection.isAllSelected}
                      onCheckedChange={toggleSelectAll}
                    />
                  </TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>Telefone</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Tags</TableHead>
                  <TableHead>Último Contato</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {contacts.map((contact) => (
                  <TableRow key={contact.id}>
                    <TableCell>
                      <Checkbox
                        checked={selection.selectedIds.includes(contact.id)}
                        onCheckedChange={() => toggleSelection(contact.id)}
                      />
                    </TableCell>
                    
                    <TableCell className="font-medium">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium">{contact.name}</p>
                          {contact.company && (
                            <p className="text-sm text-gray-500">{contact.company}</p>
                          )}
                        </div>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Phone className="h-4 w-4 text-gray-400" />
                        <span>{PhoneFormatter.formatDisplay(contact.phone)}</span>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      {contact.email && (
                        <div className="flex items-center space-x-2">
                          <Mail className="h-4 w-4 text-gray-400" />
                          <span>{contact.email}</span>
                        </div>
                      )}
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {contact.tags?.slice(0, 2).map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {contact.tags && contact.tags.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{contact.tags.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      {contact.last_contact && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Clock className="h-4 w-4" />
                          <span>
                            {formatDistance(new Date(contact.last_contact), new Date(), {
                              addSuffix: true,
                              locale: ptBR
                            })}
                          </span>
                        </div>
                      )}
                    </TableCell>
                    
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => router.push(`/contacts/${contact.id}`)}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            Ver Detalhes
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => router.push(`/contacts/${contact.id}/edit`)}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Editar
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => router.push(`/sms/send?contact=${contact.id}`)}
                          >
                            <MessageSquare className="h-4 w-4 mr-2" />
                            Enviar SMS
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => setDeleteDialog({
                              open: true,
                              contactId: contact.id,
                              contactName: contact.name
                            })}
                            className="text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Excluir
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Paginação */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex justify-center">
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              disabled={pagination.current_page === 1}
              onClick={() => {
                // Implementar navegação de página via router
                router.push({
                  pathname: router.pathname,
                  query: { ...router.query, page: pagination.current_page - 1 }
                });
              }}
            >
              Anterior
            </Button>
            
            <span className="text-sm text-gray-600">
              Página {pagination.current_page} de {pagination.total_pages}
            </span>
            
            <Button
              variant="outline"
              size="sm"
              disabled={pagination.current_page === pagination.total_pages}
              onClick={() => {
                router.push({
                  pathname: router.pathname,
                  query: { ...router.query, page: pagination.current_page + 1 }
                });
              }}
            >
              Próxima
            </Button>
          </div>
        </div>
      )}

      {/* Dialog de Confirmação de Exclusão */}
      <AlertDialog 
        open={deleteDialog.open} 
        onOpenChange={(open) => setDeleteDialog({ ...deleteDialog, open })}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar Exclusão</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir o contato "{deleteDialog.contactName}"?
              Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteDialog.contactId && handleDelete(deleteDialog.contactId)}
              className="bg-red-600 hover:bg-red-700"
              disabled={deleteContactMutation.isPending}
            >
              {deleteContactMutation.isPending ? 'Excluindo...' : 'Excluir'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

// ===== LISTA DE CAMPANHAS =====

export function CampaignsList() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [selection, setSelection] = useState<SelectionState>({
    selectedIds: [],
    isAllSelected: false
  });

  const {
    data: campaignsData,
    isLoading,
    error,
    refetch
  } = useCampaigns({
    search: search || undefined,
    per_page: 20
  });

  const campaigns = campaignsData?.items || [];

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { label: 'Rascunho', variant: 'secondary' as const, icon: Edit },
      scheduled: { label: 'Agendada', variant: 'outline' as const, icon: Clock },
      running: { label: 'Executando', variant: 'default' as const, icon: Send },
      completed: { label: 'Concluída', variant: 'default' as const, icon: CheckCircle },
      failed: { label: 'Falhou', variant: 'destructive' as const, icon: XCircle },
      paused: { label: 'Pausada', variant: 'secondary' as const, icon: AlertCircle }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center space-x-1">
        <Icon className="h-3 w-3" />
        <span>{config.label}</span>
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campanhas</h1>
          <p className="text-gray-600">
            Gerencie suas campanhas de SMS
          </p>
        </div>
        
        <Button 
          onClick={() => router.push('/campaigns/new')}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nova Campanha
        </Button>
      </div>

      {/* Lista */}
      <div className="grid gap-4">
        {campaigns.map((campaign) => (
          <Card key={campaign.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{campaign.name}</h3>
                    {getStatusBadge(campaign.status)}
                  </div>
                  
                  <p className="text-gray-600 mb-4">{campaign.description}</p>
                  
                  <div className="flex items-center space-x-6 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <User className="h-4 w-4" />
                      <span>{campaign.recipient_count || 0} destinatários</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <MessageSquare className="h-4 w-4" />
                      <span>{campaign.sent_count || 0} enviados</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>
                        {campaign.created_at && DateFormatter.formatRelative(campaign.created_at)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/campaigns/${campaign.id}`)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Ver
                  </Button>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => router.push(`/campaigns/${campaign.id}/edit`)}
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        Editar
                      </DropdownMenuItem>
                      
                      <DropdownMenuItem
                        onClick={() => {
                          navigator.clipboard.writeText(campaign.name);
                          toast.success('Nome copiado!');
                        }}
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Duplicar
                      </DropdownMenuItem>
                      
                      <DropdownMenuSeparator />
                      
                      <DropdownMenuItem className="text-red-600">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Excluir
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ===== LISTA DE TEMPLATES =====

export function TemplatesList() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  
  const {
    data: templatesData,
    isLoading,
    error,
    refetch
  } = useTemplates({
    search: search || undefined,
    per_page: 20
  });

  const templates = templatesData?.items || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
          <p className="text-gray-600">
            Gerencie seus templates de mensagem
          </p>
        </div>
        
        <Button 
          onClick={() => router.push('/templates/new')}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Novo Template
        </Button>
      </div>

      {/* Grid de Templates */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <Card key={template.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{template.name}</CardTitle>
                <Badge variant={template.is_active ? 'default' : 'secondary'}>
                  {template.is_active ? 'Ativo' : 'Inativo'}
                </Badge>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600 mb-2">Conteúdo:</p>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm font-mono">
                      {template.content.length > 100 
                        ? `${template.content.substring(0, 100)}...`
                        : template.content
                      }
                    </p>
                  </div>
                </div>

                {template.variables && template.variables.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Variáveis:</p>
                    <div className="flex flex-wrap gap-1">
                      {template.variables.map((variable, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {variable}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between pt-4">
                  <div className="text-xs text-gray-500">
                    {template.usage_count || 0} usos
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/templates/${template.id}`)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/templates/${template.id}/edit`)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/sms/send?template=${template.id}`)}
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ===== EXPORTS =====

export {
  ContactsList,
  CampaignsList,
  TemplatesList
};
