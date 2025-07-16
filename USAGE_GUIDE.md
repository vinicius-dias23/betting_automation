
# Guia de Uso - Sistema de Automação de Apostas

## 🚀 Início Rápido

### 1. Configuração Inicial

```bash
# Navegar para o diretório
cd /home/ubuntu/betting_automation

# Executar configuração automática
./setup_system.py

# OU executar manualmente
./run.sh
```

### 2. Configurar Credenciais

Edite o arquivo `.env` com suas informações:

```bash
nano .env
```

**Configurações obrigatórias:**
```env
TELEGRAM_PHONE=+5511999999999
TELEGRAM_GROUP_URL=https://web.telegram.org/k/#@grupo_apostas
BET_SITE_USERNAME=seu_usuario
BET_SITE_PASSWORD=sua_senha
BET_SITE_BASE_URL=https://sitedeapostas.com
```

### 3. Testar Sistema

```bash
# Testar se tudo está funcionando
python3 test_system.py

# Validar apenas configuração
python3 -c "from src.config import validate_config; validate_config()"
```

### 4. Executar Sistema

```bash
# Modo interativo (recomendado para primeira vez)
./run.sh

# Escolher opção 1 (primeiro plano)
```

## 📋 Fluxo de Operação

### Primeira Execução

1. **Login no Telegram**:
   - Sistema abrirá Telegram Web
   - Inserir código SMS quando solicitado
   - Inserir senha 2FA se necessário
   - Sessão será salva automaticamente

2. **Login no Site de Apostas**:
   - Sistema navegará para site de apostas
   - Pode precisar resolver CAPTCHA manualmente
   - Sessão será salva para próximas execuções

3. **Monitoramento**:
   - Sistema começará a monitorar grupo do Telegram
   - Verificará mensagens a cada 30 segundos (configurável)

### Execuções Subsequentes

- Sistema usará sessões salvas
- Login automático (se sessões válidas)
- Monitoramento contínuo

## 🎯 Formato de Mensagens Suportadas

### Formato Completo
```
Jogo: Brasil x Argentina
Valor: R$ 25,00
Odd: 2.50
Link: https://sitedeapostas.com/bet/123456
```

### Formato Simples
```
Apostar R$ 15 em Flamengo
@2.30
https://bet365.com/link/456
```

### Formato Mínimo
```
Valor: 20,50
https://sportingbet.com/789
```

### Campos Reconhecidos

- **Valor**: `R$ 10,00`, `apostar 15`, `valor: 20`, `stake: 25.50`
- **Link**: Qualquer URL HTTP/HTTPS
- **Odds**: `@2.50`, `odd: 1.80`, `cotação 3.20`
- **Evento**: `Time A x Time B`, `jogo: Brasil vs Argentina`

## ⚙️ Configurações Avançadas

### Valores de Aposta
```env
DEFAULT_BET_AMOUNT=10.00    # Valor padrão se não especificado
MAX_BET_AMOUNT=100.00       # Valor máximo permitido
MIN_BET_AMOUNT=5.00         # Valor mínimo permitido
```

### Monitoramento
```env
CHECK_INTERVAL_SECONDS=30   # Intervalo entre verificações
ENABLE_NOTIFICATIONS=true   # Habilitar notificações
```

### Segurança
```env
ENABLE_HEADLESS=true        # Executar sem interface gráfica
ENABLE_STEALTH_MODE=true    # Modo anti-detecção
MAX_RETRIES=3               # Tentativas em caso de erro
```

## 🔧 Comandos Úteis

### Monitoramento
```bash
# Ver logs em tempo real
tail -f logs/betting_automation.log

# Ver apenas apostas executadas
tail -f logs/betting_automation.log | grep "APOSTA EXECUTADA"

# Ver erros
tail -f logs/betting_automation.log | grep ERROR
```

### Controle do Sistema
```bash
# Parar sistema em background
pkill -f "python3 src/main.py"

# Ver processos rodando
ps aux | grep betting

# Limpar logs antigos
rm -f logs/*.log
```

### Limpeza de Dados
```bash
# Limpar sessões (forçar novo login)
rm -f telegram_session.json betting_session.json

# Limpar perfis do Chrome
rm -rf chrome_profiles/

# Reset completo
rm -f *.json && rm -rf chrome_profiles/ && rm -f logs/*.log
```

## 🐛 Solução de Problemas

### Problema: Telegram não carrega
```bash
# Verificar configuração
echo $TELEGRAM_PHONE
echo $TELEGRAM_GROUP_URL

# Limpar sessão e tentar novamente
rm -f telegram_session.json
./run.sh
```

### Problema: Site de apostas bloqueia
```bash
# Habilitar modo stealth
echo "ENABLE_STEALTH_MODE=true" >> .env

# Executar sem headless para debug
echo "ENABLE_HEADLESS=false" >> .env
./run.sh
```

### Problema: Mensagens não são detectadas
```bash
# Testar parser
python3 -c "
from src.utils import MessageParser
result = MessageParser.extract_bet_info('Valor: R$ 10 https://site.com/bet')
print(result)
"

# Verificar logs
tail -f logs/betting_automation.log | grep "mensagem"
```

### Problema: Dependências
```bash
# Reinstalar dependências
source venv/bin/activate
pip install --force-reinstall -r requirements.txt

# Verificar Chrome
google-chrome --version
```

## 📊 Monitoramento e Logs

### Estrutura de Logs
```
logs/
├── betting_automation.log  # Log principal
├── system.log             # Log de execução em background
└── *.log.gz               # Logs comprimidos (rotação)
```

### Screenshots de Debug
```
screenshots/
├── login_failed.png       # Falhas de login
├── bet_success_*.png      # Apostas bem-sucedidas
└── bet_error_*.png        # Erros na execução
```

### Métricas Importantes
- Número de mensagens processadas
- Apostas executadas com sucesso
- Falhas de login/conexão
- Tempo de resposta do sistema

## 🔒 Segurança e Boas Práticas

### Proteção de Credenciais
- Nunca compartilhe arquivo `.env`
- Use senhas fortes e únicas
- Habilite 2FA no Telegram
- Monitore atividade das contas

### Limites de Segurança
- Defina valores máximos de aposta
- Monitore logs regularmente
- Execute em ambiente isolado
- Faça backup das configurações

### Detecção de Problemas
- Monitore taxa de sucesso das apostas
- Verifique logs de erro regularmente
- Observe mudanças no comportamento
- Teste periodicamente em modo manual

## 📞 Suporte

### Auto-diagnóstico
```bash
# Executar teste completo
python3 test_system.py

# Verificar configuração
python3 -c "from src.config import validate_config; validate_config()"

# Testar navegador
python3 -c "from src.browser_manager import BrowserManager; print('OK')"
```

### Informações do Sistema
```bash
# Versão Python
python3 --version

# Versão Chrome
google-chrome --version

# Espaço em disco
df -h

# Memória disponível
free -h
```

### Logs de Debug
Para debug detalhado, configure:
```env
LOG_LEVEL=DEBUG
ENABLE_HEADLESS=false
```

Isso permitirá ver o navegador em ação e logs mais detalhados.
