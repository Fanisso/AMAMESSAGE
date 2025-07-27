// Arquivo Principal da Aplicação Next.js
// Configuração global, providers e inicialização

import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import Head from 'next/head';
import { Inter } from 'next/font/google';

// Providers e configurações
import { AppProviders, AppWrapper, SYSTEM_CONFIG } from '@/config/AppConfig';
import { ProtectedRoute } from '@/hooks/useAuth';

// Estilos globais
import '@/styles/globals.css';

// Configuração da fonte
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

// ===== ROTAS PÚBLICAS =====
const PUBLIC_ROUTES = [
  '/login',
  '/register',
  '/reset-password',
  '/verify-email',
  '/terms',
  '/privacy',
  '/help',
  '/_error',
  '/404',
  '/500'
];

// ===== ROTAS SEM LAYOUT =====
const NO_LAYOUT_ROUTES = [
  '/login',
  '/register',
  '/reset-password',
  '/verify-email'
];

// ===== COMPONENTE PRINCIPAL =====

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const currentPath = router.pathname;

  // Verificar se é rota pública
  const isPublicRoute = PUBLIC_ROUTES.includes(currentPath);
  
  // Verificar se deve usar layout
  const shouldUseLayout = !NO_LAYOUT_ROUTES.includes(currentPath);

  // ===== EFEITOS =====
  
  // Analytics e monitoramento
  useEffect(() => {
    const handleRouteChange = (url: string) => {
      // Aqui você pode adicionar tracking de páginas
      if (SYSTEM_CONFIG.app.environment === 'production') {
        // gtag('config', 'GA_MEASUREMENT_ID', {
        //   page_path: url,
        // });
      }
    };

    router.events.on('routeChangeComplete', handleRouteChange);
    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router.events]);

  // Configurações de desenvolvimento
  useEffect(() => {
    if (SYSTEM_CONFIG.app.environment === 'development') {
      // Logs de desenvolvimento
      console.log(`🚀 ${SYSTEM_CONFIG.app.name} v${SYSTEM_CONFIG.app.version}`);
      console.log('📄 Current page:', currentPath);
      console.log('🔐 Is public route:', isPublicRoute);
      console.log('🎨 Use layout:', shouldUseLayout);
    }
  }, [currentPath, isPublicRoute, shouldUseLayout]);

  // ===== RENDERIZADOR PRINCIPAL =====

  const renderApp = () => {
    const PageComponent = Component as any;

    // Para rotas públicas, renderizar diretamente
    if (isPublicRoute) {
      return (
        <AppWrapper useLayout={shouldUseLayout}>
          <PageComponent {...pageProps} />
        </AppWrapper>
      );
    }

    // Para rotas privadas, usar ProtectedRoute
    return (
      <ProtectedRoute>
        <AppWrapper useLayout={shouldUseLayout}>
          <PageComponent {...pageProps} />
        </AppWrapper>
      </ProtectedRoute>
    );
  };

  return (
    <>
      <Head>
        {/* Meta Tags Básicas */}
        <title>{SYSTEM_CONFIG.app.name} - {SYSTEM_CONFIG.app.description}</title>
        <meta name="description" content={SYSTEM_CONFIG.app.description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Meta Tags Adicionais */}
        <meta name="application-name" content={SYSTEM_CONFIG.app.name} />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content={SYSTEM_CONFIG.app.name} />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="theme-color" content={SYSTEM_CONFIG.ui.theme.primary} />
        
        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content={SYSTEM_CONFIG.app.name} />
        <meta property="og:description" content={SYSTEM_CONFIG.app.description} />
        <meta property="og:site_name" content={SYSTEM_CONFIG.app.name} />
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:title" content={SYSTEM_CONFIG.app.name} />
        <meta name="twitter:description" content={SYSTEM_CONFIG.app.description} />
        
        {/* Preconnect para APIs */}
        <link rel="preconnect" href={SYSTEM_CONFIG.api.baseURL} />
        
        {/* PWA Manifest */}
        <link rel="manifest" href="/manifest.json" />
        
        {/* Apple Icons */}
        <link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
        <link rel="apple-touch-icon" sizes="152x152" href="/icons/apple-touch-icon-152x152.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon-180x180.png" />
        
        {/* Favicon */}
        <link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/icons/favicon-16x16.png" />
        
        {/* Splash Screens */}
        <link rel="apple-touch-startup-image" href="/icons/apple-splash-2048-2732.jpg" />
        
        {/* Prefetch DNS para recursos externos */}
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="dns-prefetch" href="//fonts.gstatic.com" />
      </Head>

      {/* Classe da fonte no body */}
      <div className={`${inter.variable} font-sans antialiased`}>
        {/* Provider principal que envolve toda a aplicação */}
        <AppProviders>
          {renderApp()}
        </AppProviders>
      </div>
    </>
  );
}

// ===== CONFIGURAÇÕES ADICIONAIS =====

// Desabilitar SSR para componentes específicos que não funcionam no servidor
App.getInitialProps = async (appContext) => {
  // Aqui você pode adicionar lógica de inicialização global
  // Por exemplo, carregar configurações do servidor
  
  return {
    pageProps: {}
  };
};
