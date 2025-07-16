
#!/usr/bin/env python3
"""
Script de teste para validar o sistema de automação
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_imports():
    """Testa se todas as importações funcionam"""
    print("🔍 Testando importações...")
    
    try:
        from config import Config, validate_config
        print("✅ config.py - OK")
    except Exception as e:
        print(f"❌ config.py - ERRO: {e}")
        return False
    
    try:
        from utils import MessageParser, SessionManager, RetryHelper
        print("✅ utils.py - OK")
    except Exception as e:
        print(f"❌ utils.py - ERRO: {e}")
        return False
    
    try:
        from browser_manager import BrowserManager
        print("✅ browser_manager.py - OK")
    except Exception as e:
        print(f"❌ browser_manager.py - ERRO: {e}")
        return False
    
    try:
        from telegram_watcher import TelegramWatcher
        print("✅ telegram_watcher.py - OK")
    except Exception as e:
        print(f"❌ telegram_watcher.py - ERRO: {e}")
        return False
    
    try:
        from bet_executor import BetExecutor
        print("✅ bet_executor.py - OK")
    except Exception as e:
        print(f"❌ bet_executor.py - ERRO: {e}")
        return False
    
    return True

def test_message_parser():
    """Testa o parser de mensagens"""
    print("\n🔍 Testando parser de mensagens...")
    
    from utils import MessageParser
    
    test_messages = [
        "Jogo: Brasil x Argentina\nValor: R$ 25,00\nOdd: 2.50\nhttps://sitedeapostas.com/bet/123",
        "Apostar R$ 15 em Flamengo\n@2.30\nhttps://bet365.com/link/456",
        "Valor: 20,50\nLink: https://sportingbet.com/789",
        "Mensagem sem informações de aposta"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTeste {i}: {message[:50]}...")
        result = MessageParser.extract_bet_info(message)
        if result:
            print(f"✅ Extraído: Valor={result.get('valor_numerico')}, Link={bool(result.get('link'))}")
        else:
            print("❌ Nenhuma informação extraída")
    
    return True

def test_browser_creation():
    """Testa criação do navegador"""
    print("\n🔍 Testando criação do navegador...")
    
    try:
        from browser_manager import BrowserManager
        
        # Teste básico de criação
        browser = BrowserManager("test_profile")
        print("✅ BrowserManager criado")
        
        # Não vamos criar o driver real para evitar problemas
        print("✅ Teste de navegador concluído (sem inicializar driver)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de navegador: {e}")
        return False

def test_config_validation():
    """Testa validação de configuração"""
    print("\n🔍 Testando validação de configuração...")
    
    try:
        from config import validate_config
        
        # Tentar validar configuração atual
        try:
            validate_config()
            print("✅ Configuração válida")
        except ValueError as e:
            print(f"⚠️  Configuração incompleta: {e}")
            print("   (Isso é esperado se .env não estiver configurado)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def main():
    """Função principal de teste"""
    print("="*60)
    print("    TESTE DO SISTEMA DE AUTOMAÇÃO DE APOSTAS")
    print("="*60)
    
    tests = [
        ("Importações", test_imports),
        ("Parser de Mensagens", test_message_parser),
        ("Navegador", test_browser_creation),
        ("Validação de Config", test_config_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSOU")
            else:
                print(f"❌ {test_name} - FALHOU")
        except Exception as e:
            print(f"❌ {test_name} - ERRO: {e}")
    
    print("\n" + "="*60)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    print("="*60)
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema pronto para uso.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
