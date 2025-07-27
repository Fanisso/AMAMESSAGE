# AMA MESSAGE - Informações do Deploy

**Tipo de Deploy:** Production
**Data/Hora:** 2025-07-26 23:26:40
**Diretório de Origem:** W:\projects\AMAMESSAGE
**Diretório de Destino:** amamessage_deploy_production_20250726_232640

## Próximos Passos:

### Production:

1. Configure o arquivo .env com suas credenciais de produção
2. Execute como root: sudo python deploy.py production
3. Configure: sudo nano /opt/amamessage/.env
4. Inicie: sudo systemctl start amamessage
5. Ver logs: sudo journalctl -u amamessage -f

Acesso: http://seu-servidor

## Ficheiros Incluídos:

Total de ficheiros copiados: 67
Tamanho total: 0.57 MB

## Suporte:

- Documentação: README.md
- Scripts: deploy.py help
- Logs: verificar ficheiros .log
- Testes: python deploy.py test
