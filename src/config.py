
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    # Configurações do Telegram
    TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
    TELEGRAM_PASSWORD = os.getenv('TELEGRAM_PASSWORD')
    TELEGRAM_GROUP_URL = os.getenv('TELEGRAM_GROUP_URL')
    TELEGRAM_SESSION_FILE = os.getenv('TELEGRAM_SESSION_FILE', 'telegram_session.json')
    
    # Configurações do Site de Apostas
    BET_SITE_USERNAME = os.getenv('BET_SITE_USERNAME')
    BET_SITE_PASSWORD = os.getenv('BET_SITE_PASSWORD')
    BET_SITE_BASE_URL = os.getenv('BET_SITE_BASE_URL')
    
    # Configurações Gerais
    CHROME_PROFILE_DIR = Path(os.getenv('CHROME_PROFILE_DIR', './chrome_profiles/betting_profile'))
    DEFAULT_BET_AMOUNT = float(os.getenv('DEFAULT_BET_AMOUNT', '10.00'))
    MAX_BET_AMOUNT = float(os.getenv('MAX_BET_AMOUNT', '100.00'))
    MIN_BET_AMOUNT = float(os.getenv('MIN_BET_AMOUNT', '5.00'))
    CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '30'))
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Configurações de Segurança
    ENABLE_HEADLESS = os.getenv('ENABLE_HEADLESS', 'true').lower() == 'true'
    ENABLE_STEALTH_MODE = os.getenv('ENABLE_STEALTH_MODE', 'true').lower() == 'true'
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY_SECONDS = int(os.getenv('RETRY_DELAY_SECONDS', '5'))
    
    # Criar diretórios necessários
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    Path('screenshots').mkdir(exist_ok=True)

# Validação de configurações obrigatórias
def validate_config():
    required_vars = [
        'TELEGRAM_PHONE', 'TELEGRAM_GROUP_URL', 
        'BET_SITE_USERNAME', 'BET_SITE_PASSWORD', 'BET_SITE_BASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(Config, var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing_vars)}")
    
    return True
