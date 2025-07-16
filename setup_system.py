
#!/usr/bin/env python3
"""
Script de configuração inicial do sistema
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} OK")
    return True

def install_chrome():
    """Instala Chrome se necessário"""
    try:
        # Verificar se Chrome já está instalado
        result = subprocess.run(['which', 'google-chrome'], capture_output=True)
        if result.returncode == 0:
            print("✅ Chrome já instalado")
            return True
        
        print("📥 Instalando Chrome...")
        
        # Detectar sistema operacional
        if sys.platform.startswith('linux'):
            # Ubuntu/Debian
            commands = [
                ['wget', '-q', '-O', '-', 'https://dl.google.com/linux/linux_signing_key.pub'],
                ['sudo', 'apt-key', 'add', '-'],
                ['sudo', 'sh', '-c', 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'],
                ['sudo', 'apt-get', 'update'],
                ['sudo', 'apt-get', 'install', '-y', 'google-chrome-stable']
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Erro ao executar: {' '.join(cmd)}")
                    print(f"Erro: {result.stderr}")
                    return False
            
            print("✅ Chrome instalado com sucesso")
            return True
        else:
            print("❌ Instalação automática do Chrome não suportada neste OS")
            print("Por favor, instale o Chrome manualmente")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao instalar Chrome: {e}")
        return False

def create_virtual_environment():
    """Cria ambiente virtual"""
    try:
        if Path('venv').exists():
            print("✅ Ambiente virtual já existe")
            return True
        
        print("📦 Criando ambiente virtual...")
        result = subprocess.run([sys.executable, '-m', 'venv', 'venv'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erro ao criar ambiente virtual: {result.stderr}")
            return False
        
        print("✅ Ambiente virtual criado")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar ambiente virtual: {e}")
        return False

def install_dependencies():
    """Instala dependências Python"""
    try:
        print("📥 Instalando dependências...")
        
        # Ativar ambiente virtual e instalar dependências
        if sys.platform.startswith('win'):
            pip_path = 'venv\\Scripts\\pip.exe'
        else:
            pip_path = 'venv/bin/pip'
        
        commands = [
            [pip_path, 'install', '--upgrade', 'pip'],
            [pip_path, 'install', '-r', 'requirements.txt']
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Erro ao executar: {' '.join(cmd)}")
                print(f"Erro: {result.stderr}")
                return False
        
        print("✅ Dependências instaladas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = ['logs', 'screenshots', 'chrome_profiles']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Diretório {directory} criado")

def setup_config():
    """Configura arquivo .env"""
    if Path('.env').exists():
        print("✅ Arquivo .env já existe")
        return True
    
    if not Path('.env.example').exists():
        print("❌ Arquivo .env.example não encontrado")
        return False
    
    # Copiar .env.example para .env
    with open('.env.example', 'r') as src, open('.env', 'w') as dst:
        dst.write(src.read())
    
    print("✅ Arquivo .env criado a partir do .env.example")
    print("")
    print("🔧 IMPORTANTE: Configure o arquivo .env com suas credenciais!")
    print("   Edite os seguintes campos:")
    print("   - TELEGRAM_PHONE")
    print("   - TELEGRAM_GROUP_URL") 
    print("   - BET_SITE_USERNAME")
    print("   - BET_SITE_PASSWORD")
    print("   - BET_SITE_BASE_URL")
    
    return True

def main():
    """Função principal de setup"""
    print("="*60)
    print("    CONFIGURAÇÃO DO SISTEMA DE AUTOMAÇÃO DE APOSTAS")
    print("="*60)
    
    steps = [
        ("Verificando Python", check_python_version),
        ("Criando diretórios", create_directories),
        ("Criando ambiente virtual", create_virtual_environment),
        ("Instalando dependências", install_dependencies),
        ("Instalando Chrome", install_chrome),
        ("Configurando .env", setup_config),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Falha em: {step_name}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("\n📋 Próximos passos:")
    print("1. Configure o arquivo .env com suas credenciais")
    print("2. Execute: ./run.sh")
    print("\n⚠️  Lembre-se: Use por sua conta e risco!")

if __name__ == "__main__":
    main()
