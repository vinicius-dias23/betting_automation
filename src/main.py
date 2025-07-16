
#!/usr/bin/env python3
"""
Sistema de Automação de Apostas Esportivas
Monitora grupo do Telegram e executa apostas automaticamente
"""

import sys
import signal
import time
from pathlib import Path
from loguru import logger

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from config import Config, validate_config
from telegram_watcher import TelegramWatcher
from bet_executor import BetExecutor

class BettingAutomationSystem:
    """Sistema principal de automação de apostas"""
    
    def __init__(self):
        self.telegram_watcher = None
        self.bet_executor = None
        self.running = False
        
        # Configurar logging
        self._setup_logging()
        
        # Configurar handler para interrupção
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Configura sistema de logging"""
        # Remover handler padrão
        logger.remove()
        
        # Adicionar handler para console
        logger.add(
            sys.stdout,
            level=Config.LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
        
        # Adicionar handler para arquivo
        logger.add(
            "logs/betting_automation.log",
            level=Config.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        
        logger.info("Sistema de logging configurado")
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        logger.info(f"Sinal {signum} recebido, encerrando sistema...")
        self.stop()
    
    def initialize(self) -> bool:
        """Inicializa componentes do sistema"""
        try:
            logger.info("Inicializando Sistema de Automação de Apostas...")
            
            # Validar configurações
            validate_config()
            logger.info("Configurações validadas")
            
            # Inicializar componentes
            self.telegram_watcher = TelegramWatcher()
            self.bet_executor = BetExecutor()
            
            logger.info("Componentes inicializados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False
    
    def on_new_bet_detected(self, bet_info: dict):
        """Callback executado quando nova aposta é detectada"""
        try:
            logger.info("="*60)
            logger.info("NOVA APOSTA DETECTADA!")
            logger.info("="*60)
            
            # Log das informações da aposta
            logger.info(f"Evento: {bet_info.get('evento', 'N/A')}")
            logger.info(f"Valor: R$ {bet_info.get('valor_numerico', 'N/A')}")
            logger.info(f"Odds: {bet_info.get('odds', 'N/A')}")
            logger.info(f"Link: {bet_info.get('link', 'N/A')}")
            
            # Executar aposta
            logger.info("Executando aposta...")
            success = self.bet_executor.execute_bet(bet_info)
            
            if success:
                logger.success("✅ APOSTA EXECUTADA COM SUCESSO!")
                
                # Notificação (se habilitada)
                if Config.ENABLE_NOTIFICATIONS:
                    self._send_notification("Aposta executada com sucesso!", bet_info)
            else:
                logger.error("❌ FALHA NA EXECUÇÃO DA APOSTA")
                
                # Notificação de erro (se habilitada)
                if Config.ENABLE_NOTIFICATIONS:
                    self._send_notification("Falha na execução da aposta", bet_info)
            
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Erro no callback de nova aposta: {e}")
    
    def _send_notification(self, title: str, bet_info: dict):
        """Envia notificação (placeholder para implementação futura)"""
        try:
            # Aqui pode ser implementado envio de email, webhook, etc.
            logger.info(f"NOTIFICAÇÃO: {title}")
            logger.info(f"Detalhes: {bet_info}")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
    
    def start(self):
        """Inicia o sistema de automação"""
        try:
            if not self.initialize():
                logger.error("Falha na inicialização, sistema não pode ser iniciado")
                return False
            
            logger.info("🚀 INICIANDO SISTEMA DE AUTOMAÇÃO DE APOSTAS")
            logger.info(f"Grupo Telegram: {Config.TELEGRAM_GROUP_URL}")
            logger.info(f"Site de Apostas: {Config.BET_SITE_BASE_URL}")
            logger.info(f"Intervalo de Verificação: {Config.CHECK_INTERVAL_SECONDS}s")
            logger.info(f"Valor Padrão: R$ {Config.DEFAULT_BET_AMOUNT}")
            
            self.running = True
            
            # Iniciar monitoramento do Telegram
            logger.info("Iniciando monitoramento do Telegram...")
            self.telegram_watcher.start_monitoring(self.on_new_bet_detected)
            
        except KeyboardInterrupt:
            logger.info("Sistema interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro durante execução: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Para o sistema de automação"""
        if not self.running:
            return
        
        logger.info("Parando sistema de automação...")
        self.running = False
        
        try:
            if self.telegram_watcher:
                self.telegram_watcher.close()
            
            if self.bet_executor:
                self.bet_executor.close()
            
            logger.info("Sistema parado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao parar sistema: {e}")

def main():
    """Função principal"""
    try:
        # Banner
        print("\n" + "="*60)
        print("    SISTEMA DE AUTOMAÇÃO DE APOSTAS ESPORTIVAS")
        print("="*60)
        print("⚠️  AVISO: Use por sua conta e risco!")
        print("⚠️  Apostas podem resultar em perdas financeiras!")
        print("⚠️  Este sistema é apenas para fins educacionais!")
        print("="*60 + "\n")
        
        # Confirmar início
        response = input("Deseja continuar? (s/N): ").strip().lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("Sistema cancelado pelo usuário.")
            return
        
        # Iniciar sistema
        system = BettingAutomationSystem()
        system.start()
        
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
