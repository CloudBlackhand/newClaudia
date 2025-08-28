#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço SMS - Claudia Cobranças
Envio de códigos de verificação via SMS
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SMSService:
    """Serviço de envio de SMS"""
    
    def __init__(self):
        self.provider = os.getenv('SMS_PROVIDER', 'console')  # console, twilio, aws
        self.setup_provider()
    
    def setup_provider(self):
        """Configurar provedor SMS"""
        if self.provider == 'twilio':
            try:
                from twilio.rest import Client
                self.client = Client(
                    os.getenv('TWILIO_ACCOUNT_SID'),
                    os.getenv('TWILIO_AUTH_TOKEN')
                )
                self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
                logger.info("✅ Twilio configurado")
            except ImportError:
                logger.warning("⚠️ Twilio não instalado, usando console")
                self.provider = 'console'
        
        elif self.provider == 'aws':
            try:
                import boto3
                self.client = boto3.client('sns')
                self.from_number = os.getenv('AWS_SNS_PHONE_NUMBER')
                logger.info("✅ AWS SNS configurado")
            except ImportError:
                logger.warning("⚠️ AWS SNS não instalado, usando console")
                self.provider = 'console'
        
        else:
            logger.info("📱 Usando modo console para SMS")
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Enviar SMS"""
        try:
            if self.provider == 'twilio':
                return self._send_twilio(phone_number, message)
            elif self.provider == 'aws':
                return self._send_aws(phone_number, message)
            else:
                return self._send_console(phone_number, message)
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return False
    
    def _send_twilio(self, phone_number: str, message: str) -> bool:
        """Enviar via Twilio"""
        try:
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )
            logger.info(f"📱 SMS Twilio enviado para {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Erro Twilio: {e}")
            return False
    
    def _send_aws(self, phone_number: str, message: str) -> bool:
        """Enviar via AWS SNS"""
        try:
            self.client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            logger.info(f"📱 SMS AWS enviado para {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Erro AWS SNS: {e}")
            return False
    
    def _send_console(self, phone_number: str, message: str) -> bool:
        """Enviar via console (desenvolvimento)"""
        print(f"\n{'='*50}")
        print(f"📱 SMS SIMULADO")
        print(f"Para: {phone_number}")
        print(f"Mensagem: {message}")
        print(f"{'='*50}\n")
        
        logger.info(f"📱 SMS console enviado para {phone_number}: {message}")
        return True

# Instância global
sms_service = SMSService()
