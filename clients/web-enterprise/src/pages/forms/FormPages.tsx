// Páginas de Formulários Integradas com APIs
// Componentes de página que integram os formulários com as APIs

import React from 'react';
import { useRouter } from 'next/router';
import { ContactForm } from '@/components/forms/ContactForm';
import { CampaignForm } from '@/components/forms/CampaignForm';
import { TemplateForm } from '@/components/forms/TemplateForm';
import { SMSForm } from '@/components/forms/SMSForm';
import {
  useCreateContact,
  useUpdateContact,
  useContact,
  useCreateCampaign,
  useUpdateCampaign,
  useCampaign,
  useCreateTemplate,
  useUpdateTemplate,
  useTemplate,
  useSendSMS,
  useTemplates,
  useContacts
} from '@/hooks/api-hooks';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

// ===== PÁGINA DE CRIAÇÃO DE CONTATO =====

export function CreateContactPage() {
  const router = useRouter();
  const createContactMutation = useCreateContact();

  const handleSubmit = async (data: any) => {
    try {
      const newContact = await createContactMutation.mutateAsync(data);
      router.push(`/contacts/${newContact.id}`);
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push('/contacts');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar aos Contatos
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Novo Contato
          </h1>
          <p className="text-gray-600">
            Adicione um novo contato ao seu sistema
          </p>
        </div>

        {/* Formulário */}
        <ContactForm
          mode="create"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={createContactMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== PÁGINA DE EDIÇÃO DE CONTATO =====

export function EditContactPage() {
  const router = useRouter();
  const contactId = parseInt(router.query.id as string);
  
  const { data: contact, isLoading } = useContact(contactId);
  const updateContactMutation = useUpdateContact();

  const handleSubmit = async (data: any) => {
    try {
      await updateContactMutation.mutateAsync({ id: contactId, data });
      router.push(`/contacts/${contactId}`);
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push(`/contacts/${contactId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <h2 className="text-xl font-semibold mb-2">Contato não encontrado</h2>
            <p className="text-gray-600 mb-4">
              O contato solicitado não existe ou foi removido.
            </p>
            <Button onClick={() => router.push('/contacts')}>
              Voltar aos Contatos
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar ao Contato
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Editar Contato
          </h1>
          <p className="text-gray-600">
            Atualize as informações de {contact.name}
          </p>
        </div>

        {/* Formulário */}
        <ContactForm
          mode="edit"
          initialData={contact}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={updateContactMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== PÁGINA DE CRIAÇÃO DE CAMPANHA =====

export function CreateCampaignPage() {
  const router = useRouter();
  const createCampaignMutation = useCreateCampaign();

  const handleSubmit = async (data: any) => {
    try {
      const newCampaign = await createCampaignMutation.mutateAsync(data);
      router.push(`/campaigns/${newCampaign.id}`);
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push('/campaigns');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar às Campanhas
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Nova Campanha SMS
          </h1>
          <p className="text-gray-600">
            Crie uma nova campanha de SMS para seus contatos
          </p>
        </div>

        {/* Formulário */}
        <CampaignForm
          mode="create"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={createCampaignMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== PÁGINA DE EDIÇÃO DE CAMPANHA =====

export function EditCampaignPage() {
  const router = useRouter();
  const campaignId = parseInt(router.query.id as string);
  
  const { data: campaign, isLoading } = useCampaign(campaignId);
  const updateCampaignMutation = useUpdateCampaign();

  const handleSubmit = async (data: any) => {
    try {
      await updateCampaignMutation.mutateAsync({ id: campaignId, data });
      router.push(`/campaigns/${campaignId}`);
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push(`/campaigns/${campaignId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <h2 className="text-xl font-semibold mb-2">Campanha não encontrada</h2>
            <p className="text-gray-600 mb-4">
              A campanha solicitada não existe ou foi removida.
            </p>
            <Button onClick={() => router.push('/campaigns')}>
              Voltar às Campanhas
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar à Campanha
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Editar Campanha
          </h1>
          <p className="text-gray-600">
            Atualize as configurações de {campaign.name}
          </p>
        </div>

        {/* Formulário */}
        <CampaignForm
          mode="edit"
          initialData={campaign}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={updateCampaignMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== PÁGINA DE CRIAÇÃO DE TEMPLATE =====

export function CreateTemplatePage() {
  const router = useRouter();
  const createTemplateMutation = useCreateTemplate();

  const handleSubmit = async (data: any) => {
    try {
      const newTemplate = await createTemplateMutation.mutateAsync(data);
      router.push(`/templates/${newTemplate.id}`);
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push('/templates');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar aos Templates
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Novo Template SMS
          </h1>
          <p className="text-gray-600">
            Crie um novo template reutilizável para suas mensagens
          </p>
        </div>

        {/* Formulário */}
        <TemplateForm
          mode="create"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={createTemplateMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== PÁGINA DE EDIÇÃO DE TEMPLATE =====

export function EditTemplatePage() {
  const router = useRouter();
  const templateId = parseInt(router.query.id as string);
  
  const { data: template, isLoading } = useTemplate(templateId);
  const updateTemplateMutation = useUpdateTemplate();

  const handleSubmit = async (data: any) => {
    try {
      await updateTemplateMutation.mutateAsync({ id: templateId, data });
      router.push(`/templates/${templateId}`);
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push(`/templates/${templateId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!template) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <h2 className="text-xl font-semibold mb-2">Template não encontrado</h2>
            <p className="text-gray-600 mb-4">
              O template solicitado não existe ou foi removido.
            </p>
            <Button onClick={() => router.push('/templates')}>
              Voltar aos Templates
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar ao Template
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Editar Template
          </h1>
          <p className="text-gray-600">
            Atualize o template {template.name}
          </p>
        </div>

        {/* Formulário */}
        <TemplateForm
          mode="edit"
          initialData={template}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={updateTemplateMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== PÁGINA DE ENVIO DE SMS =====

export function SendSMSPage() {
  const router = useRouter();
  const sendSMSMutation = useSendSMS();
  
  // Buscar templates e contatos para o formulário
  const { data: templatesData } = useTemplates({ 
    is_active: true, 
    per_page: 50 
  });
  const { data: contactsData } = useContacts({ 
    per_page: 20, 
    sort_by: 'last_contact' 
  });

  const templates = templatesData?.items.map(template => ({
    id: template.id,
    name: template.name,
    content: template.content,
    variables: template.variables
  })) || [];

  const contacts = contactsData?.items.map(contact => ({
    id: contact.id,
    name: contact.name,
    phone: contact.phone
  })) || [];

  const handleSubmit = async (data: any) => {
    try {
      await sendSMSMutation.mutateAsync(data);
      
      // Mostrar opções após envio
      toast.success('SMS enviado com sucesso!', {
        action: {
          label: 'Ver Histórico',
          onClick: () => router.push('/sms/history')
        }
      });
      
      // Opcional: redirecionar ou limpar formulário
      // router.push('/sms/history');
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar ao Dashboard
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Enviar SMS
          </h1>
          <p className="text-gray-600">
            Envie uma mensagem SMS individual
          </p>
        </div>

        {/* Formulário */}
        <SMSForm
          mode="single"
          templates={templates}
          contacts={contacts}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={sendSMSMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== PÁGINA DE ENVIO RÁPIDO DE SMS =====

export function QuickSMSPage() {
  const router = useRouter();
  const sendSMSMutation = useSendSMS();
  
  // Buscar apenas templates favoritos e contatos recentes
  const { data: templatesData } = useTemplates({ 
    is_active: true,
    // Assumindo que temos um filtro para favoritos
    per_page: 10 
  });
  const { data: contactsData } = useContacts({ 
    per_page: 10, 
    sort_by: 'last_contact' 
  });

  const templates = templatesData?.items.map(template => ({
    id: template.id,
    name: template.name,
    content: template.content,
    variables: template.variables
  })) || [];

  const contacts = contactsData?.items.map(contact => ({
    id: contact.id,
    name: contact.name,
    phone: contact.phone
  })) || [];

  const handleSubmit = async (data: any) => {
    try {
      await sendSMSMutation.mutateAsync(data);
      // Manter na página para envios rápidos consecutivos
    } catch (error) {
      // Erro já tratado no hook
    }
  };

  const handleCancel = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancel}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar ao Dashboard
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Envio Rápido de SMS
          </h1>
          <p className="text-gray-600">
            Interface otimizada para envios frequentes
          </p>
        </div>

        {/* Formulário */}
        <SMSForm
          mode="quick"
          templates={templates}
          contacts={contacts}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={sendSMSMutation.isPending}
        />
      </div>
    </div>
  );
}

// ===== EXPORTS =====

export {
  CreateContactPage,
  EditContactPage,
  CreateCampaignPage,
  EditCampaignPage,
  CreateTemplatePage,
  EditTemplatePage,
  SendSMSPage,
  QuickSMSPage
};
