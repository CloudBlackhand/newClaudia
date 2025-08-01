#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente WhatsApp Web.js Integrado
Sistema WhatsApp direto em Python sem dependência Node.js
"""

import asyncio
import logging
import base64
import time
import json
import os
from typing import Optional, Dict, Any, List
import aiohttp
import websockets
from playwright.async_api import async_playwright, Browser, Page
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)

class WhatsAppClient:
    """Cliente WhatsApp Web integrado com Playwright"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_connected = False
        self.session_data = None
        self.qr_code_data = None
        self.message_queue = []
        
    async def initialize(self) -> Optional[str]:
        """Inicializar WhatsApp Web e gerar QR Code"""
        try:
            logger.info("🚀 Inicializando WhatsApp Web...")
            
            # Inicializar Playwright
            self.playwright = await async_playwright().start()
            
            # Configurar navegador stealth
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Headless para testes - QR via base64
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ]
            )
            
            # Configurar contexto stealth
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1366, 'height': 768},
                locale='pt-BR',
                timezone_id='America/Sao_Paulo'
            )
            
            # Stealth mode - mascarar automação
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                window.chrome = {
                    runtime: {}
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            self.page = await context.new_page()
            
            # Carregar sessão se existir
            await self._load_session()
            
            # Acessar WhatsApp Web
            await self.page.goto('https://web.whatsapp.com')
            
            # Aguardar carregar
            await asyncio.sleep(5)
            
            # Verificar se já está logado
            if await self._check_if_logged_in():
                logger.info("✅ Já logado no WhatsApp")
                self.is_connected = True
                return None
            else:
                # Aguardar QR Code aparecer
                qr_code = await self._wait_for_qr_code()
                if qr_code:
                    self.qr_code_data = qr_code
                    logger.info("📱 QR Code gerado, aguardando escaneamento...")
                    
                    # Iniciar monitoramento de login
                    asyncio.create_task(self._monitor_login())
                    
                    return qr_code
                else:
                    raise Exception("Não foi possível obter QR Code")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar WhatsApp: {e}")
            raise
    
    async def _check_if_logged_in(self) -> bool:
        """Verificar se já está logado"""
        try:
            # Aguardar alguns segundos para página carregar
            await asyncio.sleep(3)
            
            # Verificar se existe o elemento de conversas
            try:
                await self.page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                return True
            except:
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar login: {e}")
            return False
    
    async def _wait_for_qr_code(self) -> Optional[str]:
        """Aguardar e capturar QR Code"""
        try:
            # Aguardar QR Code aparecer
            qr_selector = '[data-testid="qr-code"]'
            await self.page.wait_for_selector(qr_selector, timeout=30000)
            
            # Aguardar um pouco para garantir que carregou
            await asyncio.sleep(2)
            
            # Capturar QR Code
            qr_element = await self.page.query_selector(qr_selector)
            if qr_element:
                # Obter atributo data-ref do QR
                qr_data = await qr_element.get_attribute('data-ref')
                
                if qr_data:
                    # Gerar QR Code como base64
                    qr_img = qrcode.make(qr_data)
                    buffer = BytesIO()
                    qr_img.save(buffer, format='PNG')
                    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    return f"data:image/png;base64,{qr_base64}"
                else:
                    # Fallback: screenshot do QR
                    qr_screenshot = await qr_element.screenshot()
                    qr_base64 = base64.b64encode(qr_screenshot).decode()
                    return f"data:image/png;base64,{qr_base64}"
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar QR Code: {e}")
            return None
    
    async def _monitor_login(self):
        """Monitorar login via QR Code"""
        try:
            logger.info("👀 Monitorando login...")
            
            # Aguardar até 2 minutos para login
            for _ in range(120):  # 120 segundos
                if await self._check_if_logged_in():
                    logger.info("✅ Login realizado com sucesso!")
                    self.is_connected = True
                    
                    # Salvar sessão
                    await self._save_session()
                    
                    # Configurar listeners
                    await self._setup_message_listeners()
                    
                    break
                
                await asyncio.sleep(1)
            
            if not self.is_connected:
                logger.warning("⏰ Timeout no login via QR Code")
                
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento de login: {e}")
    
    async def _setup_message_listeners(self):
        """Configurar listeners para mensagens recebidas"""
        try:
            # Injetar código para capturar mensagens
            await self.page.evaluate("""
                window.receivedMessages = [];
                
                // Função para capturar novas mensagens
                function captureMessages() {
                    const messages = document.querySelectorAll('[data-testid="conversation-panel-messages"] [data-testid="msg-container"]');
                    
                    messages.forEach(msg => {
                        const isIncoming = !msg.querySelector('[data-testid="msg-meta-status"]');
                        if (isIncoming) {
                            const textElement = msg.querySelector('span.selectable-text span');
                            const text = textElement ? textElement.innerText : '';
                            
                            if (text && !window.processedMessages?.includes(text)) {
                                window.receivedMessages.push({
                                    text: text,
                                    timestamp: Date.now(),
                                    processed: false
                                });
                                
                                if (!window.processedMessages) window.processedMessages = [];
                                window.processedMessages.push(text);
                            }
                        }
                    });
                }
                
                // Monitorar mudanças
                const observer = new MutationObserver(captureMessages);
                observer.observe(document.body, { childList: true, subtree: true });
                
                setInterval(captureMessages, 1000);
            """)
            
            logger.info("✅ Listeners de mensagem configurados")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar listeners: {e}")
    
    async def send_message(self, phone: str, message: str, attachment: Optional[str] = None) -> bool:
        """Enviar mensagem com simulação humana"""
        try:
            if not self.is_connected:
                logger.error("❌ WhatsApp não conectado")
                return False
            
            logger.info(f"📤 Enviando mensagem para {phone}")
            
            # Formatar número
            formatted_phone = self._format_phone(phone)
            
            # Abrir conversa
            chat_url = f"https://web.whatsapp.com/send?phone={formatted_phone}"
            await self.page.goto(chat_url)
            
            # Aguardar conversa carregar
            await asyncio.sleep(3)
            
            # Verificar se conversa abriu
            try:
                await self.page.wait_for_selector('[data-testid="conversation-panel-body"]', timeout=10000)
            except:
                logger.error(f"❌ Não foi possível abrir conversa com {phone}")
                return False
            
            # Enviar anexo se fornecido
            if attachment and os.path.exists(attachment):
                await self._send_attachment(attachment)
                await asyncio.sleep(2)
            
            # Localizar campo de mensagem
            message_input = await self.page.wait_for_selector('[data-testid="message-composer-input"]')
            
            # Simular digitação humana
            await self._type_human_like(message_input, message)
            
            # Aguardar um pouco antes de enviar
            await asyncio.sleep(1)
            
            # Enviar mensagem
            await self.page.keyboard.press('Enter')
            
            # Aguardar confirmação
            await asyncio.sleep(2)
            
            logger.info(f"✅ Mensagem enviada para {phone}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem para {phone}: {e}")
            return False
    
    async def _send_attachment(self, file_path: str):
        """Enviar anexo"""
        try:
            # Clicar no botão de anexo
            attach_button = await self.page.wait_for_selector('[data-testid="clip"]')
            await attach_button.click()
            
            await asyncio.sleep(1)
            
            # Clicar em documento
            doc_button = await self.page.wait_for_selector('[data-testid="attach-document"]')
            await doc_button.click()
            
            # Upload do arquivo
            file_input = await self.page.wait_for_selector('input[type="file"]')
            await file_input.set_input_files(file_path)
            
            await asyncio.sleep(2)
            
            # Enviar anexo
            send_button = await self.page.wait_for_selector('[data-testid="send-button"]')
            await send_button.click()
            
            logger.info(f"✅ Anexo enviado: {os.path.basename(file_path)}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar anexo: {e}")
    
    async def _type_human_like(self, element, text: str):
        """Simular digitação humana"""
        # Limpar campo primeiro
        await element.click()
        await self.page.keyboard.press('Control+A')
        await self.page.keyboard.press('Delete')
        
        # Digitar com variação de velocidade
        for char in text:
            await element.type(char)
            # Variação aleatória na velocidade
            delay = 0.05 + (hash(char) % 100) / 2000  # 0.05-0.10s por caractere
            await asyncio.sleep(delay)
            
            # Pausas ocasionais (simular pensamento)
            if char in '.!?' and len(text) > 20:
                await asyncio.sleep(0.5)
    
    async def get_qr_code(self) -> Optional[str]:
        """Obter QR Code atual"""
        if not self.is_connected and self.qr_code_data:
            # Tentar capturar QR atualizado
            try:
                new_qr = await self._wait_for_qr_code()
                if new_qr:
                    self.qr_code_data = new_qr
                return self.qr_code_data
            except:
                return self.qr_code_data
        return None
    
    async def get_received_messages(self) -> List[Dict[str, Any]]:
        """Obter mensagens recebidas"""
        try:
            if not self.is_connected:
                return []
            
            messages = await self.page.evaluate("""
                () => {
                    const unprocessed = window.receivedMessages?.filter(msg => !msg.processed) || [];
                    
                    // Marcar como processadas
                    if (window.receivedMessages) {
                        window.receivedMessages.forEach(msg => msg.processed = true);
                    }
                    
                    return unprocessed;
                }
            """)
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter mensagens: {e}")
            return []
    
    def _format_phone(self, phone: str) -> str:
        """Formatar número de telefone"""
        # Remover caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se necessário
        if not clean_phone.startswith('55'):
            clean_phone = '55' + clean_phone
        
        return clean_phone
    
    async def _save_session(self):
        """Salvar dados da sessão"""
        try:
            # Obter cookies e localStorage
            cookies = await self.page.context.cookies()
            local_storage = await self.page.evaluate('() => ({ ...localStorage })')
            
            session_data = {
                'cookies': cookies,
                'local_storage': local_storage,
                'timestamp': time.time()
            }
            
            # Salvar em arquivo
            os.makedirs('sessions', exist_ok=True)
            with open('sessions/whatsapp_session.json', 'w') as f:
                json.dump(session_data, f)
            
            logger.info("💾 Sessão salva")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar sessão: {e}")
    
    async def _load_session(self):
        """Carregar sessão salva"""
        try:
            session_file = 'sessions/whatsapp_session.json'
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Verificar se sessão não está muito antiga (7 dias)
                if time.time() - session_data.get('timestamp', 0) < 7 * 24 * 3600:
                    # Restaurar cookies
                    await self.page.context.add_cookies(session_data['cookies'])
                    
                    # Restaurar localStorage
                    await self.page.evaluate(f"""
                        () => {{
                            const data = {json.dumps(session_data['local_storage'])};
                            for (const [key, value] of Object.entries(data)) {{
                                localStorage.setItem(key, value);
                            }}
                        }}
                    """)
                    
                    logger.info("📂 Sessão carregada")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Erro ao carregar sessão: {e}")
        
        return False
    
    async def close(self):
        """Fechar cliente"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("🔒 Cliente WhatsApp fechado")
        except Exception as e:
            logger.error(f"❌ Erro ao fechar cliente: {e}") 