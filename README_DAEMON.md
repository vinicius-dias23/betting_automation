# Sistema de Automação de Apostas - Daemon 24/7

## 📋 Visão Geral

O sistema de automação de apostas agora possui um daemon robusto que executa continuamente 24/7 com:

- ✅ **Execução contínua**: Mantém o sistema rodando ininterruptamente
- ✅ **Monitoramento automático**: Verifica status a cada hora
- ✅ **Recuperação automática**: Reinicia automaticamente em caso de falhas
- ✅ **Logs persistentes**: Mantém histórico completo de execução
- ✅ **Configuração robusta**: Funciona mesmo após reinicializações do sistema

## 🚀 Como Usar

### Controle Manual do Daemon

```bash
# Iniciar daemon
./daemon_control.sh start

# Parar daemon
./daemon_control.sh stop

# Reiniciar daemon
./daemon_control.sh restart

# Ver status
./daemon_control.sh status

# Ver logs do daemon
./daemon_control.sh logs

# Acompanhar logs em tempo real
./daemon_control.sh logs-live

# Ver logs do sistema principal
./daemon_control.sh system-logs
```

### Tarefa Agendada Automática

Uma tarefa agendada foi configurada para:
- **Frequência**: A cada 1 hora
- **Função**: Verificar se o daemon está rodando
- **Ação**: Reiniciar automaticamente se necessário
- **Relatórios**: Gerar relatórios de status em `/status_reports/`

## 📁 Estrutura de Arquivos

```
/home/ubuntu/betting_automation/
├── daemon_runner.py          # Script principal do daemon
├── daemon_control.sh         # Script de controle
├── daemon_status.json        # Status atual do daemon
├── logs/
│   ├── daemon.log           # Logs do daemon
│   └── system.log           # Logs do sistema principal
└── status_reports/
    └── status_report.md     # Relatórios de status
```

## 🔧 Funcionamento do Daemon

### Características Principais

1. **Monitoramento Contínuo**
   - Verifica processo principal a cada 10 segundos
   - Detecta falhas e crashes automaticamente

2. **Recuperação Automática**
   - Até 10 tentativas de reinicialização
   - Delay de 30 segundos entre tentativas
   - Logs detalhados de cada tentativa

3. **Gestão de Logs**
   - Logs com timestamp para daemon e sistema
   - Rotação automática de logs
   - Separação entre logs do daemon e sistema principal

4. **Status Persistente**
   - Arquivo JSON com status atual
   - Informações de PID, reinicializações e detalhes
   - Histórico de execução

### Estados do Daemon

- **running**: Daemon e sistema principal executando normalmente
- **starting**: Daemon iniciando o sistema principal
- **restarting**: Daemon reiniciando após falha
- **stopped**: Daemon parado manualmente
- **error**: Erro crítico que impediu execução

## 📊 Monitoramento

### Verificação de Status
```bash
# Status rápido
./daemon_control.sh status

# Status detalhado via Python
python3 daemon_runner.py status
```

### Logs em Tempo Real
```bash
# Logs do daemon
./daemon_control.sh logs-live

# Logs do sistema
tail -f logs/system.log
```

### Relatórios Automáticos

Os relatórios de status são gerados automaticamente a cada hora em:
`/home/ubuntu/betting_automation/status_reports/`

Contêm:
- Status atual do sistema
- Estatísticas de funcionamento
- Alertas e problemas detectados
- Histórico de reinicializações

## 🛠️ Solução de Problemas

### Daemon Não Inicia

1. Verificar se ambiente virtual existe:
   ```bash
   ls -la venv/
   ```

2. Verificar arquivo .env:
   ```bash
   cat .env
   ```

3. Verificar logs:
   ```bash
   ./daemon_control.sh logs
   ```

### Sistema Principal Falha Constantemente

1. Verificar configurações no .env
2. Verificar logs do sistema:
   ```bash
   ./daemon_control.sh system-logs
   ```
3. Testar execução manual:
   ```bash
   ./run.sh
   ```

### Muitas Reinicializações

O daemon para automaticamente após 10 reinicializações para evitar loops infinitos. Para resetar:

```bash
./daemon_control.sh stop
./daemon_control.sh start
```

## 🔒 Segurança

- Daemon executa com permissões do usuário atual
- Logs não expõem credenciais sensíveis
- Processo isolado em ambiente virtual
- Controle de acesso via arquivos de sistema

## 📈 Performance

- **Uso de CPU**: Mínimo (verificações a cada 10s)
- **Uso de Memória**: ~50-100MB para daemon + sistema principal
- **Logs**: Rotação automática para evitar crescimento excessivo
- **Rede**: Apenas tráfego necessário para Telegram e site de apostas

## 🔄 Backup e Recuperação

### Arquivos Importantes para Backup
- `.env` (configurações)
- `logs/` (histórico)
- `status_reports/` (relatórios)
- `daemon_status.json` (status atual)

### Recuperação Após Falha do Sistema
1. Restaurar arquivos de backup
2. Executar: `./daemon_control.sh start`
3. Verificar: `./daemon_control.sh status`

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs: `./daemon_control.sh logs`
2. Verificar status: `./daemon_control.sh status`
3. Consultar este README
4. Verificar relatórios em `/status_reports/`
