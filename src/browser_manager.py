
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from fake_useragent import UserAgent
from pathlib import Path
import time
import random
from loguru import logger
from config import Config

class BrowserManager:
    """Gerenciador de instâncias do navegador com configurações otimizadas"""
    
    def __init__(self, profile_name: str = "default"):
        self.profile_name = profile_name
        self.profile_dir = Config.CHROME_PROFILE_DIR / profile_name
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.driver = None
        self.ua = UserAgent()
    
    def create_driver(self, headless: bool = None, stealth: bool = None) -> uc.Chrome:
        """Cria instância do Chrome com configurações otimizadas"""
        if headless is None:
            headless = Config.ENABLE_HEADLESS
        if stealth is None:
            stealth = Config.ENABLE_STEALTH_MODE
        
        try:
            options = Options()
            
            # Configurações básicas
            if headless:
                options.add_argument('--headless=new')
            
            # Configurações de perfil persistente
            options.add_argument(f'--user-data-dir={self.profile_dir}')
            options.add_argument('--profile-directory=Default')
            
            # Configurações de segurança e performance
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Acelera carregamento
            options.add_argument('--disable-javascript')  # Pode ser removido se necessário
            
            # Configurações anti-detecção
            if stealth:
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument(f'--user-agent={self.ua.random}')
            
            # Configurações de janela
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            
            # Configurações de rede
            options.add_argument('--aggressive-cache-discard')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            
            # Preferências adicionais
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,  # Bloquear notificações
                    "media_stream": 2,   # Bloquear câmera/microfone
                },
                "profile.managed_default_content_settings": {
                    "images": 2  # Bloquear imagens para velocidade
                }
            }
            options.add_experimental_option("prefs", prefs)
            
            # Criar driver com undetected-chromedriver para melhor stealth
            if stealth:
                self.driver = uc.Chrome(options=options, version_main=None)
            else:
                self.driver = uc.Chrome(options=options)
            
            # Configurações pós-inicialização para stealth
            if stealth:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": self.ua.random
                })
            
            logger.info(f"Driver criado com sucesso - Headless: {headless}, Stealth: {stealth}")
            return self.driver
            
        except Exception as e:
            logger.error(f"Erro ao criar driver: {e}")
            raise
    
    def get_driver(self) -> uc.Chrome:
        """Retorna driver existente ou cria novo"""
        if self.driver is None:
            self.create_driver()
        return self.driver
    
    def restart_driver(self):
        """Reinicia o driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.driver = None
        return self.create_driver()
    
    def close_driver(self):
        """Fecha o driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {e}")
            finally:
                self.driver = None
    
    def navigate_with_retry(self, url: str, max_retries: int = 3) -> bool:
        """Navega para URL com retry em caso de falha"""
        for attempt in range(max_retries):
            try:
                driver = self.get_driver()
                driver.get(url)
                
                # Aguardar carregamento
                time.sleep(random.uniform(2, 4))
                
                # Verificar se página carregou
                if driver.current_url and "about:blank" not in driver.current_url:
                    logger.info(f"Navegação bem-sucedida para: {url}")
                    return True
                else:
                    raise WebDriverException("Página não carregou corretamente")
                    
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou para {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 6))
                    continue
                else:
                    logger.error(f"Falha ao navegar para {url} após {max_retries} tentativas")
                    return False
        return False
    
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Aguarda carregamento completo da página"""
        try:
            driver = self.get_driver()
            
            # Aguardar JavaScript terminar
            for _ in range(timeout):
                ready_state = driver.execute_script("return document.readyState")
                if ready_state == "complete":
                    time.sleep(1)  # Aguardar um pouco mais
                    return True
                time.sleep(1)
            
            logger.warning(f"Timeout aguardando carregamento da página após {timeout}s")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao aguardar carregamento da página: {e}")
            return False
    
    def handle_cloudflare(self) -> bool:
        """Tenta lidar com proteção Cloudflare"""
        try:
            driver = self.get_driver()
            
            # Verificar se há challenge do Cloudflare
            if "cloudflare" in driver.page_source.lower() or "checking your browser" in driver.page_source.lower():
                logger.info("Detectado challenge Cloudflare, aguardando...")
                
                # Aguardar até 60 segundos para resolver
                for _ in range(60):
                    time.sleep(1)
                    if "cloudflare" not in driver.page_source.lower():
                        logger.info("Challenge Cloudflare resolvido")
                        return True
                
                logger.warning("Timeout aguardando resolução do Cloudflare")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao lidar com Cloudflare: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()
