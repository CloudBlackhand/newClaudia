#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Anti-Captcha para Blacktemplar Bolter
Adaptado do GoogleRecaptchaBypass para usar Playwright ao invés de DrissionPage
Resolve reCAPTCHA v2 usando reconhecimento de áudio
"""

import os
import urllib.request
import random
import time
import tempfile
import requests
from typing import Optional
from playwright.async_api import Page
import speech_recognition as sr
from pydub import AudioSegment
import asyncio
from .logger import logger, security_event

class CaptchaSolver:
    """Resolvedor de reCAPTCHA usando reconhecimento de áudio com Playwright"""
    
    # Constantes
    TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
    TIMEOUT_STANDARD = 7000  # milliseconds for Playwright
    TIMEOUT_SHORT = 1000
    TIMEOUT_DETECTION = 50
    
    def __init__(self, page: Page):
        """Inicializar solver com página Playwright
        
        Args:
            page: Instância da página Playwright
        """
        self.page = page
        self.bypass_available = True
        logger.info("CaptchaSolver inicializado com Playwright")
        
    async def solve_captcha(self) -> bool:
        """Tentar resolver o reCAPTCHA
        
        Returns:
            bool: True se resolvido com sucesso, False caso contrário
        """
        try:
            logger.info("🔐 Iniciando resolução de reCAPTCHA...")
            
            # Aguardar iframe do reCAPTCHA aparecer
            await self.page.wait_for_selector("iframe[title='reCAPTCHA']", timeout=self.TIMEOUT_STANDARD)
            
            # Localizar o iframe principal do reCAPTCHA
            recaptcha_frame = self.page.frame_locator("iframe[title='reCAPTCHA']")
            
            # Aguardar checkbox aparecer e clicar
            await recaptcha_frame.locator(".rc-anchor-content").wait_for(timeout=self.TIMEOUT_STANDARD)
            await recaptcha_frame.locator(".rc-anchor-content").click()
            
            logger.info("✅ Clicou no checkbox do reCAPTCHA")
            
            # Aguardar um pouco para ver se resolve automaticamente
            await asyncio.sleep(2)
            
            # Verificar se foi resolvido apenas com o clique
            if await self.is_solved():
                logger.info("🎉 reCAPTCHA resolvido automaticamente!")
                security_event("captcha_solved_automatically", "low")
                return True
            
            # Se não resolveu automaticamente, tentar desafio de áudio
            logger.info("🎵 Captcha não resolvido automaticamente, tentando áudio...")
            
            # Localizar iframe do desafio
            challenge_frame = self.page.frame_locator("iframe[title*='recaptcha challenge']")
            
            # Clicar no botão de áudio
            await challenge_frame.locator("#recaptcha-audio-button").wait_for(timeout=self.TIMEOUT_STANDARD)
            await challenge_frame.locator("#recaptcha-audio-button").click()
            
            logger.info("🔊 Clicou no botão de áudio")
            await asyncio.sleep(1)
            
            # Verificar se o bot foi detectado
            if await self.is_detected():
                logger.error("🚫 Bot detectado pelo reCAPTCHA")
                security_event("captcha_bot_detected", "high")
                return False
            
            # Aguardar áudio carregar e obter URL
            await challenge_frame.locator("#audio-source").wait_for(timeout=self.TIMEOUT_STANDARD)
            audio_url = await challenge_frame.locator("#audio-source").get_attribute("src")
            
            if not audio_url:
                logger.error("❌ URL do áudio não encontrada")
                return False
                
            logger.info(f"🎵 URL do áudio obtida: {audio_url[:50]}...")
            
            # Processar áudio e obter texto
            text_response = await self._process_audio_challenge(audio_url)
            
            if not text_response:
                logger.error("❌ Falha ao processar áudio")
                return False
                
            logger.info(f"🎯 Texto reconhecido: {text_response}")
            
            # Inserir resposta no campo
            await challenge_frame.locator("#audio-response").fill(text_response.lower())
            await challenge_frame.locator("#recaptcha-verify-button").click()
            
            logger.info("✅ Resposta submetida")
            await asyncio.sleep(2)
            
            # Verificar se foi resolvido
            if await self.is_solved():
                logger.info("🎉 reCAPTCHA resolvido com sucesso via áudio!")
                security_event("captcha_solved_audio", "low", text_length=len(text_response))
                return True
            else:
                logger.error("❌ reCAPTCHA não foi resolvido")
                security_event("captcha_failed", "medium")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao resolver reCAPTCHA: {e}")
            security_event("captcha_error", "medium", error=str(e))
            return False
    
    async def _process_audio_challenge(self, audio_url: str) -> Optional[str]:
        """Processar desafio de áudio e retornar texto reconhecido
        
        Args:
            audio_url: URL do arquivo de áudio
            
        Returns:
            str: Texto reconhecido ou None se falhou
        """
        mp3_path = None
        wav_path = None
        
        try:
            # Gerar nomes únicos para arquivos temporários
            random_id = random.randrange(1, 10000)
            mp3_path = os.path.join(self.TEMP_DIR, f"captcha_audio_{random_id}.mp3")
            wav_path = os.path.join(self.TEMP_DIR, f"captcha_audio_{random_id}.wav")
            
            logger.info("⬇️ Baixando arquivo de áudio...")
            
            # Baixar áudio
            urllib.request.urlretrieve(audio_url, mp3_path)
            
            # Converter MP3 para WAV
            logger.info("🔄 Convertendo áudio para WAV...")
            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")
            
            # Reconhecer fala usando Google Speech Recognition
            logger.info("🎤 Reconhecendo fala no áudio...")
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                # Ajustar para ruído ambiente
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
            
            # Tentar reconhecimento em inglês (reCAPTCHA usa inglês)
            text = recognizer.recognize_google(audio_data, language='en-US')
            
            logger.info(f"✅ Áudio reconhecido com sucesso: '{text}'")
            return text
            
        except sr.UnknownValueError:
            logger.error("❌ Google Speech Recognition não conseguiu entender o áudio")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ Erro no serviço Google Speech Recognition: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao processar áudio: {e}")
            return None
        finally:
            # Limpar arquivos temporários
            for path in (mp3_path, wav_path):
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
    
    async def is_solved(self) -> bool:
        """Verificar se o captcha foi resolvido
        
        Returns:
            bool: True se resolvido, False caso contrário
        """
        try:
            # Procurar pelo checkmark visível que indica sucesso
            recaptcha_frame = self.page.frame_locator("iframe[title='reCAPTCHA']")
            
            # Verificar se o checkbox está marcado
            checkbox = recaptcha_frame.locator(".recaptcha-checkbox-checkmark")
            
            # Se o elemento tem atributo style, significa que está visível (resolvido)
            style_attr = await checkbox.get_attribute("style")
            
            is_solved = style_attr is not None and style_attr != ""
            
            if is_solved:
                logger.info("✅ Captcha verificado como resolvido")
            
            return is_solved
            
        except Exception as e:
            logger.debug(f"Erro ao verificar se captcha foi resolvido: {e}")
            return False
    
    async def is_detected(self) -> bool:
        """Verificar se o bot foi detectado
        
        Returns:
            bool: True se detectado, False caso contrário
        """
        try:
            # Procurar por mensagens de erro que indicam detecção de bot
            challenge_frame = self.page.frame_locator("iframe[title*='recaptcha challenge']")
            
            # Procurar texto "Try again later" que indica detecção
            try_again_element = challenge_frame.locator("text=Try again later")
            
            # Verificar se o elemento está visível
            is_detected = await try_again_element.is_visible()
            
            if is_detected:
                logger.warning("🚫 Bot detectado pelo reCAPTCHA!")
                
            return is_detected
            
        except Exception:
            return False
    
    async def get_token(self) -> Optional[str]:
        """Obter token do reCAPTCHA se disponível
        
        Returns:
            str: Token ou None se não disponível
        """
        try:
            token_element = self.page.locator("#recaptcha-token")
            token = await token_element.get_attribute("value")
            return token
        except Exception:
            return None
    
    def get_bypass_status(self) -> dict:
        """Obter status do sistema de bypass
        
        Returns:
            dict: Status do sistema
        """
        return {
            "bypass_available": self.bypass_available,
            "method": "audio_recognition",
            "dependencies": {
                "speech_recognition": True,
                "pydub": True,
                "playwright": True
            }
        }

# Funções de conveniência
async def solve_recaptcha(page: Page) -> bool:
    """Função de conveniência para resolver reCAPTCHA
    
    Args:
        page: Página Playwright
        
    Returns:
        bool: True se resolvido
    """
    solver = CaptchaSolver(page)
    return await solver.solve_captcha()

def get_captcha_solver_info() -> dict:
    """Obter informações sobre o resolvedor de captcha
    
    Returns:
        dict: Informações do sistema
    """
    return {
        "name": "Blacktemplar Captcha Solver",
        "version": "1.0.0",
        "method": "Audio Recognition",
        "supported_types": ["reCAPTCHA v2"],
        "dependencies": ["speech_recognition", "pydub", "playwright"],
        "free": True
    }