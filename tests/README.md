# 🧪 AMAMESSAGE - Estrutura de Testes por Linha de Deploy

Esta estrutura organiza os testes de acordo com as diferentes linhas de deploy do sistema AMAMESSAGE, permitindo validação específica para cada ambiente e tipo de cliente.

## 📁 Estrutura de Pastas

```
tests/
├── shared/                     # Testes compartilhados entre todas as linhas
│   ├── utils/                  # Utilitários de teste
│   ├── fixtures/               # Dados de teste
│   └── base_tests.py          # Classes base para testes
│
├── local/                      # Deploy Local (Desenvolvimento)
│   ├── unit/                   # Testes unitários
│   ├── integration/            # Testes de integração
│   └── e2e/                    # Testes end-to-end
│
├── web_client/                 # Deploy Web Cliente (Testes)
│   ├── ui/                     # Testes de interface web
│   └── api/                    # Testes de API cliente
│
├── cloud_test/                 # Deploy Nuvem (Testes)
│   ├── performance/            # Testes de performance
│   ├── stress/                 # Testes de stress
│   └── load/                   # Testes de carga
│
├── cloud_production/           # Deploy Nuvem (Produção)
│   ├── monitoring/             # Testes de monitoramento
│   ├── security/               # Testes de segurança
│   └── smoke/                  # Testes smoke
│
├── mobile/                     # Deploy Mobile
│   ├── android/                # Testes específicos Android
│   └── ios/                    # Testes específicos iOS
│
└── windows_modem/              # Deploy Windows com Modem Físico
    ├── hardware/               # Testes de hardware
    └── drivers/                # Testes de drivers
```

## 🎯 Tipos de Cliente por Linha

### 👥 **Clientes Empresariais**
- **Web**: Interface completa para empresas
- **Mobile**: Funcionalidades empresariais via mobile (conforto)

### 👤 **Clientes Individuais**
- **Mobile**: Funcionalidades completas via app
- **Web**: Interface simplificada (quando necessário)

## 🚀 Comandos de Teste por Linha

### **Local (Desenvolvimento)**
```bash
# Todos os testes locais
pytest tests/local/ -v

# Apenas testes unitários
pytest tests/local/unit/ -v

# Apenas testes de integração
pytest tests/local/integration/ -v

# Testes end-to-end
pytest tests/local/e2e/ -v
```

### **Web Cliente**
```bash
# Testes da interface web
pytest tests/web_client/ui/ -v

# Testes da API cliente
pytest tests/web_client/api/ -v
```

### **Nuvem (Testes)**
```bash
# Testes de performance
pytest tests/cloud_test/performance/ -v --cloud-env=test

# Testes de stress
pytest tests/cloud_test/stress/ -v --cloud-env=test
```

### **Nuvem (Produção)**
```bash
# Testes smoke de produção
pytest tests/cloud_production/smoke/ -v --cloud-env=prod

# Testes de segurança
pytest tests/cloud_production/security/ -v --cloud-env=prod
```

### **Mobile**
```bash
# Testes Android
pytest tests/mobile/android/ -v --platform=android

# Testes iOS
pytest tests/mobile/ios/ -v --platform=ios
```

### **Windows com Modem**
```bash
# Testes de hardware
pytest tests/windows_modem/hardware/ -v --modem-test

# Testes de drivers
pytest tests/windows_modem/drivers/ -v --driver-test
```

## 🔧 Configuração por Ambiente

### **Arquivos de Configuração**
- `conftest.py` - Configuração global de testes
- `pytest.ini` - Configurações do pytest
- `.env.test` - Variáveis para testes

### **Fixtures por Linha**
Cada linha de deploy tem suas próprias fixtures específicas:
- `tests/local/conftest.py` - Fixtures para desenvolvimento
- `tests/web_client/conftest.py` - Fixtures para web
- `tests/mobile/conftest.py` - Fixtures para mobile
- etc.

## 📊 Relatórios de Teste

### **Por Linha de Deploy**
```bash
# Gerar relatório HTML por linha
pytest tests/local/ --html=reports/local_report.html
pytest tests/web_client/ --html=reports/web_client_report.html
pytest tests/mobile/ --html=reports/mobile_report.html
```

### **Cobertura de Código**
```bash
# Cobertura por linha
pytest tests/local/ --cov=backend --cov-report=html:reports/local_coverage
pytest tests/web_client/ --cov=clients/web --cov-report=html:reports/web_coverage
```

## 🏷️ Tags de Teste

Use tags para categorizar testes:
```python
@pytest.mark.unit          # Teste unitário
@pytest.mark.integration   # Teste de integração
@pytest.mark.e2e          # Teste end-to-end
@pytest.mark.smoke        # Teste smoke
@pytest.mark.slow         # Teste demorado
@pytest.mark.hardware     # Requer hardware
@pytest.mark.cloud        # Requer ambiente nuvem
@pytest.mark.mobile       # Específico mobile
@pytest.mark.web          # Específico web
```

### **Executar por Tag**
```bash
# Apenas testes rápidos
pytest -m "not slow"

# Apenas testes que não requerem hardware
pytest -m "not hardware"

# Testes específicos para mobile
pytest -m "mobile"
```

## 📋 Checklist de Validação

### **Antes do Deploy**
- [ ] Testes unitários passando (local)
- [ ] Testes de integração passando
- [ ] Testes específicos da linha passando
- [ ] Cobertura de código adequada
- [ ] Testes de segurança passando (produção)

### **Após Deploy**
- [ ] Testes smoke passando
- [ ] Monitoramento ativo
- [ ] Logs sem erros críticos
- [ ] Performance dentro dos limites

## 🔄 CI/CD por Linha

Cada linha tem seu pipeline específico:
- **Local**: Testes rápidos em desenvolvimento
- **Web Cliente**: Testes de UI e compatibilidade
- **Nuvem**: Testes de performance e segurança
- **Mobile**: Testes em emuladores/dispositivos
- **Windows**: Testes de hardware específico

## 📞 Suporte

Para problemas específicos de uma linha de teste:
1. Consulte o README da linha específica
2. Verifique os logs em `tests/logs/[linha]/`
3. Execute testes diagnósticos específicos
4. Consulte a documentação técnica da linha

---

**🚀 Para começar:** Execute `pytest tests/shared/test_setup.py` para validar a configuração básica!
