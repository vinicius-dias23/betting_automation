
import time
import json
from datetime import datetime
from typing import Optional, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger

from browser_manager import BrowserManager
from utils import SessionManager, MessageParser, ElementWaiter, human_like_delay, take_screenshot
from config import Config

class TelegramWatcher:
    """Classe para monitorar mensagens no Telegram Web"""
    
    def __init__(self):
        self.browser_manager = BrowserManager("telegram_profile")
        self.session_manager = SessionManager(Config.TELEGRAM_SESSION_FILE)
        self.last_message_id = None
        self.last_message_text = ""
        self.is_logged_in = False
    
    def login(self) -> bool:
        """Realiza login no Telegram Web"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Tentar carregar sessão existente
            if self.session_manager.load_cookies(driver, "web.telegram.org"):
                logger.info("Tentando usar sessão salva...")
                driver.get("https://web.telegram.org/k/")
                
                # Aguardar carregamento e verificar se está logado
                time.sleep(5)
                if self._check_login_status():
                    logger.info("Login realizado com sessão salva")
                    self.is_logged_in = True
                    return True
            
            # Se não conseguiu com sessão salva, fazer login manual
            logger.info("Realizando login manual no Telegram...")
            driver.get("https://web.telegram.org/k/")
            
            # Aguardar página carregar
            self.browser_manager.wait_for_page_load()
            
            waiter = ElementWaiter(driver)
            
            # Aguardar campo de telefone
            try:
                phone_input = waiter.wait_for_element(By.CSS_SELECTOR, 'input[type="tel"]', 15)
                phone_input.clear()
                phone_input.send_keys(Config.TELEGRAM_PHONE)
                human_like_delay()
                
                # Clicar em "Next" ou "Avançar"
                next_button = waiter.wait_for_clickable(By.CSS_SELECTOR, 'button[type="submit"], .btn-primary', 10)
                next_button.click()
                
                logger.info("Número de telefone inserido, aguardando código...")
                
                # Aguardar campo de código
                code_input = waiter.wait_for_element(By.CSS_SELECTOR, 'input[type="tel"], input[type="text"]', 30)
                
                # Solicitar código ao usuário
                print("\n" + "="*50)
                print("CÓDIGO DE VERIFICAÇÃO NECESSÁRIO")
                print("="*50)
                print("Um código foi enviado para seu Telegram.")
                print("Digite o código recebido:")
                verification_code = input("Código: ").strip()
                
                code_input.clear()
                code_input.send_keys(verification_code)
                human_like_delay()
                
                # Clicar em confirmar
                confirm_button = waiter.wait_for_clickable(By.CSS_SELECTOR, 'button[type="submit"], .btn-primary', 10)
                confirm_button.click()
                
                # Verificar se precisa de senha (2FA)
                try:
                    password_input = waiter.wait_for_element(By.CSS_SELECTOR, 'input[type="password"]', 10)
                    if Config.TELEGRAM_PASSWORD:
                        password_input.send_keys(Config.TELEGRAM_PASSWORD)
                        human_like_delay()
                        
                        password_confirm = waiter.wait_for_clickable(By.CSS_SELECTOR, 'button[type="submit"], .btn-primary', 5)
                        password_confirm.click()
                    else:
                        print("Senha 2FA necessária:")
                        password = input("Senha: ").strip()
                        password_input.send_keys(password)
                        human_like_delay()
                        
                        password_confirm = waiter.wait_for_clickable(By.CSS_SELECTOR, 'button[type="submit"], .btn-primary', 5)
                        password_confirm.click()
                        
                except TimeoutException:
                    logger.info("Senha 2FA não necessária")
                
                # Aguardar login completar
                time.sleep(10)
                
                if self._check_login_status():
                    logger.info("Login realizado com sucesso")
                    self.session_manager.save_cookies(driver)
                    self.is_logged_in = True
                    return True
                else:
                    logger.error("Falha no login - interface não carregou")
                    take_screenshot(driver, "login_failed.png")
                    return False
                    
            except TimeoutException as e:
                logger.error(f"Timeout durante login: {e}")
                take_screenshot(driver, "login_timeout.png")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            take_screenshot(self.browser_manager.get_driver(), "login_error.png")
            return False
    
    def _check_login_status(self) -> bool:
        """Verifica se está logado no Telegram"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Procurar por elementos que indicam login bem-sucedido
            login_indicators = [
                '.chat-list',
                '.sidebar-left',
                '.im-page-chat-list',
                '[data-testid="ChatList"]',
                '.chatlist-container'
            ]
            
            for selector in login_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Login confirmado - encontrado elemento: {selector}")
                        return True
                except:
                    continue
            
            # Verificar se ainda está na página de login
            login_elements = [
                'input[type="tel"]',
                '.login-phone',
                '.auth-form'
            ]
            
            for selector in login_elements:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Ainda na página de login - encontrado: {selector}")
                        return False
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar status de login: {e}")
            return False
    
    def navigate_to_group(self) -> bool:
        """Navega para o grupo de apostas"""
        try:
            if not self.is_logged_in:
                logger.error("Não está logado no Telegram")
                return False
            
            driver = self.browser_manager.get_driver()
            
            # Navegar para o grupo
            logger.info(f"Navegando para grupo: {Config.TELEGRAM_GROUP_URL}")
            driver.get(Config.TELEGRAM_GROUP_URL)
            
            # Aguardar carregamento
            time.sleep(5)
            self.browser_manager.wait_for_page_load()
            
            # Verificar se chegou no grupo
            waiter = ElementWaiter(driver)
            try:
                # Procurar por elementos que indicam que estamos em um chat
                chat_indicators = [
                    '.messages-container',
                    '.chat-container',
                    '.im-page-chat-container',
                    '[data-testid="Messages"]'
                ]
                
                for selector in chat_indicators:
                    try:
                        waiter.wait_for_element(By.CSS_SELECTOR, selector, 10)
                        logger.info(f"Grupo carregado - encontrado: {selector}")
                        return True
                    except TimeoutException:
                        continue
                
                logger.error("Não foi possível confirmar carregamento do grupo")
                take_screenshot(driver, "group_navigation_failed.png")
                return False
                
            except Exception as e:
                logger.error(f"Erro ao verificar carregamento do grupo: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao navegar para grupo: {e}")
            return False
    
    def get_latest_message(self) -> Optional[Dict]:
        """Obtém a última mensagem do grupo"""
        try:
            driver = self.browser_manager.get_driver()
            waiter = ElementWaiter(driver)
            
            # Seletores possíveis para mensagens
            message_selectors = [
                '.message',
                '.im_message_text',
                '[data-testid="Message"]',
                '.chat-message',
                '.message-content'
            ]
            
            messages = []
            for selector in message_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        messages = elements
                        logger.debug(f"Encontradas {len(messages)} mensagens com seletor: {selector}")
                        break
                except:
                    continue
            
            if not messages:
                logger.warning("Nenhuma mensagem encontrada")
                return None
            
            # Pegar a última mensagem
            last_message = messages[-1]
            
            try:
                # Tentar extrair texto da mensagem
                message_text = ""
                text_selectors = [
                    '.message-text',
                    '.text-content',
                    '.im_message_text',
                    'strong',
                    '.message-content'
                ]
                
                for text_selector in text_selectors:
                    try:
                        text_element = last_message.find_element(By.CSS_SELECTOR, text_selector)
                        message_text = text_element.text.strip()
                        if message_text:
                            break
                    except:
                        continue
                
                if not message_text:
                    message_text = last_message.text.strip()
                
                # Tentar extrair link
                link = ""
                try:
                    link_element = last_message.find_element(By.CSS_SELECTOR, 'a[href]')
                    link = link_element.get_attribute('href')
                except:
                    pass
                
                # Criar ID único para a mensagem
                message_id = hash(message_text + str(datetime.now().timestamp()))
                
                message_data = {
                    'id': message_id,
                    'text': message_text,
                    'link': link,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.debug(f"Mensagem extraída: {message_data}")
                return message_data
                
            except Exception as e:
                logger.error(f"Erro ao extrair dados da mensagem: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter última mensagem: {e}")
            return None
    
    def check_for_new_message(self) -> Optional[Dict]:
        """Verifica se há nova mensagem e retorna informações de aposta"""
        try:
            current_message = self.get_latest_message()
            
            if not current_message:
                return None
            
            # Verificar se é uma nova mensagem
            if (self.last_message_id != current_message['id'] and 
                self.last_message_text != current_message['text']):
                
                logger.info("Nova mensagem detectada!")
                logger.info(f"Texto: {current_message['text'][:100]}...")
                
                # Atualizar última mensagem
                self.last_message_id = current_message['id']
                self.last_message_text = current_message['text']
                
                # Extrair informações de aposta
                bet_info = MessageParser.extract_bet_info(current_message['text'])
                
                if bet_info:
                    # Adicionar link se encontrado na mensagem
                    if current_message['link']:
                        bet_info['link'] = current_message['link']
                    
                    bet_info['message_data'] = current_message
                    logger.info(f"Informações de aposta extraídas: {bet_info}")
                    return bet_info
                else:
                    logger.info("Mensagem não contém informações de aposta válidas")
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao verificar nova mensagem: {e}")
            return None
    
    def start_monitoring(self, callback_function):
        """Inicia monitoramento contínuo de mensagens"""
        logger.info("Iniciando monitoramento do Telegram...")
        
        if not self.login():
            logger.error("Falha no login, não é possível monitorar")
            return False
        
        if not self.navigate_to_group():
            logger.error("Falha ao navegar para grupo, não é possível monitorar")
            return False
        
        logger.info(f"Monitoramento iniciado - verificando a cada {Config.CHECK_INTERVAL_SECONDS}s")
        
        while True:
            try:
                bet_info = self.check_for_new_message()
                
                if bet_info:
                    logger.info("Nova aposta detectada, executando callback...")
                    try:
                        callback_function(bet_info)
                    except Exception as e:
                        logger.error(f"Erro no callback: {e}")
                
                time.sleep(Config.CHECK_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro durante monitoramento: {e}")
                time.sleep(Config.CHECK_INTERVAL_SECONDS * 2)  # Aguardar mais em caso de erro
    
    def close(self):
        """Fecha o watcher e limpa recursos"""
        self.browser_manager.close_driver()
        logger.info("Telegram Watcher fechado")
