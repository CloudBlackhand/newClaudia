#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 WEB AUTOMATION ENGINE - INSPIRADO NO WAHA
=====================================

Sistema de automação web headless para cobrança
Baseado na arquitetura do WAHA WhatsApp HTTP API

Funcionalidades:
- Chrome headless no Railway Ubuntu
- Login automatizado em sites
- Captura de dados de cobrança
- Integração com sistema de cobrança
- Anti-detecção de bot
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import aiofiles
from pyppeteer import launch
from pyppeteer.page import Page
from pyppeteer.browser import Browser


# ===== CONFIGURAÇÃO DE LOGGING =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===== ENUMS =====
class AutomationStatus(Enum):
    """Status da automação"""
    IDLE = "idle"
    CONNECTING = "connecting"
    LOGGED_IN = "logged_in"
    SCRAPING = "scraping"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class SiteType(Enum):
    """Tipos de sites suportados"""
    SERASA = "serasa"
    SPC = "spc"
    BANCO_CENTRAL = "banco_central"
    CARTORIO = "cartorio"
    CUSTOM = "custom"


# ===== DATACLASSES =====
@dataclass
class BrowserConfig:
    """Configuração do navegador"""
    headless: bool = True
    disable_images: bool = True
    disable_javascript: bool = False
    user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    viewport: Dict[str, int] = None
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1366, "height": 768}


@dataclass
class LoginCredentials:
    """Credenciais de login"""
    username: str
    password: str
    site_type: SiteType
    login_url: str
    username_selector: str
    password_selector: str
    submit_selector: str
    success_indicator: str


@dataclass
class ScrapingTask:
    """Tarefa de scraping"""
    task_id: str
    site_type: SiteType
    target_url: str
    data_selectors: Dict[str, str]
    search_params: Dict[str, Any]
    expected_data: List[str]


@dataclass
class AutomationResult:
    """Resultado da automação"""
    success: bool
    data: Dict[str, Any]
    screenshots: List[str]
    errors: List[str]
    execution_time: float
    timestamp: datetime


# ===== MAIN CLASS =====
class WebAutomationEngine:
    """
    🌐 ENGINE DE AUTOMAÇÃO WEB HEADLESS
    
    Inspirado no WAHA para automação de sites de cobrança
    """
    
    def __init__(self, config: BrowserConfig = None):
        """Inicializa o engine de automação"""
        self.config = config or BrowserConfig()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.status = AutomationStatus.IDLE
        self.sessions: Dict[str, Dict] = {}
        
        # Configurações específicas para Railway/Ubuntu
        self.railway_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-gpu'
        ]
        
        logger.info("🌐 Web Automation Engine inicializado!")
    
    async def start_browser(self) -> bool:
        """
        🚀 Inicia o navegador Chrome headless
        Configurado para funcionar no Railway Ubuntu
        """
        try:
            self.status = AutomationStatus.CONNECTING
            logger.info("🚀 Iniciando Chrome headless...")
            
            # Configurações otimizadas para Railway
            launch_options = {
                'headless': self.config.headless,
                'args': self.railway_args,
                'ignoreHTTPSErrors': True,
                'autoClose': False,
                'dumpio': True
            }
            
            # Detectar se está no Railway
            if os.getenv('RAILWAY_ENVIRONMENT'):
                launch_options['executablePath'] = '/usr/bin/google-chrome-stable'
                logger.info("🚂 Detectado ambiente Railway - usando Chrome otimizado")
            
            self.browser = await launch(**launch_options)
            self.page = await self.browser.newPage()
            
            # Configurar página
            await self._configure_page()
            
            self.status = AutomationStatus.IDLE
            logger.info("✅ Chrome headless iniciado com sucesso!")
            return True
            
        except Exception as e:
            self.status = AutomationStatus.ERROR
            logger.error(f"❌ Erro ao iniciar Chrome: {e}")
            return False
    
    async def _configure_page(self):
        """⚙️ Configura a página com anti-detecção"""
        try:
            # User Agent
            await self.page.setUserAgent(self.config.user_agent)
            
            # Viewport
            await self.page.setViewport(self.config.viewport)
            
            # Desabilitar imagens se configurado
            if self.config.disable_images:
                await self.page.setRequestInterception(True)
                self.page.on('request', self._block_resources)
            
            # Anti-detecção: remover webdriver properties
            await self.page.evaluateOnNewDocument("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Remove chrome detection
                window.chrome = {
                    runtime: {},
                };
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en'],
                });
            """)
            
            logger.info("⚙️ Página configurada com anti-detecção")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar página: {e}")
    
    async def _block_resources(self, request):
        """🚫 Bloqueia recursos desnecessários"""
        resource_type = request.resourceType
        if resource_type in ['image', 'stylesheet', 'font']:
            await request.abort()
        else:
            await request.continue_()
    
    async def login_to_site(self, credentials: LoginCredentials, session_id: str = "default") -> bool:
        """
        🔐 Faz login automatizado em site específico
        Inspirado no processo de login do WAHA
        """
        try:
            if not self.browser or not self.page:
                await self.start_browser()
            
            logger.info(f"🔐 Fazendo login em {credentials.site_type.value}...")
            
            # Navegar para página de login
            await self.page.goto(credentials.login_url, {'waitUntil': 'networkidle2'})
            
            # Screenshot inicial
            screenshot_path = f"temp/login_start_{session_id}_{int(time.time())}.png"
            await self.page.screenshot({'path': screenshot_path})
            
            # Aguardar elementos carregarem
            await self.page.waitForSelector(credentials.username_selector, {'timeout': 10000})
            
            # Inserir credenciais
            await self.page.type(credentials.username_selector, credentials.username)
            await asyncio.sleep(1)  # Simular digitação humana
            
            await self.page.type(credentials.password_selector, credentials.password)
            await asyncio.sleep(1)
            
            # Screenshot antes do submit
            screenshot_before = f"temp/login_before_{session_id}_{int(time.time())}.png"
            await self.page.screenshot({'path': screenshot_before})
            
            # Fazer login
            await self.page.click(credentials.submit_selector)
            
            # Aguardar redirecionamento
            await self.page.waitForNavigation({'timeout': 15000})
            
            # Verificar se login foi bem-sucedido
            success = await self._verify_login_success(credentials.success_indicator)
            
            if success:
                self.status = AutomationStatus.LOGGED_IN
                self.sessions[session_id] = {
                    'site_type': credentials.site_type,
                    'login_time': datetime.now(),
                    'status': 'active'
                }
                logger.info(f"✅ Login realizado com sucesso em {credentials.site_type.value}!")
                
                # Screenshot de sucesso
                screenshot_success = f"temp/login_success_{session_id}_{int(time.time())}.png"
                await self.page.screenshot({'path': screenshot_success})
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            return False
    
    async def _verify_login_success(self, success_indicator: str) -> bool:
        """✅ Verifica se o login foi bem-sucedido"""
        try:
            # Aguardar elemento que indica sucesso
            await self.page.waitForSelector(success_indicator, {'timeout': 10000})
            return True
        except:
            # Se não encontrou o indicador, verificar URL ou título
            current_url = self.page.url
            page_title = await self.page.title()
            
            # Indicadores comuns de erro
            error_indicators = ['erro', 'error', 'invalid', 'incorreto', 'login']
            
            if any(indicator in current_url.lower() or indicator in page_title.lower() 
                   for indicator in error_indicators):
                return False
            
            return True
    
    async def scrape_data(self, task: ScrapingTask) -> AutomationResult:
        """
        📊 Realiza scraping de dados específicos
        """
        start_time = time.time()
        result = AutomationResult(
            success=False,
            data={},
            screenshots=[],
            errors=[],
            execution_time=0,
            timestamp=datetime.now()
        )
        
        try:
            if not self.browser or not self.page:
                result.errors.append("Navegador não inicializado")
                return result
            
            logger.info(f"📊 Iniciando scraping: {task.task_id}")
            self.status = AutomationStatus.SCRAPING
            
            # Navegar para URL alvo
            await self.page.goto(task.target_url, {'waitUntil': 'networkidle2'})
            
            # Screenshot inicial
            screenshot_path = f"temp/scraping_{task.task_id}_{int(time.time())}.png"
            await self.page.screenshot({'path': screenshot_path})
            result.screenshots.append(screenshot_path)
            
            # Realizar busca se necessário
            if task.search_params:
                await self._perform_search(task.search_params)
                await asyncio.sleep(2)
            
            # Extrair dados usando seletores
            extracted_data = {}
            for data_key, selector in task.data_selectors.items():
                try:
                    element = await self.page.querySelector(selector)
                    if element:
                        if data_key.endswith('_text'):
                            value = await self.page.evaluate('(element) => element.textContent', element)
                        elif data_key.endswith('_value'):
                            value = await self.page.evaluate('(element) => element.value', element)
                        elif data_key.endswith('_href'):
                            value = await self.page.evaluate('(element) => element.href', element)
                        else:
                            value = await self.page.evaluate('(element) => element.textContent', element)
                        
                        extracted_data[data_key] = value.strip() if value else None
                    else:
                        extracted_data[data_key] = None
                        
                except Exception as e:
                    result.errors.append(f"Erro ao extrair {data_key}: {e}")
                    extracted_data[data_key] = None
            
            result.data = extracted_data
            result.success = len([v for v in extracted_data.values() if v is not None]) > 0
            
            # Screenshot final
            final_screenshot = f"temp/scraping_final_{task.task_id}_{int(time.time())}.png"
            await self.page.screenshot({'path': final_screenshot})
            result.screenshots.append(final_screenshot)
            
            logger.info(f"✅ Scraping concluído: {task.task_id}")
            
        except Exception as e:
            result.errors.append(f"Erro no scraping: {e}")
            logger.error(f"❌ Erro no scraping: {e}")
        
        finally:
            result.execution_time = time.time() - start_time
            self.status = AutomationStatus.IDLE
        
        return result
    
    async def _perform_search(self, search_params: Dict[str, Any]):
        """🔍 Realiza busca no site"""
        for field, value in search_params.items():
            try:
                selector = f"input[name='{field}'], input[id='{field}'], #{field}"
                await self.page.waitForSelector(selector, {'timeout': 5000})
                await self.page.type(selector, str(value))
                await asyncio.sleep(0.5)
            except:
                logger.warning(f"⚠️ Campo de busca não encontrado: {field}")
    
    async def get_screenshot(self, filename: str = None) -> str:
        """📸 Captura screenshot da página atual"""
        try:
            if not self.page:
                return None
            
            if not filename:
                filename = f"temp/screenshot_{int(time.time())}.png"
            
            await self.page.screenshot({'path': filename})
            logger.info(f"📸 Screenshot salvo: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar screenshot: {e}")
            return None
    
    async def close_browser(self):
        """🔚 Fecha o navegador"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.page = None
                self.status = AutomationStatus.DISCONNECTED
                logger.info("🔚 Navegador fechado")
        except Exception as e:
            logger.error(f"❌ Erro ao fechar navegador: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """📊 Retorna status atual do engine"""
        return {
            'status': self.status.value,
            'browser_active': self.browser is not None,
            'page_active': self.page is not None,
            'sessions': len(self.sessions),
            'active_sessions': [s for s in self.sessions.values() if s['status'] == 'active']
        }


# ===== FACTORY FUNCTIONS =====
def create_serasa_credentials(username: str, password: str) -> LoginCredentials:
    """🏦 Cria credenciais para Serasa"""
    return LoginCredentials(
        username=username,
        password=password,
        site_type=SiteType.SERASA,
        login_url="https://www.serasa.com.br/login",
        username_selector="input[name='username'], #username, .username",
        password_selector="input[name='password'], #password, .password",
        submit_selector="button[type='submit'], .btn-login, #login-button",
        success_indicator=".dashboard, .home, .loggedin"
    )


def create_spc_credentials(username: str, password: str) -> LoginCredentials:
    """🏛️ Cria credenciais para SPC"""
    return LoginCredentials(
        username=username,
        password=password,
        site_type=SiteType.SPC,
        login_url="https://www.spcbrasil.org.br/login",
        username_selector="input[name='login'], #login",
        password_selector="input[name='senha'], #senha",
        submit_selector="button[type='submit'], .btn-entrar",
        success_indicator=".area-cliente, .dashboard"
    )


# ===== TESTE =====
async def test_automation():
    """🧪 Teste básico do engine"""
    engine = WebAutomationEngine()
    
    try:
        # Iniciar navegador
        success = await engine.start_browser()
        if not success:
            print("❌ Falha ao iniciar navegador")
            return
        
        print("✅ Navegador iniciado!")
        print(f"📊 Status: {engine.get_status()}")
        
        # Navegar para uma página de teste
        await engine.page.goto('https://httpbin.org/user-agent')
        await asyncio.sleep(2)
        
        # Capturar screenshot
        screenshot = await engine.get_screenshot()
        print(f"📸 Screenshot: {screenshot}")
        
        # Obter conteúdo da página
        content = await engine.page.content()
        print(f"📄 Página carregada: {len(content)} caracteres")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    finally:
        await engine.close_browser()


if __name__ == "__main__":
    print("🌐 WEB AUTOMATION ENGINE - INSPIRADO NO WAHA")
    print("=" * 50)
    
    # Executar teste
    asyncio.run(test_automation())
