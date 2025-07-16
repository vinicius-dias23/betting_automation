
import re
import time
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class MessageParser:
    """Classe para extrair informações das mensagens do Telegram"""
    
    @staticmethod
    def extract_bet_info(message_text: str) -> Optional[Dict]:
        """
        Extrai informações de aposta da mensagem do Telegram
        Formato esperado: valor da aposta, link, detalhes
        """
        try:
            # Padrões regex para diferentes formatos de mensagem
            patterns = {
                'valor': [
                    r'(?:valor|aposta|stake):\s*R?\$?\s*(\d+(?:[.,]\d{2})?)',
                    r'apostar\s+R?\$?\s*(\d+(?:[.,]\d{2})?)',
                    r'(\d+(?:[.,]\d{2})?)\s*(?:reais|R\$)',
                ],
                'link': [
                    r'(https?://[^\s]+)',
                    r'(?:link|url):\s*(https?://[^\s]+)',
                ],
                'odds': [
                    r'(?:odd|cotação):\s*(\d+[.,]\d+)',
                    r'@(\d+[.,]\d+)',
                ],
                'evento': [
                    r'(?:jogo|partida|evento):\s*([^\n]+)',
                    r'([A-Za-z\s]+\s+x\s+[A-Za-z\s]+)',
                ]
            }
            
            extracted_info = {}
            
            # Extrair cada tipo de informação
            for info_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, message_text, re.IGNORECASE)
                    if match:
                        extracted_info[info_type] = match.group(1).strip()
                        break
            
            # Validar se temos pelo menos valor e link
            if 'valor' in extracted_info and 'link' in extracted_info:
                # Normalizar valor (trocar vírgula por ponto)
                valor_str = extracted_info['valor'].replace(',', '.')
                extracted_info['valor_numerico'] = float(valor_str)
                
                logger.info(f"Informações extraídas: {extracted_info}")
                return extracted_info
            else:
                logger.warning(f"Informações insuficientes na mensagem: {message_text[:100]}...")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao extrair informações da mensagem: {e}")
            return None

class SessionManager:
    """Gerenciador de sessões para persistência de login"""
    
    def __init__(self, session_file: str):
        self.session_file = Path(session_file)
    
    def save_cookies(self, driver) -> bool:
        """Salva cookies da sessão atual"""
        try:
            cookies = driver.get_cookies()
            with open(self.session_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Sessão salva com {len(cookies)} cookies")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar sessão: {e}")
            return False
    
    def load_cookies(self, driver, domain: str) -> bool:
        """Carrega cookies salvos para a sessão atual"""
        if not self.session_file.exists():
            logger.info("Nenhuma sessão salva encontrada")
            return False
        
        try:
            with open(self.session_file, 'r') as f:
                cookies = json.load(f)
            
            if not cookies:
                return False
            
            # Navegar para o domínio antes de adicionar cookies
            driver.get(f'https://{domain}')
            
            loaded_count = 0
            for cookie in cookies:
                try:
                    # Remover chaves problemáticas
                    cookie.pop('expiry', None)
                    cookie.pop('sameSite', None)
                    driver.add_cookie(cookie)
                    loaded_count += 1
                except Exception as e:
                    logger.warning(f"Falha ao carregar cookie {cookie.get('name')}: {e}")
            
            logger.info(f"Carregados {loaded_count} cookies")
            driver.refresh()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar sessão: {e}")
            return False
    
    def clear_session(self):
        """Remove arquivo de sessão"""
        if self.session_file.exists():
            self.session_file.unlink()
            logger.info("Sessão limpa")

class RetryHelper:
    """Helper para operações com retry"""
    
    @staticmethod
    def retry_operation(func, max_retries: int = 3, delay: int = 5, *args, **kwargs):
        """Executa operação com retry em caso de falha"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay + random.uniform(0, 2))  # Adiciona jitter
                    continue
                raise
        return None

class ElementWaiter:
    """Helper para aguardar elementos na página"""
    
    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
    
    def wait_for_element(self, by: By, value: str, timeout: int = None):
        """Aguarda elemento estar presente"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = None):
        """Aguarda elemento estar clicável"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def wait_for_text_in_element(self, by: By, value: str, text: str, timeout: int = None):
        """Aguarda texto específico aparecer no elemento"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        return wait.until(EC.text_to_be_present_in_element((by, value), text))

def human_like_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Adiciona delay humanizado entre ações"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def take_screenshot(driver, filename: str = None):
    """Captura screenshot para debug"""
    if not filename:
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
    
    screenshot_path = Path('screenshots') / filename
    try:
        driver.save_screenshot(str(screenshot_path))
        logger.info(f"Screenshot salvo: {screenshot_path}")
        return str(screenshot_path)
    except Exception as e:
        logger.error(f"Erro ao salvar screenshot: {e}")
        return None

def validate_bet_amount(amount: float, min_amount: float, max_amount: float) -> float:
    """Valida e ajusta valor da aposta dentro dos limites"""
    if amount < min_amount:
        logger.warning(f"Valor {amount} menor que mínimo {min_amount}, ajustando")
        return min_amount
    elif amount > max_amount:
        logger.warning(f"Valor {amount} maior que máximo {max_amount}, ajustando")
        return max_amount
    return amount
