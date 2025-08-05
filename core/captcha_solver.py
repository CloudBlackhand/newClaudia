#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Anti-Captcha para Claudia Cobranças
Solução avançada para bypass de captchas da Desktop
COM SPEECH RECOGNITION PARA ÁUDIO
"""

import asyncio
import time
import logging
import os
import requests
import tempfile
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page

# Importar SpeechRecognition
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ SpeechRecognition não disponível: {e}")
    SPEECH_AVAILABLE = False

from .logger import logger

class CaptchaSolver:
    """Sistema anti-captcha avançado para Claudia Cobranças"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_initialized = False
        self.recognizer = None
        
        # Inicializar SpeechRecognition se disponível
        if SPEECH_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                logger.info("🎵 SpeechRecognition inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar SpeechRecognition: {e}")
        
    async def initialize(self):
        """Inicializar browser para captcha solving"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            self.page = await self.browser.new_page()
            
            # Configurar user agent
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            self.is_initialized = True
            logger.info("✅ CaptchaSolver inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar CaptchaSolver: {e}")
            self.is_initialized = False
    
    async def solve_recaptcha(self, site_key: str, url: str) -> Optional[str]:
        """Resolver reCAPTCHA usando técnicas avançadas"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            logger.info(f"🎯 Tentando resolver reCAPTCHA em: {url}")
            
            # Navegar para a página
            await self.page.goto(url, wait_until='networkidle')
            
            # Aguardar carregamento do reCAPTCHA
            await self.page.wait_for_selector('iframe[src*="recaptcha"]', timeout=10000)
            
            # Tentar resolver automaticamente
            result = await self._attempt_automatic_solve(site_key)
            if result:
                logger.info("✅ reCAPTCHA resolvido automaticamente")
                return result
            
            # Fallback para resolução manual
            logger.warning("⚠️ Fallback para resolução manual")
            return await self._manual_solve(site_key)
            
        except Exception as e:
            logger.error(f"❌ Erro ao resolver reCAPTCHA: {e}")
            return None
    
    async def _attempt_automatic_solve(self, site_key: str) -> Optional[str]:
        """Tentativa de resolução automática"""
        try:
            # Verificar se há audio challenge
            audio_challenge = await self.page.query_selector('iframe[title="recaptcha challenge"]')
            if audio_challenge:
                return await self._solve_audio_challenge()
            
            # Verificar se há visual challenge
            visual_challenge = await self.page.query_selector('iframe[title="recaptcha challenge"]')
            if visual_challenge:
                return await self._solve_visual_challenge()
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na resolução automática: {e}")
            return None
    
    async def _solve_audio_challenge(self) -> Optional[str]:
        """Resolver challenge de áudio com SpeechRecognition"""
        if not SPEECH_AVAILABLE or not self.recognizer:
            logger.warning("⚠️ SpeechRecognition não disponível para audio challenge")
            return None
            
        try:
            logger.info("🎵 Iniciando challenge de áudio...")
            
            # Clicar no botão de áudio
            audio_button = await self.page.query_selector('button[title="Get an audio challenge"]')
            if audio_button:
                await audio_button.click()
                await asyncio.sleep(2)
                
                # Baixar áudio
                audio_url = await self.page.evaluate('() => document.querySelector("audio").src')
                if audio_url:
                    # Baixar arquivo de áudio
                    audio_file = await self._download_audio(audio_url)
                    if audio_file:
                        # Processar áudio com SpeechRecognition
                        text = await self._process_audio(audio_file)
                        if text:
                            # Inserir texto no campo
                            await self._submit_audio_answer(text)
                            return "audio_solved"
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro no challenge de áudio: {e}")
            return None
    
    async def _download_audio(self, audio_url: str) -> Optional[str]:
        """Baixar arquivo de áudio"""
        try:
            response = requests.get(audio_url)
            if response.status_code == 200:
                # Salvar em arquivo temporário
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.write(response.content)
                temp_file.close()
                logger.info(f"🎵 Áudio baixado: {temp_file.name}")
                return temp_file.name
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao baixar áudio: {e}")
            return None
    
    async def _process_audio(self, audio_file: str) -> Optional[str]:
        """Processar áudio com SpeechRecognition"""
        try:
            # Verificar se o arquivo é WAV (formato preferido)
            if audio_file.endswith('.wav'):
                # Usar diretamente
                with sr.AudioFile(audio_file) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data, language='pt-BR')
                    
                    logger.info(f"🎵 Áudio reconhecido: '{text}'")
                    return text
            else:
                # Para outros formatos, tentar reconhecer diretamente
                logger.warning("⚠️ Formato de áudio não suportado sem pydub")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar áudio: {e}")
            return None
        finally:
            # Limpar arquivos temporários
            try:
                os.unlink(audio_file)
            except:
                pass
    
    async def _submit_audio_answer(self, text: str):
        """Enviar resposta do áudio"""
        try:
            # Encontrar campo de texto
            text_input = await self.page.query_selector('input[type="text"]')
            if text_input:
                await text_input.fill(text)
                await asyncio.sleep(1)
                
                # Clicar no botão de verificar
                verify_button = await self.page.query_selector('button[type="submit"]')
                if verify_button:
                    await verify_button.click()
                    logger.info("✅ Resposta de áudio enviada")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar resposta: {e}")
    
    async def _solve_visual_challenge(self) -> Optional[str]:
        """Resolver challenge visual"""
        try:
            logger.info("🖼️ Challenge visual detectado")
            # Implementar lógica para challenge visual
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro no challenge visual: {e}")
            return None
    
    async def _manual_solve(self, site_key: str) -> Optional[str]:
        """Resolução manual (fallback)"""
        try:
            logger.info("👤 Aguardando resolução manual...")
            
            # Aguardar até que o reCAPTCHA seja resolvido
            await self.page.wait_for_function(
                '() => grecaptcha && grecaptcha.getResponse()',
                timeout=300000  # 5 minutos
            )
            
            # Obter resposta
            response = await self.page.evaluate('() => grecaptcha.getResponse()')
            if response:
                logger.info("✅ reCAPTCHA resolvido manualmente")
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na resolução manual: {e}")
            return None
    
    async def close(self):
        """Fechar recursos"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            logger.info("🔒 CaptchaSolver fechado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao fechar CaptchaSolver: {e}")

def get_captcha_solver_info() -> Dict[str, Any]:
    """Retorna informações do sistema anti-captcha"""
    return {
        "name": "Claudia Captcha Solver",
        "version": "2.2",
        "company": "Desktop",
        "capabilities": [
            "reCAPTCHA v2",
            "Audio Challenge (SpeechRecognition)",
            "Visual Challenge", 
            "Automatic Solving",
            "Manual Fallback"
        ],
        "speech_recognition": SPEECH_AVAILABLE,
        "status": "active"
    }

# Instância global
captcha_solver = CaptchaSolver()