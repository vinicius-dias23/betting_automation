
# Sistema de Automação de Apostas Esportivas

⚠️ **AVISO IMPORTANTE**: Este sistema é fornecido apenas para fins educacionais. O uso de automação para apostas pode violar os termos de serviço de sites de apostas e pode resultar em perdas financeiras. Use por sua conta e risco.

## Descrição

Sistema completo de automação que monitora mensagens em grupos do Telegram e executa apostas automaticamente em sites de apostas esportivas.

### Funcionalidades

- 🔍 **Monitoramento do Telegram**: Login automático e monitoramento contínuo de grupos
- 📊 **Extração de Dados**: Análise inteligente de mensagens para extrair informações de apostas
- 🎯 **Execução Automática**: Login e execução automática de apostas em sites de apostas
- 🛡️ **Modo Stealth**: Configurações anti-detecção para evitar bloqueios
- 💾 **Persistência de Sessão**: Mantém login ativo entre execuções
- 📝 **Logging Completo**: Sistema robusto de logs para auditoria
- 🔄 **Recuperação de Erros**: Retry automático e tratamento de falhas

## Requisitos

### Sistema
- Python 3.8+
- Google Chrome ou Chromium
- Linux/macOS/Windows
- Conexão com internet estável

### Credenciais Necessárias
- Conta do Telegram com acesso ao grupo de apostas
- Conta no site de apostas
- Número de telefone do Telegram
- Credenciais do site de apostas

## Instalação

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd betting_automation
```

### 2. Execute o Script de Instalação
```bash
chmod +x run.sh
./run.sh
```

O script irá:
- Criar ambiente virtual Python
- Instalar todas as dependências
- Instalar Chrome (se necessário)
- Criar arquivo de configuração

### 3. Configure as Credenciais

Edite o arquivo `.env` com suas informações:

```env
# Configurações do Telegram
TELEGRAM_PHONE=+5511999999999
TELEGRAM_PASSWORD=sua_senha_telegram_2fa
TELEGRAM_GROUP_URL=https://web.telegram.org/k/#@grupo_apostas

# Configurações do Site de Apostas
BET_SITE_USERNAME=seu_usuario
BET_SITE_PASSWORD=sua_senha
BET_SITE_BASE_URL=https://sitedeapostas.com

# Configurações Gerais
DEFAULT_BET_AMOUNT=10.00
MAX_BET_AMOUNT=100.00
MIN_BET_AMOUNT=5.00
CHECK_INTERVAL_SECONDS=30
```

## Uso

### Execução Simples
```bash
./run.sh
```

### Opções de Execução

1. **Primeiro Plano** (recomendado para teste):
   - Executa com output visível
   - Fácil de interromper (Ctrl+C)

2. **Segundo Plano** (daemon):
   - Executa em background
   - Logs salvos em arquivo
   - Para parar: `kill <PID>`

3. **Validação de Configuração**:
   - Apenas testa se configurações estão corretas

### Primeira Execução

Na primeira execução, você precisará:

1. **Login no Telegram**:
   - Inserir código de verificação enviado por SMS
   - Inserir senha 2FA (se habilitada)

2. **Login no Site de Apostas**:
   - Pode precisar resolver CAPTCHA manualmente
   - Sessão será salva para próximas execuções

## Formato das Mensagens

O sistema reconhece mensagens com o seguinte formato:

```
Jogo: Time A x Time B
Valor: R$ 25,00
Odd: 2.50
Link: https://sitedeapostas.com/aposta/123456
```

Ou formatos alternativos:
```
Apostar R$ 15 em Time A
@2.30
https://sitedeapostas.com/bet/789
```

### Campos Reconhecidos
- **Valor**: `R$ 10,00`, `apostar 15`, `valor: 20`
- **Link**: Qualquer URL HTTP/HTTPS
- **Odds**: `@2.50`, `odd: 1.80`, `cotação 3.20`
- **Evento**: `Time A x Time B`, `jogo: Brasil vs Argentina`

## Estrutura do Projeto

```
betting_automation/
├── src/
│   ├── main.py              # Sistema principal
│   ├── config.py            # Configurações
│   ├── telegram_watcher.py  # Monitoramento Telegram
│   ├── bet_executor.py      # Execução de apostas
│   ├── browser_manager.py   # Gerenciamento do navegador
│   └── utils.py             # Utilitários
├── logs/                    # Arquivos de log
├── screenshots/             # Screenshots de debug
├── chrome_profiles/         # Perfis persistentes do Chrome
├── requirements.txt         # Dependências Python
├── .env                     # Configurações (criar a partir do .env.example)
├── run.sh                   # Script de execução
└── README.md               # Este arquivo
```

## Configurações Avançadas

### Configurações de Segurança
```env
ENABLE_HEADLESS=true        # Executar sem interface gráfica
ENABLE_STEALTH_MODE=true    # Modo anti-detecção
MAX_RETRIES=3               # Tentativas em caso de erro
RETRY_DELAY_SECONDS=5       # Delay entre tentativas
```

### Configurações de Monitoramento
```env
CHECK_INTERVAL_SECONDS=30   # Intervalo entre verificações
ENABLE_NOTIFICATIONS=true   # Habilitar notificações
LOG_LEVEL=INFO             # Nível de log (DEBUG, INFO, WARNING, ERROR)
```

## Logs e Monitoramento

### Arquivos de Log
- `logs/betting_automation.log`: Log principal do sistema
- `logs/system.log`: Log de execução em background

### Screenshots
- Capturas automáticas em caso de erro
- Salvos em `screenshots/` com timestamp

### Monitoramento em Tempo Real
```bash
# Ver logs em tempo real
tail -f logs/betting_automation.log

# Ver apenas erros
tail -f logs/betting_automation.log | grep ERROR

# Ver apostas executadas
tail -f logs/betting_automation.log | grep "APOSTA EXECUTADA"
```

## Solução de Problemas

### Problemas Comuns

1. **Chrome não encontrado**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install google-chrome-stable
   
   # CentOS/RHEL
   sudo yum install google-chrome-stable
   ```

2. **Erro de permissão**:
   ```bash
   chmod +x run.sh
   ```

3. **Dependências não instaladas**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Telegram não carrega**:
   - Verificar se número de telefone está correto
   - Verificar conexão com internet
   - Tentar limpar sessão: `rm telegram_session.json`

5. **Site de apostas bloqueia**:
   - Habilitar modo stealth: `ENABLE_STEALTH_MODE=true`
   - Aumentar delays entre ações
   - Verificar se credenciais estão corretas

### Debug

Para debug detalhado:
```env
LOG_LEVEL=DEBUG
ENABLE_HEADLESS=false  # Ver navegador em ação
```

### Limpeza de Dados
```bash
# Limpar sessões salvas
rm -f telegram_session.json betting_session.json

# Limpar perfis do Chrome
rm -rf chrome_profiles/

# Limpar logs
rm -f logs/*.log
```

## Segurança

### Boas Práticas
- ✅ Use senhas fortes e únicas
- ✅ Habilite 2FA no Telegram
- ✅ Execute em ambiente isolado
- ✅ Monitore logs regularmente
- ✅ Defina limites de aposta
- ✅ Faça backup das configurações

### Riscos
- ⚠️ Detecção por sites de apostas
- ⚠️ Perda de credenciais se comprometidas
- ⚠️ Perdas financeiras por bugs
- ⚠️ Violação de termos de serviço

## Limitações

- Funciona apenas com sites que permitem automação
- Requer manutenção quando sites mudam estrutura
- Dependente de estabilidade da conexão
- Pode ser detectado por sistemas anti-bot

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/`
2. Consulte a seção de solução de problemas
3. Verifique se configurações estão corretas
4. Teste com `ENABLE_HEADLESS=false` para debug visual

## Disclaimer

Este software é fornecido "como está", sem garantias de qualquer tipo. O uso deste sistema pode:
- Violar termos de serviço de sites de apostas
- Resultar em perdas financeiras
- Ser considerado ilegal em algumas jurisdições

Use por sua conta e risco. Os desenvolvedores não se responsabilizam por quaisquer danos ou perdas resultantes do uso deste software.
