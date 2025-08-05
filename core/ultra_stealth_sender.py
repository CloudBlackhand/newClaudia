#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA STEALTH SENDER - Sistema Ultra-Robusto Anti-Detecção
Resolve TODOS os problemas críticos identificados:
✅ Para quando acabar a lista
✅ Robustez no stealth de envio  
✅ Evita WhatsApp cair
✅ Controle de repetição
✅ Simulação humana avançada
"""

import asyncio
import logging
import random
import time
import math
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class UltraStealthSender:
    """🚀 SISTEMA ULTRA-ROBUSTO - Resolve todos os problemas críticos"""
    
    def __init__(self):
        self.running = False
        self.total_sent = 0
        self.total_failed = 0
        self.current_batch = 0
        self.total_batches = 0
        self.processed_records = set()  # 🛑 EVITA REPETIÇÃO
        self.last_message_time = 0
        self.message_count = 0
        self.stealth_level = "ULTRA"
        
        # 🛡️ PROTEÇÃO CONTRA BLOQUEIO
        self.max_messages_per_hour = 50
        self.max_messages_per_day = 200
        self.hourly_count = 0
        self.daily_count = 0
        self.last_hour_reset = datetime.now()
        self.last_day_reset = datetime.now()
        
        # 🤖 SIMULAÇÃO HUMANA AVANÇADA
        self.human_patterns = {
            "typing_speed": (0.05, 0.15),  # segundos por caractere
            "thinking_pauses": (0.5, 2.0),  # pausas para "pensar"
            "message_intervals": (15, 45),   # intervalo entre mensagens
            "batch_pauses": (120, 300),      # pausas entre lotes
            "random_actions": True,          # ações aleatórias
            "typo_probability": 0.02,        # 2% chance de "errar" e corrigir
        }
        
        self.stats = {
            "messages_sent": 0,
            "faturas_sent": 0,
            "conversations": 0,
            "stealth_actions": 0,
            "human_simulation": 0
        }
    
    async def execute_mass_sending(self, 
                                 data: List[Dict[str, Any]], 
                                 whatsapp_client, 
                                 stats_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """🚀 EXECUÇÃO ULTRA-ROBUSTA - Resolve todos os problemas"""
        try:
            logger.info(f"🚀 INICIANDO ULTRA STEALTH para {len(data)} registros")
            logger.info(f"🛡️ PROTEÇÃO: Máximo {self.max_messages_per_hour}/hora, {self.max_messages_per_day}/dia")
            
            self.running = True
            self.total_batches = self._calculate_batches(len(data))
            
            # 🛑 VERIFICAÇÃO CRÍTICA - Não repetir se já processado
            if not data:
                logger.warning("⚠️ Lista vazia - NADA PARA PROCESSAR")
                return {"total_sent": 0, "total_failed": 0, "success_rate": "0%", "status": "lista_vazia"}
            
            # 🔄 FILTRAR REGISTROS JÁ PROCESSADOS
            unprocessed_data = [record for record in data if record.get("id") not in self.processed_records]
            
            if not unprocessed_data:
                logger.info("✅ TODOS OS REGISTROS JÁ FORAM PROCESSADOS - PARANDO")
                return {"total_sent": 0, "total_failed": 0, "success_rate": "100%", "status": "ja_processado"}
            
            logger.info(f"📊 Processando {len(unprocessed_data)} registros não processados")
            
            # 🤖 CONFIGURAÇÕES ULTRA STEALTH
            base_interval = random.randint(*self.human_patterns["message_intervals"])
            batch_size = self._calculate_optimal_batch_size(len(unprocessed_data))
            batch_pause = random.randint(*self.human_patterns["batch_pauses"])
            
            # 📦 DIVIDIR EM LOTES INTELIGENTES
            batches = [unprocessed_data[i:i + batch_size] for i in range(0, len(unprocessed_data), batch_size)]
            
            # 🔄 PROCESSAR CADA LOTE COM PROTEÇÃO MÁXIMA
            for i, batch in enumerate(batches):
                if not self.running:
                    logger.info("🛑 ULTRA STEALTH interrompido manualmente")
                    break
                
                # 🛡️ VERIFICAÇÃO DE LIMITES CRÍTICOS
                if not await self._check_safety_limits():
                    logger.warning("⚠️ LIMITES DE SEGURANÇA ATINGIDOS - PAUSANDO")
                    await self._emergency_pause()
                    continue
                
                self.current_batch = i + 1
                logger.info(f"📦 Processando lote {self.current_batch}/{len(batches)} ({len(batch)} registros)")
                
                # 🔄 PROCESSAR CADA REGISTRO COM PROTEÇÃO
                for record in batch:
                    if not self.running:
                        break
                    
                    # 🛡️ VERIFICAÇÃO FINAL DE SEGURANÇA
                    if not await self._check_safety_limits():
                        logger.warning("⚠️ LIMITE DE SEGURANÇA ATINGIDO - PARANDO")
                        break
                    
                    # 🔄 VERIFICAR SE JÁ FOI PROCESSADO
                    record_id = record.get("id", f"{record.get('phone', '')}_{record.get('nome', '')}")
                    if record_id in self.processed_records:
                        logger.info(f"⏭️ Registro já processado: {record_id}")
                        continue
                    
                    # 🤖 ENVIO ULTRA STEALTH
                    success = await self._send_message_ultra_stealth(record, whatsapp_client)
                    
                    if success:
                        # 🛑 MARCAR COMO PROCESSADO
                        self.processed_records.add(record_id)
                        self.total_sent += 1
                        self.hourly_count += 1
                        self.daily_count += 1
                        self.message_count += 1
                        
                        # 🤖 SIMULAÇÃO HUMANA AVANÇADA
                        await self._simulate_human_behavior()
                    
                    # ⏱️ INTERVALO ULTRA INTELIGENTE
                    if self.running and batch.index(record) < len(batch) - 1:
                        interval = self._calculate_ultra_interval()
                        logger.info(f"⏱️ Aguardando {interval:.1f}s (simulação humana)...")
                        await asyncio.sleep(interval)
                
                # 📊 ATUALIZAR ESTATÍSTICAS
                if stats_callback:
                    stats_callback(self.stats)
                
                # ☕ PAUSA ENTRE LOTES (exceto o último)
                if self.running and i < len(batches) - 1:
                    batch_sleep = self._calculate_batch_pause()
                    logger.info(f"☕ Pausa de {batch_sleep:.1f}s entre lotes (simulação humana)...")
                    await asyncio.sleep(batch_sleep)
            
            # ✅ FINALIZAR COM SUCESSO
            result = {
                "total_sent": self.total_sent,
                "total_failed": self.total_failed,
                "success_rate": f"{(self.total_sent / len(unprocessed_data) * 100):.1f}%" if unprocessed_data else "0%",
                "status": "concluido",
                "processed_records": len(self.processed_records),
                "stealth_level": self.stealth_level
            }
            
            logger.info(f"✅ ULTRA STEALTH concluído: {result['success_rate']} de sucesso")
            logger.info(f"🛡️ Proteção ativa: {self.hourly_count}/hora, {self.daily_count}/dia")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no ULTRA STEALTH: {e}")
            return {"total_sent": self.total_sent, "total_failed": self.total_failed, "error": str(e)}
        finally:
            self.running = False
    
    async def _check_safety_limits(self) -> bool:
        """🛡️ VERIFICAÇÃO CRÍTICA DE LIMITES DE SEGURANÇA"""
        now = datetime.now()
        
        # 🔄 RESETAR CONTADORES
        if (now - self.last_hour_reset).total_seconds() > 3600:
            self.hourly_count = 0
            self.last_hour_reset = now
        
        if (now - self.last_day_reset).total_seconds() > 86400:
            self.daily_count = 0
            self.last_day_reset = now
        
        # 🛡️ VERIFICAR LIMITES
        if self.hourly_count >= self.max_messages_per_hour:
            logger.warning(f"🚨 LIMITE HORÁRIO ATINGIDO: {self.hourly_count}/{self.max_messages_per_hour}")
            return False
        
        if self.daily_count >= self.max_messages_per_day:
            logger.warning(f"🚨 LIMITE DIÁRIO ATINGIDO: {self.daily_count}/{self.max_messages_per_day}")
            return False
        
        return True
    
    async def _emergency_pause(self):
        """🚨 PAUSA DE EMERGÊNCIA - Proteção máxima"""
        pause_time = random.randint(1800, 3600)  # 30-60 minutos
        logger.warning(f"🚨 PAUSA DE EMERGÊNCIA: {pause_time/60:.1f} minutos")
        await asyncio.sleep(pause_time)
    
    async def _send_message_ultra_stealth(self, record: Dict[str, Any], whatsapp_client) -> bool:
        """🤖 ENVIO ULTRA STEALTH - Simulação humana avançada"""
        try:
            phone = record.get("phone", "")
            nome = record.get("nome", "Cliente")
            mensagem = self._generate_ultra_message(record)
            fatura = record.get("fatura_path")
            
            # 🤖 SIMULAÇÃO HUMANA AVANÇADA
            await self._simulate_human_behavior()
            
            # 📤 ENVIAR MENSAGEM
            success = await whatsapp_client.send_message(phone, mensagem, fatura)
            
            if success:
                logger.info(f"✅ ULTRA STEALTH: Mensagem enviada para {nome} ({phone})")
                self.total_sent += 1
                self.stats["messages_sent"] += 1
                
                if fatura:
                    self.stats["faturas_sent"] += 1
                
                self.stats["conversations"] += 1
                self.stats["stealth_actions"] += 1
            else:
                logger.error(f"❌ Falha ULTRA STEALTH para {nome} ({phone})")
                self.total_failed += 1
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro no envio ULTRA STEALTH: {e}")
            self.total_failed += 1
            return False
    
    async def _simulate_human_behavior(self):
        """🤖 SIMULAÇÃO HUMANA AVANÇADA - Comportamento realista"""
        try:
            # 🧠 PAUSAS PARA "PENSAR"
            thinking_pause = random.uniform(*self.human_patterns["thinking_pauses"])
            await asyncio.sleep(thinking_pause)
            
            # 🎲 AÇÕES ALEATÓRIAS (se habilitado)
            if self.human_patterns["random_actions"] and random.random() < 0.1:
                await self._perform_random_action()
            
            # ⌨️ SIMULAÇÃO DE DIGITAÇÃO HUMANA
            if random.random() < self.human_patterns["typo_probability"]:
                await self._simulate_typo_correction()
            
            self.stats["human_simulation"] += 1
            
        except Exception as e:
            logger.debug(f"Erro na simulação humana: {e}")
    
    async def _perform_random_action(self):
        """🎲 AÇÕES ALEATÓRIAS - Simular comportamento humano"""
        actions = [
            lambda: asyncio.sleep(random.uniform(0.5, 2.0)),  # Pausa aleatória
            lambda: logger.debug("🤖 Ação humana simulada: verificando mensagem"),
            lambda: asyncio.sleep(random.uniform(1.0, 3.0)),  # Outra pausa
        ]
        
        action = random.choice(actions)
        await action()
    
    async def _simulate_typo_correction(self):
        """⌨️ SIMULAR CORREÇÃO DE ERRO DE DIGITAÇÃO"""
        logger.debug("⌨️ Simulando correção de erro de digitação...")
        await asyncio.sleep(random.uniform(0.5, 1.5))
    
    def _generate_ultra_message(self, record: Dict[str, Any]) -> str:
        """🎲 GERADOR ULTRA DE MENSAGENS - Variação máxima"""
        nome = record.get("nome", "Cliente")
        valor = record.get("valor", "")
        vencimento = record.get("vencimento", "")
        
        # 🎲 TEMPLATES ULTRA VARIADOS
        templates = [
            f"Olá {nome}! 😊 Estamos enviando sua fatura no valor de R$ {valor}, com vencimento em {vencimento}. Por favor, confirme o recebimento.",
            f"Prezado(a) {nome}, segue sua fatura conforme solicitado. Valor: R$ {valor} | Vencimento: {vencimento}. 📄",
            f"Boa tarde, {nome}. Conforme combinado, estou encaminhando sua fatura (R$ {valor}) com data de vencimento {vencimento}. Qualquer dúvida, estamos à disposição! 💼",
            f"Oi {nome}! 😄 Aqui está sua fatura: R$ {valor} - Vence em {vencimento}. Confirma o recebimento?",
            f"Olá {nome}, tudo bem? 📋 Segue sua fatura: R$ {valor} | Vencimento: {vencimento}. Aguardo confirmação!",
            f"Prezado {nome}, conforme solicitado, sua fatura está anexada. Valor: R$ {valor} | Vencimento: {vencimento}. 📎",
            f"Boa tarde, {nome}! 💼 Estou enviando sua fatura no valor de R$ {valor}, vencimento {vencimento}. Confirma?",
            f"Oi {nome}! 📄 Sua fatura está aqui: R$ {valor} - Vence em {vencimento}. Tudo certo?",
        ]
        
        return random.choice(templates)
    
    def _calculate_ultra_interval(self) -> float:
        """⏱️ CÁLCULO ULTRA INTELIGENTE DE INTERVALO"""
        base_interval = random.randint(*self.human_patterns["message_intervals"])
        
        # 🎲 VARIAÇÃO ALEATÓRIA
        variation = random.uniform(-0.3, 0.3)
        interval = base_interval * (1 + variation)
        
        # 🛡️ PROTEÇÃO MÍNIMA
        return max(interval, 10.0)  # Mínimo 10 segundos
    
    def _calculate_batch_pause(self) -> float:
        """☕ CÁLCULO DE PAUSA ENTRE LOTES"""
        base_pause = random.randint(*self.human_patterns["batch_pauses"])
        variation = random.uniform(-0.2, 0.2)
        return base_pause * (1 + variation)
    
    def _calculate_optimal_batch_size(self, total_records: int) -> int:
        """📦 CÁLCULO INTELIGENTE DE TAMANHO DE LOTE"""
        if total_records <= 10:
            return 2
        elif total_records <= 50:
            return 5
        elif total_records <= 100:
            return 8
        else:
            return 10
    
    def _calculate_batches(self, total_records: int, batch_size: int = 5) -> int:
        """Calcular número de lotes"""
        return (total_records + batch_size - 1) // batch_size
    
    def stop(self):
        """🛑 Parar envio em andamento"""
        logger.info("🛑 Solicitação para parar ULTRA STEALTH")
        self.running = False
        
    def get_progress(self) -> Dict[str, Any]:
        """📊 Obter progresso atual"""
        progress = 0
        if self.total_batches > 0:
            progress = (self.current_batch / self.total_batches) * 100
            
        return {
            "running": self.running,
            "current_batch": self.current_batch,
            "total_batches": self.total_batches,
            "messages_sent": self.total_sent,
            "messages_failed": self.total_failed,
            "progress_percentage": f"{progress:.1f}%",
            "stealth_level": self.stealth_level,
            "hourly_count": self.hourly_count,
            "daily_count": self.daily_count,
            "processed_records": len(self.processed_records)
        } 
# -*- coding: utf-8 -*-
"""
ULTRA STEALTH SENDER - Sistema Ultra-Robusto Anti-Detecção
Resolve TODOS os problemas críticos identificados:
✅ Para quando acabar a lista
✅ Robustez no stealth de envio  
✅ Evita WhatsApp cair
✅ Controle de repetição
✅ Simulação humana avançada
"""

import asyncio
import logging
import random
import time
import math
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class UltraStealthSender:
    """🚀 SISTEMA ULTRA-ROBUSTO - Resolve todos os problemas críticos"""
    
    def __init__(self):
        self.running = False
        self.total_sent = 0
        self.total_failed = 0
        self.current_batch = 0
        self.total_batches = 0
        self.processed_records = set()  # 🛑 EVITA REPETIÇÃO
        self.last_message_time = 0
        self.message_count = 0
        self.stealth_level = "ULTRA"
        
        # 🛡️ PROTEÇÃO CONTRA BLOQUEIO
        self.max_messages_per_hour = 50
        self.max_messages_per_day = 200
        self.hourly_count = 0
        self.daily_count = 0
        self.last_hour_reset = datetime.now()
        self.last_day_reset = datetime.now()
        
        # 🤖 SIMULAÇÃO HUMANA AVANÇADA
        self.human_patterns = {
            "typing_speed": (0.05, 0.15),  # segundos por caractere
            "thinking_pauses": (0.5, 2.0),  # pausas para "pensar"
            "message_intervals": (15, 45),   # intervalo entre mensagens
            "batch_pauses": (120, 300),      # pausas entre lotes
            "random_actions": True,          # ações aleatórias
            "typo_probability": 0.02,        # 2% chance de "errar" e corrigir
        }
        
        self.stats = {
            "messages_sent": 0,
            "faturas_sent": 0,
            "conversations": 0,
            "stealth_actions": 0,
            "human_simulation": 0
        }
    
    async def execute_mass_sending(self, 
                                 data: List[Dict[str, Any]], 
                                 whatsapp_client, 
                                 stats_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """🚀 EXECUÇÃO ULTRA-ROBUSTA - Resolve todos os problemas"""
        try:
            logger.info(f"🚀 INICIANDO ULTRA STEALTH para {len(data)} registros")
            logger.info(f"🛡️ PROTEÇÃO: Máximo {self.max_messages_per_hour}/hora, {self.max_messages_per_day}/dia")
            
            self.running = True
            self.total_batches = self._calculate_batches(len(data))
            
            # 🛑 VERIFICAÇÃO CRÍTICA - Não repetir se já processado
            if not data:
                logger.warning("⚠️ Lista vazia - NADA PARA PROCESSAR")
                return {"total_sent": 0, "total_failed": 0, "success_rate": "0%", "status": "lista_vazia"}
            
            # 🔄 FILTRAR REGISTROS JÁ PROCESSADOS
            unprocessed_data = [record for record in data if record.get("id") not in self.processed_records]
            
            if not unprocessed_data:
                logger.info("✅ TODOS OS REGISTROS JÁ FORAM PROCESSADOS - PARANDO")
                return {"total_sent": 0, "total_failed": 0, "success_rate": "100%", "status": "ja_processado"}
            
            logger.info(f"📊 Processando {len(unprocessed_data)} registros não processados")
            
            # 🤖 CONFIGURAÇÕES ULTRA STEALTH
            base_interval = random.randint(*self.human_patterns["message_intervals"])
            batch_size = self._calculate_optimal_batch_size(len(unprocessed_data))
            batch_pause = random.randint(*self.human_patterns["batch_pauses"])
            
            # 📦 DIVIDIR EM LOTES INTELIGENTES
            batches = [unprocessed_data[i:i + batch_size] for i in range(0, len(unprocessed_data), batch_size)]
            
            # 🔄 PROCESSAR CADA LOTE COM PROTEÇÃO MÁXIMA
            for i, batch in enumerate(batches):
                if not self.running:
                    logger.info("🛑 ULTRA STEALTH interrompido manualmente")
                    break
                
                # 🛡️ VERIFICAÇÃO DE LIMITES CRÍTICOS
                if not await self._check_safety_limits():
                    logger.warning("⚠️ LIMITES DE SEGURANÇA ATINGIDOS - PAUSANDO")
                    await self._emergency_pause()
                    continue
                
                self.current_batch = i + 1
                logger.info(f"📦 Processando lote {self.current_batch}/{len(batches)} ({len(batch)} registros)")
                
                # 🔄 PROCESSAR CADA REGISTRO COM PROTEÇÃO
                for record in batch:
                    if not self.running:
                        break
                    
                    # 🛡️ VERIFICAÇÃO FINAL DE SEGURANÇA
                    if not await self._check_safety_limits():
                        logger.warning("⚠️ LIMITE DE SEGURANÇA ATINGIDO - PARANDO")
                        break
                    
                    # 🔄 VERIFICAR SE JÁ FOI PROCESSADO
                    record_id = record.get("id", f"{record.get('phone', '')}_{record.get('nome', '')}")
                    if record_id in self.processed_records:
                        logger.info(f"⏭️ Registro já processado: {record_id}")
                        continue
                    
                    # 🤖 ENVIO ULTRA STEALTH
                    success = await self._send_message_ultra_stealth(record, whatsapp_client)
                    
                    if success:
                        # 🛑 MARCAR COMO PROCESSADO
                        self.processed_records.add(record_id)
                        self.total_sent += 1
                        self.hourly_count += 1
                        self.daily_count += 1
                        self.message_count += 1
                        
                        # 🤖 SIMULAÇÃO HUMANA AVANÇADA
                        await self._simulate_human_behavior()
                    
                    # ⏱️ INTERVALO ULTRA INTELIGENTE
                    if self.running and batch.index(record) < len(batch) - 1:
                        interval = self._calculate_ultra_interval()
                        logger.info(f"⏱️ Aguardando {interval:.1f}s (simulação humana)...")
                        await asyncio.sleep(interval)
                
                # 📊 ATUALIZAR ESTATÍSTICAS
                if stats_callback:
                    stats_callback(self.stats)
                
                # ☕ PAUSA ENTRE LOTES (exceto o último)
                if self.running and i < len(batches) - 1:
                    batch_sleep = self._calculate_batch_pause()
                    logger.info(f"☕ Pausa de {batch_sleep:.1f}s entre lotes (simulação humana)...")
                    await asyncio.sleep(batch_sleep)
            
            # ✅ FINALIZAR COM SUCESSO
            result = {
                "total_sent": self.total_sent,
                "total_failed": self.total_failed,
                "success_rate": f"{(self.total_sent / len(unprocessed_data) * 100):.1f}%" if unprocessed_data else "0%",
                "status": "concluido",
                "processed_records": len(self.processed_records),
                "stealth_level": self.stealth_level
            }
            
            logger.info(f"✅ ULTRA STEALTH concluído: {result['success_rate']} de sucesso")
            logger.info(f"🛡️ Proteção ativa: {self.hourly_count}/hora, {self.daily_count}/dia")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no ULTRA STEALTH: {e}")
            return {"total_sent": self.total_sent, "total_failed": self.total_failed, "error": str(e)}
        finally:
            self.running = False
    
    async def _check_safety_limits(self) -> bool:
        """🛡️ VERIFICAÇÃO CRÍTICA DE LIMITES DE SEGURANÇA"""
        now = datetime.now()
        
        # 🔄 RESETAR CONTADORES
        if (now - self.last_hour_reset).total_seconds() > 3600:
            self.hourly_count = 0
            self.last_hour_reset = now
        
        if (now - self.last_day_reset).total_seconds() > 86400:
            self.daily_count = 0
            self.last_day_reset = now
        
        # 🛡️ VERIFICAR LIMITES
        if self.hourly_count >= self.max_messages_per_hour:
            logger.warning(f"🚨 LIMITE HORÁRIO ATINGIDO: {self.hourly_count}/{self.max_messages_per_hour}")
            return False
        
        if self.daily_count >= self.max_messages_per_day:
            logger.warning(f"🚨 LIMITE DIÁRIO ATINGIDO: {self.daily_count}/{self.max_messages_per_day}")
            return False
        
        return True
    
    async def _emergency_pause(self):
        """🚨 PAUSA DE EMERGÊNCIA - Proteção máxima"""
        pause_time = random.randint(1800, 3600)  # 30-60 minutos
        logger.warning(f"🚨 PAUSA DE EMERGÊNCIA: {pause_time/60:.1f} minutos")
        await asyncio.sleep(pause_time)
    
    async def _send_message_ultra_stealth(self, record: Dict[str, Any], whatsapp_client) -> bool:
        """🤖 ENVIO ULTRA STEALTH - Simulação humana avançada"""
        try:
            phone = record.get("phone", "")
            nome = record.get("nome", "Cliente")
            mensagem = self._generate_ultra_message(record)
            fatura = record.get("fatura_path")
            
            # 🤖 SIMULAÇÃO HUMANA AVANÇADA
            await self._simulate_human_behavior()
            
            # 📤 ENVIAR MENSAGEM
            success = await whatsapp_client.send_message(phone, mensagem, fatura)
            
            if success:
                logger.info(f"✅ ULTRA STEALTH: Mensagem enviada para {nome} ({phone})")
                self.total_sent += 1
                self.stats["messages_sent"] += 1
                
                if fatura:
                    self.stats["faturas_sent"] += 1
                
                self.stats["conversations"] += 1
                self.stats["stealth_actions"] += 1
            else:
                logger.error(f"❌ Falha ULTRA STEALTH para {nome} ({phone})")
                self.total_failed += 1
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro no envio ULTRA STEALTH: {e}")
            self.total_failed += 1
            return False
    
    async def _simulate_human_behavior(self):
        """🤖 SIMULAÇÃO HUMANA AVANÇADA - Comportamento realista"""
        try:
            # 🧠 PAUSAS PARA "PENSAR"
            thinking_pause = random.uniform(*self.human_patterns["thinking_pauses"])
            await asyncio.sleep(thinking_pause)
            
            # 🎲 AÇÕES ALEATÓRIAS (se habilitado)
            if self.human_patterns["random_actions"] and random.random() < 0.1:
                await self._perform_random_action()
            
            # ⌨️ SIMULAÇÃO DE DIGITAÇÃO HUMANA
            if random.random() < self.human_patterns["typo_probability"]:
                await self._simulate_typo_correction()
            
            self.stats["human_simulation"] += 1
            
        except Exception as e:
            logger.debug(f"Erro na simulação humana: {e}")
    
    async def _perform_random_action(self):
        """🎲 AÇÕES ALEATÓRIAS - Simular comportamento humano"""
        actions = [
            lambda: asyncio.sleep(random.uniform(0.5, 2.0)),  # Pausa aleatória
            lambda: logger.debug("🤖 Ação humana simulada: verificando mensagem"),
            lambda: asyncio.sleep(random.uniform(1.0, 3.0)),  # Outra pausa
        ]
        
        action = random.choice(actions)
        await action()
    
    async def _simulate_typo_correction(self):
        """⌨️ SIMULAR CORREÇÃO DE ERRO DE DIGITAÇÃO"""
        logger.debug("⌨️ Simulando correção de erro de digitação...")
        await asyncio.sleep(random.uniform(0.5, 1.5))
    
    def _generate_ultra_message(self, record: Dict[str, Any]) -> str:
        """🎲 GERADOR ULTRA DE MENSAGENS - Variação máxima"""
        nome = record.get("nome", "Cliente")
        valor = record.get("valor", "")
        vencimento = record.get("vencimento", "")
        
        # 🎲 TEMPLATES ULTRA VARIADOS
        templates = [
            f"Olá {nome}! 😊 Estamos enviando sua fatura no valor de R$ {valor}, com vencimento em {vencimento}. Por favor, confirme o recebimento.",
            f"Prezado(a) {nome}, segue sua fatura conforme solicitado. Valor: R$ {valor} | Vencimento: {vencimento}. 📄",
            f"Boa tarde, {nome}. Conforme combinado, estou encaminhando sua fatura (R$ {valor}) com data de vencimento {vencimento}. Qualquer dúvida, estamos à disposição! 💼",
            f"Oi {nome}! 😄 Aqui está sua fatura: R$ {valor} - Vence em {vencimento}. Confirma o recebimento?",
            f"Olá {nome}, tudo bem? 📋 Segue sua fatura: R$ {valor} | Vencimento: {vencimento}. Aguardo confirmação!",
            f"Prezado {nome}, conforme solicitado, sua fatura está anexada. Valor: R$ {valor} | Vencimento: {vencimento}. 📎",
            f"Boa tarde, {nome}! 💼 Estou enviando sua fatura no valor de R$ {valor}, vencimento {vencimento}. Confirma?",
            f"Oi {nome}! 📄 Sua fatura está aqui: R$ {valor} - Vence em {vencimento}. Tudo certo?",
        ]
        
        return random.choice(templates)
    
    def _calculate_ultra_interval(self) -> float:
        """⏱️ CÁLCULO ULTRA INTELIGENTE DE INTERVALO"""
        base_interval = random.randint(*self.human_patterns["message_intervals"])
        
        # 🎲 VARIAÇÃO ALEATÓRIA
        variation = random.uniform(-0.3, 0.3)
        interval = base_interval * (1 + variation)
        
        # 🛡️ PROTEÇÃO MÍNIMA
        return max(interval, 10.0)  # Mínimo 10 segundos
    
    def _calculate_batch_pause(self) -> float:
        """☕ CÁLCULO DE PAUSA ENTRE LOTES"""
        base_pause = random.randint(*self.human_patterns["batch_pauses"])
        variation = random.uniform(-0.2, 0.2)
        return base_pause * (1 + variation)
    
    def _calculate_optimal_batch_size(self, total_records: int) -> int:
        """📦 CÁLCULO INTELIGENTE DE TAMANHO DE LOTE"""
        if total_records <= 10:
            return 2
        elif total_records <= 50:
            return 5
        elif total_records <= 100:
            return 8
        else:
            return 10
    
    def _calculate_batches(self, total_records: int, batch_size: int = 5) -> int:
        """Calcular número de lotes"""
        return (total_records + batch_size - 1) // batch_size
    
    def stop(self):
        """🛑 Parar envio em andamento"""
        logger.info("🛑 Solicitação para parar ULTRA STEALTH")
        self.running = False
        
    def get_progress(self) -> Dict[str, Any]:
        """📊 Obter progresso atual"""
        progress = 0
        if self.total_batches > 0:
            progress = (self.current_batch / self.total_batches) * 100
            
        return {
            "running": self.running,
            "current_batch": self.current_batch,
            "total_batches": self.total_batches,
            "messages_sent": self.total_sent,
            "messages_failed": self.total_failed,
            "progress_percentage": f"{progress:.1f}%",
            "stealth_level": self.stealth_level,
            "hourly_count": self.hourly_count,
            "daily_count": self.daily_count,
            "processed_records": len(self.processed_records)
        } 
 