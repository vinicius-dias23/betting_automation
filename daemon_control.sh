#!/bin/bash

# Script de controle do daemon de automação de apostas

DAEMON_DIR="/home/ubuntu/betting_automation"
DAEMON_SCRIPT="$DAEMON_DIR/daemon_runner.py"
DAEMON_LOG="$DAEMON_DIR/logs/daemon.log"
STATUS_FILE="$DAEMON_DIR/daemon_status.json"

cd "$DAEMON_DIR"

case "$1" in
    start)
        echo "🚀 Iniciando daemon de automação de apostas..."
        nohup python3 "$DAEMON_SCRIPT" start > /dev/null 2>&1 &
        sleep 2
        echo "✅ Daemon iniciado!"
        echo "📋 Para verificar status: $0 status"
        echo "📄 Para ver logs: $0 logs"
        ;;
    
    stop)
        echo "🛑 Parando daemon..."
        python3 "$DAEMON_SCRIPT" stop
        echo "✅ Daemon parado!"
        ;;
    
    restart)
        echo "🔄 Reiniciando daemon..."
        python3 "$DAEMON_SCRIPT" stop
        sleep 3
        nohup python3 "$DAEMON_SCRIPT" start > /dev/null 2>&1 &
        sleep 2
        echo "✅ Daemon reiniciado!"
        ;;
    
    status)
        echo "📊 Status do daemon:"
        if [ -f "$STATUS_FILE" ]; then
            python3 -c "
import json
with open('$STATUS_FILE', 'r') as f:
    status = json.load(f)
    print(f\"Status: {status.get('status', 'unknown')}\")
    print(f\"Timestamp: {status.get('timestamp', 'N/A')}\")
    print(f\"Reinicializações: {status.get('restart_count', 0)}\")
    if status.get('pid'):
        print(f\"PID: {status['pid']}\")
    if status.get('details'):
        print(f\"Detalhes: {status['details']}\")
"
        else
            echo "❌ Arquivo de status não encontrado"
        fi
        ;;
    
    logs)
        echo "📄 Logs do daemon (últimas 50 linhas):"
        if [ -f "$DAEMON_LOG" ]; then
            tail -n 50 "$DAEMON_LOG"
        else
            echo "❌ Arquivo de log não encontrado"
        fi
        ;;
    
    logs-live)
        echo "📄 Acompanhando logs em tempo real (Ctrl+C para sair):"
        if [ -f "$DAEMON_LOG" ]; then
            tail -f "$DAEMON_LOG"
        else
            echo "❌ Arquivo de log não encontrado"
        fi
        ;;
    
    system-logs)
        echo "📄 Logs do sistema principal (últimas 50 linhas):"
        SYSTEM_LOG="$DAEMON_DIR/logs/system.log"
        if [ -f "$SYSTEM_LOG" ]; then
            tail -n 50 "$SYSTEM_LOG"
        else
            echo "❌ Arquivo de log do sistema não encontrado"
        fi
        ;;
    
    *)
        echo "Sistema de Controle do Daemon de Automação de Apostas"
        echo ""
        echo "Uso: $0 {start|stop|restart|status|logs|logs-live|system-logs}"
        echo ""
        echo "Comandos:"
        echo "  start       - Inicia o daemon"
        echo "  stop        - Para o daemon"
        echo "  restart     - Reinicia o daemon"
        echo "  status      - Mostra status atual"
        echo "  logs        - Mostra logs do daemon"
        echo "  logs-live   - Acompanha logs em tempo real"
        echo "  system-logs - Mostra logs do sistema principal"
        echo ""
        exit 1
        ;;
esac
