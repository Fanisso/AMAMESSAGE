# Shared Components - AMAMESSAGE Monorepo
# Componentes compartilhados entre backend, web e mobile

Este diretório contém código e recursos compartilhados entre todos os componentes do sistema AMAMESSAGE.

## Estrutura

```
shared/
├── api/                    # Definições de API compartilhadas
├── models/                 # Modelos de dados comuns
├── types/                  # Definições de tipos
├── utils/                  # Utilitários comuns
├── constants/              # Constantes do sistema
├── schemas/                # Schemas de validação
└── services/               # Serviços base compartilhados
```

## Uso

### Backend (Python)
```python
from shared.models import SMSMessage, USSDSession
from shared.utils import validate_phone_number
```

### Web Client (JavaScript/TypeScript)
```javascript
import { SMSMessage, USSDSession } from '../shared/models'
import { validatePhoneNumber } from '../shared/utils'
```

### Mobile (React Native/Flutter)
```dart
import 'package:amamessage_shared/models.dart';
import 'package:amamessage_shared/utils.dart';
```

## Componentes

- **API Definitions**: Especificações OpenAPI/Swagger compartilhadas
- **Data Models**: Estruturas de dados consistentes
- **Validation Schemas**: Regras de validação unificadas
- **Utility Functions**: Funções auxiliares reutilizáveis
- **Constants**: Configurações e constantes do sistema
