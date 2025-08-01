#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StealthSender - Módulo de envio com padrões anti-detecção
Funcionalidade para envio de mensagens em massa com padrões humanos
"""

import asyncio
import logging
import random
import time
from typing import List, Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

class StealthSender:
    """Classe para envio stealth de mensagens em massa"""
    
    def __init__(self):
        self.running = False
        self.total_sent = 0
        self.total_failed = 0
        self.current_batch = 0
        self.total_batches = 0
        self.stats = {
            "messages_sent": 0,
            "faturas_sent": 0,
            "conversations": 0
        }
    
    async def execute_mass_sending(self, 
                                 data: List[Dict[str, Any]], 
                                 whatsapp_client, 
                                 stats_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Executar envio em massa com padrões stealth"""
        try:
            logger.info(f"🚀 Iniciando envio stealth para {len(data)} registros")
            
            self.running = True
            self.total_batches = self._calculate_batches(len(data))
            
            # Configurações de intervalo
            base_interval = 15  # segundos entre mensagens
            interval_variation = 0.3  # variação de ±30%
            batch_size = 5  # mensagens por lote
            batch_pause = 120  # 2 minutos entre lotes
            
            # Inicialização de estatísticas
            self.total_sent = 0
            self.total_failed = 0
            self.current_batch = 0
            
            # Dividir em lotes
            batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
            
            # Processar cada lote com pausas entre eles
            for i, batch in enumerate(batches):
                if not self.running:
                    logger.info("🛑 Envio stealth interrompido manualmente")
                    break
                
                self.current_batch = i + 1
                logger.info(f"📦 Processando lote {self.current_batch}/{len(batches)}")
                
                # Processar cada registro no lote
                for record in batch:
                    if not self.running:
                        break
                    
                    # Enviar mensagem com anexo se aplicável
                    await self._send_message_stealth(record, whatsapp_client)
                    
                    # Intervalo variável entre mensagens (simular comportamento humano)
                    if self.running and batch.index(record) < len(batch) - 1:
                        variation = random.uniform(-interval_variation, interval_variation)
                        sleep_time = base_interval * (1 + variation)
                        logger.info(f"⏱️ Aguardando {sleep_time:.1f}s antes da próxima mensagem...")
                        await asyncio.sleep(sleep_time)
                
                # Atualizar estatísticas após cada lote
                if stats_callback:
                    stats_callback(self.stats)
                
                # Pausa entre lotes (exceto o último)
                if self.running and i < len(batches) - 1:
                    variation = random.uniform(-0.2, 0.2)  # ±20%
                    batch_sleep = batch_pause * (1 + variation)
                    logger.info(f"☕ Pausa de {batch_sleep:.1f}s entre lotes...")
                    await asyncio.sleep(batch_sleep)
            
            # Finalizar
            result = {
                "total_sent": self.total_sent,
                "total_failed": self.total_failed,
                "success_rate": f"{(self.total_sent / len(data) * 100):.1f}%" if len(data) > 0 else "0%"
            }
            
            logger.info(f"✅ Envio stealth concluído: {result['success_rate']} de sucesso")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no envio stealth: {e}")
            return {"total_sent": self.total_sent, "total_failed": self.total_failed, "error": str(e)}
        finally:
            self.running = False
    
    async def _send_message_stealth(self, record: Dict[str, Any], whatsapp_client) -> bool:
        """Enviar mensagem individual com padrão stealth"""
        try:
            phone = record.get("phone", "")
            nome = record.get("nome", "Cliente")
            mensagem = self._generate_message(record)
            fatura = record.get("fatura_path")
            
            # Simular digitação antes de enviar
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            # Enviar mensagem
            success = await whatsapp_client.send_message(phone, mensagem, fatura)
            
            if success:
                logger.info(f"✅ Mensagem enviada para {nome} ({phone})")
                self.total_sent += 1
                self.stats["messages_sent"] += 1
                
                if fatura:
                    self.stats["faturas_sent"] += 1
                
                self.stats["conversations"] += 1
            else:
                logger.error(f"❌ Falha ao enviar para {nome} ({phone})")
                self.total_failed += 1
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem stealth: {e}")
            self.total_failed += 1
            return False
    
    def _generate_message(self, record: Dict[str, Any]) -> str:
        """Gerar mensagem personalizada"""
        nome = record.get("nome", "Cliente")
        valor = record.get("valor", "")
        vencimento = record.get("vencimento", "")
        
        # Variação de mensagens para evitar detecção
        templates = [
            f"Olá {nome}, tudo bem? Estamos enviando sua fatura no valor de R$ {valor}, com vencimento em {vencimento}. Por favor, confirme o recebimento.",
            f"Prezado(a) {nome}, segue sua fatura conforme solicitado. Valor: R$ {valor} | Vencimento: {vencimento}.",
            f"Boa tarde, {nome}. Conforme combinado, estou encaminhando sua fatura (R$ {valor}) com data de vencimento {vencimento}. Qualquer dúvida, estamos à disposição."
        ]
        
        return random.choice(templates)
    
    def _calculate_batches(self, total_records: int, batch_size: int = 5) -> int:
        """Calcular número de lotes"""
        return (total_records + batch_size - 1) // batch_size
    
    def stop(self):
        """Parar envio em andamento"""
        logger.info("🛑 Solicitação para parar envio stealth")
        self.running = False
        
    def get_progress(self) -> Dict[str, Any]:
        """Obter progresso atual"""
        progress = 0
        if self.total_batches > 0:
            progress = (self.current_batch / self.total_batches) * 100
            
        return {
            "running": self.running,
            "current_batch": self.current_batch,
            "total_batches": self.total_batches,
            "messages_sent": self.total_sent,
            "messages_failed": self.total_failed,
            "progress_percentage": f"{progress:.1f}%"
        }