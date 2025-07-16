
import time
import re
from typing import Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger

from browser_manager import BrowserManager
from utils import SessionManager, ElementWaiter, human_like_delay, take_screenshot, validate_bet_amount, RetryHelper
from config import Config

class BetExecutor:
    """Classe para executar apostas automaticamente"""
    
    def __init__(self):
        self.browser_manager = BrowserManager("betting_profile")
        self.session_manager = SessionManager("betting_session.json")
        self.is_logged_in = False
        self.bet_site_domain = self._extract_domain(Config.BET_SITE_BASE_URL)
    
    def _extract_domain(self, url: str) -> str:
        """Extrai domínio da URL"""
        try:
            # Remove protocolo e pega apenas o domínio
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            return domain
        except:
            return url
    
    def login(self) -> bool:
        """Realiza login no site de apostas"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Tentar carregar sessão existente
            if self.session_manager.load_cookies(driver, self.bet_site_domain):
                logger.info("Tentando usar sessão salva do site de apostas...")
                driver.get(Config.BET_SITE_BASE_URL)
                
                # Aguardar carregamento
                time.sleep(5)
                self.browser_manager.wait_for_page_load()
                
                if self._check_login_status():
                    logger.info("Login realizado com sessão salva")
                    self.is_logged_in = True
                    return True
            
            # Se não conseguiu com sessão salva, fazer login manual
            logger.info("Realizando login manual no site de apostas...")
            
            # Navegar para página de login
            login_url = f"{Config.BET_SITE_BASE_URL}/login"
            if not self.browser_manager.navigate_with_retry(login_url):
                logger.error("Falha ao navegar para página de login")
                return False
            
            # Lidar com Cloudflare se necessário
            if not self.browser_manager.handle_cloudflare():
                logger.error("Falha ao resolver Cloudflare")
                return False
            
            waiter = ElementWaiter(driver)
            
            # Procurar campos de login
            username_selectors = [
                'input[name="username"]',
                'input[name="email"]',
                'input[name="login"]',
                'input[type="email"]',
                'input[id*="user"]',
                'input[id*="email"]',
                'input[placeholder*="usuário"]',
                'input[placeholder*="email"]'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[id*="pass"]',
                'input[placeholder*="senha"]'
            ]
            
            # Encontrar campo de usuário
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = waiter.wait_for_element(By.CSS_SELECTOR, selector, 5)
                    logger.info(f"Campo de usuário encontrado: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                logger.error("Campo de usuário não encontrado")
                take_screenshot(driver, "login_username_not_found.png")
                return False
            
            # Encontrar campo de senha
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Campo de senha encontrado: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.error("Campo de senha não encontrado")
                take_screenshot(driver, "login_password_not_found.png")
                return False
            
            # Preencher credenciais
            username_field.clear()
            username_field.send_keys(Config.BET_SITE_USERNAME)
            human_like_delay(0.5, 1.5)
            
            password_field.clear()
            password_field.send_keys(Config.BET_SITE_PASSWORD)
            human_like_delay(0.5, 1.5)
            
            # Procurar botão de login
            login_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[id*="login"]',
                'button[class*="login"]',
                '.btn-login',
                '.login-btn',
                'button:contains("Entrar")',
                'button:contains("Login")'
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Botão de login encontrado: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                # Tentar enviar Enter no campo de senha
                logger.info("Botão de login não encontrado, tentando Enter")
                password_field.send_keys(Keys.RETURN)
            else:
                login_button.click()
            
            # Aguardar login
            time.sleep(5)
            self.browser_manager.wait_for_page_load()
            
            # Verificar se login foi bem-sucedido
            if self._check_login_status():
                logger.info("Login realizado com sucesso")
                self.session_manager.save_cookies(driver)
                self.is_logged_in = True
                return True
            else:
                logger.error("Falha no login - não foi possível confirmar")
                take_screenshot(driver, "login_failed.png")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            take_screenshot(self.browser_manager.get_driver(), "login_error.png")
            return False
    
    def _check_login_status(self) -> bool:
        """Verifica se está logado no site de apostas"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Indicadores de login bem-sucedido
            logged_in_indicators = [
                '.user-menu',
                '.account-menu',
                '.profile-menu',
                '.logout',
                '.sair',
                '[data-testid="user-menu"]',
                '.user-info',
                '.balance',
                '.saldo'
            ]
            
            for selector in logged_in_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Login confirmado - encontrado: {selector}")
                        return True
                except:
                    continue
            
            # Verificar se ainda está na página de login
            login_indicators = [
                'input[name="username"]',
                'input[name="password"]',
                '.login-form',
                '.auth-form'
            ]
            
            for selector in login_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Ainda na página de login - encontrado: {selector}")
                        return False
                except:
                    continue
            
            # Se não encontrou indicadores claros, assumir que está logado
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar status de login: {e}")
            return False
    
    def execute_bet(self, bet_info: Dict) -> bool:
        """Executa uma aposta baseada nas informações fornecidas"""
        try:
            if not self.is_logged_in:
                logger.error("Não está logado no site de apostas")
                if not self.login():
                    return False
            
            driver = self.browser_manager.get_driver()
            
            # Verificar se há link na aposta
            if 'link' not in bet_info or not bet_info['link']:
                logger.error("Link da aposta não encontrado")
                return False
            
            bet_link = bet_info['link']
            bet_amount = bet_info.get('valor_numerico', Config.DEFAULT_BET_AMOUNT)
            
            # Validar valor da aposta
            bet_amount = validate_bet_amount(bet_amount, Config.MIN_BET_AMOUNT, Config.MAX_BET_AMOUNT)
            
            logger.info(f"Executando aposta - Link: {bet_link}, Valor: R$ {bet_amount}")
            
            # Navegar para o link da aposta
            if not self.browser_manager.navigate_with_retry(bet_link):
                logger.error("Falha ao navegar para link da aposta")
                return False
            
            # Aguardar página carregar
            self.browser_manager.wait_for_page_load()
            
            # Lidar com Cloudflare se necessário
            if not self.browser_manager.handle_cloudflare():
                logger.error("Falha ao resolver Cloudflare na página da aposta")
                return False
            
            # Procurar campo de valor da aposta
            if not self._fill_bet_amount(bet_amount):
                logger.error("Falha ao preencher valor da aposta")
                return False
            
            # Confirmar aposta
            if not self._confirm_bet():
                logger.error("Falha ao confirmar aposta")
                return False
            
            logger.info("Aposta executada com sucesso!")
            take_screenshot(driver, f"bet_success_{int(time.time())}.png")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar aposta: {e}")
            take_screenshot(self.browser_manager.get_driver(), f"bet_error_{int(time.time())}.png")
            return False
    
    def _fill_bet_amount(self, amount: float) -> bool:
        """Preenche o valor da aposta"""
        try:
            driver = self.browser_manager.get_driver()
            waiter = ElementWaiter(driver)
            
            # Seletores possíveis para campo de valor
            amount_selectors = [
                'input[name*="stake"]',
                'input[name*="amount"]',
                'input[name*="valor"]',
                'input[id*="stake"]',
                'input[id*="amount"]',
                'input[id*="valor"]',
                'input[placeholder*="valor"]',
                'input[placeholder*="stake"]',
                'input[class*="stake"]',
                'input[class*="amount"]',
                '.bet-amount input',
                '.stake-input',
                '.amount-input'
            ]
            
            amount_field = None
            for selector in amount_selectors:
                try:
                    amount_field = waiter.wait_for_element(By.CSS_SELECTOR, selector, 5)
                    logger.info(f"Campo de valor encontrado: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not amount_field:
                logger.error("Campo de valor da aposta não encontrado")
                take_screenshot(driver, "amount_field_not_found.png")
                return False
            
            # Limpar campo e inserir valor
            amount_field.clear()
            human_like_delay(0.3, 0.7)
            
            # Converter para string com formato brasileiro
            amount_str = f"{amount:.2f}".replace('.', ',')
            amount_field.send_keys(amount_str)
            human_like_delay(0.5, 1.0)
            
            logger.info(f"Valor R$ {amount} inserido no campo")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao preencher valor da aposta: {e}")
            return False
    
    def _confirm_bet(self) -> bool:
        """Confirma a aposta"""
        try:
            driver = self.browser_manager.get_driver()
            waiter = ElementWaiter(driver)
            
            # Seletores possíveis para botão de confirmar
            confirm_selectors = [
                'button[id*="confirm"]',
                'button[class*="confirm"]',
                'button[id*="place"]',
                'button[class*="place"]',
                '.btn-confirm',
                '.confirm-bet',
                '.place-bet',
                'button:contains("Confirmar")',
                'button:contains("Apostar")',
                'button:contains("Place Bet")',
                'input[type="submit"][value*="Confirmar"]',
                'input[type="submit"][value*="Apostar"]'
            ]
            
            confirm_button = None
            for selector in confirm_selectors:
                try:
                    confirm_button = waiter.wait_for_clickable(By.CSS_SELECTOR, selector, 5)
                    logger.info(f"Botão de confirmar encontrado: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not confirm_button:
                logger.error("Botão de confirmar aposta não encontrado")
                take_screenshot(driver, "confirm_button_not_found.png")
                return False
            
            # Clicar no botão de confirmar
            confirm_button.click()
            human_like_delay(1.0, 2.0)
            
            # Aguardar confirmação
            self.browser_manager.wait_for_page_load()
            
            # Verificar se aposta foi confirmada
            success_indicators = [
                '.bet-success',
                '.success-message',
                '.confirmation',
                'text*="sucesso"',
                'text*="confirmada"',
                'text*="success"'
            ]
            
            for selector in success_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Confirmação de sucesso encontrada: {selector}")
                        return True
                except:
                    continue
            
            # Se não encontrou indicadores específicos, assumir sucesso se não há erros
            error_indicators = [
                '.error',
                '.alert-danger',
                '.bet-error',
                'text*="erro"',
                'text*="error"',
                'text*="falha"'
            ]
            
            for selector in error_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.error(f"Erro encontrado: {elements[0].text}")
                        return False
                except:
                    continue
            
            logger.info("Aposta aparentemente confirmada (sem indicadores de erro)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao confirmar aposta: {e}")
            return False
    
    def close(self):
        """Fecha o executor e limpa recursos"""
        self.browser_manager.close_driver()
        logger.info("Bet Executor fechado")
