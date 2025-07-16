
#!/bin/bash

# Script para executar o sistema de automação de apostas

set -e

echo "=========================================="
echo "  Sistema de Automação de Apostas"
echo "=========================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p logs
mkdir -p screenshots

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📋 Copiando .env.example para .env..."
    cp .env.example .env
    echo ""
    echo "🔧 CONFIGURE O ARQUIVO .env ANTES DE CONTINUAR!"
    echo "   Edite o arquivo .env com suas credenciais:"
    echo "   - TELEGRAM_PHONE"
    echo "   - TELEGRAM_GROUP_URL"
    echo "   - BET_SITE_USERNAME"
    echo "   - BET_SITE_PASSWORD"
    echo "   - BET_SITE_BASE_URL"
    echo ""
    echo "   Depois execute novamente: ./run.sh"
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar se Chrome está instalado
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  Chrome/Chromium não encontrado!"
    echo "📥 Instalando Chrome..."
    
    # Detectar sistema operacional
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable
        # CentOS/RHEL/Fedora
        elif command -v yum &> /dev/null; then
            sudo yum install -y google-chrome-stable
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y google-chrome-stable
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "❌ Instale o Chrome manualmente no macOS"
        exit 1
    fi
fi

echo ""
echo "✅ Ambiente configurado com sucesso!"
echo ""

# Perguntar modo de execução
echo "Escolha o modo de execução:"
echo "1) Executar em primeiro plano (recomendado para teste)"
echo "2) Executar em segundo plano (daemon)"
echo "3) Apenas validar configuração"
echo ""
read -p "Opção (1-3): " choice

case $choice in
    1)
        echo "🚀 Executando em primeiro plano..."
        python3 src/main.py
        ;;
    2)
        echo "🚀 Executando em segundo plano..."
        nohup python3 src/main.py > logs/system.log 2>&1 &
        PID=$!
        echo "Sistema iniciado com PID: $PID"
        echo "Para parar: kill $PID"
        echo "Para ver logs: tail -f logs/system.log"
        ;;
    3)
        echo "🔍 Validando configuração..."
        python3 -c "
from src.config import validate_config
try:
    validate_config()
    print('✅ Configuração válida!')
except Exception as e:
    print(f'❌ Erro na configuração: {e}')
"
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac
