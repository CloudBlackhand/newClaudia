#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗂️ GERENCIADOR DE ARMAZENAMENTO INTELIGENTE
Sistema que evita consumo excessivo de espaço no Railway
"""

import os
import time
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class StorageManager:
    """🗂️ GERENCIADOR INTELIGENTE DE ARMAZENAMENTO"""
    
    def __init__(self, faturas_dir: str = "faturas"):
        self.faturas_dir = Path(faturas_dir)
        self.faturas_dir.mkdir(exist_ok=True)
        
        # 🎯 CONFIGURAÇÕES DE LIMITE
        self.max_storage_mb = 50  # Máximo 50MB para faturas
        self.max_files_per_user = 5  # Máximo 5 faturas por usuário
        self.max_file_age_hours = 24  # Faturas expiram em 24h
        self.cleanup_interval_minutes = 30  # Limpeza a cada 30min
        
        # 📊 ESTATÍSTICAS
        self.last_cleanup = None
        self.files_cleaned = 0
        self.space_freed_mb = 0.0
        
        logger.info("🗂️ StorageManager inicializado com limite de 50MB")
    
    async def save_invoice(self, phone: str, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """💾 SALVAR FATURA COM CONTROLE INTELIGENTE DE ESPAÇO"""
        try:
            # 🧹 Limpeza preventiva antes de salvar
            await self.cleanup_expired_files()
            await self.enforce_user_limits(phone)
            
            # 📁 Criar pasta do usuário
            user_dir = self.faturas_dir / phone
            user_dir.mkdir(exist_ok=True)
            
            # 📄 Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fatura_{timestamp}.pdf"
            full_path = user_dir / filename
            
            # 💾 Salvar arquivo
            with open(full_path, 'wb') as f:
                f.write(file_data)
            
            file_size_mb = len(file_data) / (1024 * 1024)
            
            logger.info(f"💾 Fatura salva: {full_path} ({file_size_mb:.2f}MB)")
            
            # 📊 Verificar se ainda temos espaço
            total_size = await self.get_total_storage_size()
            if total_size > self.max_storage_mb:
                logger.warning(f"⚠️ Limite de armazenamento excedido: {total_size:.2f}MB")
                await self.emergency_cleanup()
            
            return {
                'success': True,
                'file_path': str(full_path),
                'file_size_mb': file_size_mb,
                'total_storage_mb': total_size,
                'files_for_user': await self.count_user_files(phone)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar fatura: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cleanup_expired_files(self) -> Dict[str, Any]:
        """🧹 LIMPEZA AUTOMÁTICA DE ARQUIVOS EXPIRADOS"""
        try:
            if not self.faturas_dir.exists():
                return {'files_removed': 0, 'space_freed_mb': 0.0}
            
            cutoff_time = datetime.now() - timedelta(hours=self.max_file_age_hours)
            files_removed = 0
            space_freed = 0.0
            
            # 🔍 Escanear todos os arquivos
            for user_dir in self.faturas_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.iterdir():
                        if file_path.is_file():
                            # ⏰ Verificar idade do arquivo
                            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            
                            if file_time < cutoff_time:
                                file_size = file_path.stat().st_size / (1024 * 1024)
                                file_path.unlink()  # Deletar arquivo
                                files_removed += 1
                                space_freed += file_size
                                logger.info(f"🗑️ Arquivo expirado removido: {file_path}")
                    
                    # 📁 Remover pasta vazia
                    if not any(user_dir.iterdir()):
                        user_dir.rmdir()
                        logger.info(f"📁 Pasta vazia removida: {user_dir}")
            
            self.last_cleanup = datetime.now()
            self.files_cleaned += files_removed
            self.space_freed_mb += space_freed
            
            logger.info(f"🧹 Limpeza concluída: {files_removed} arquivos, {space_freed:.2f}MB liberados")
            
            return {
                'files_removed': files_removed,
                'space_freed_mb': space_freed,
                'total_storage_mb': await self.get_total_storage_size()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")
            return {'files_removed': 0, 'space_freed_mb': 0.0, 'error': str(e)}
    
    async def enforce_user_limits(self, phone: str) -> None:
        """👤 APLICAR LIMITES POR USUÁRIO"""
        try:
            user_dir = self.faturas_dir / phone
            if not user_dir.exists():
                return
            
            # 📊 Listar arquivos do usuário por data
            user_files = []
            for file_path in user_dir.iterdir():
                if file_path.is_file():
                    user_files.append((file_path, file_path.stat().st_mtime))
            
            # 🔄 Ordenar por data (mais antigos primeiro)
            user_files.sort(key=lambda x: x[1])
            
            # 🗑️ Remover arquivos excedentes
            while len(user_files) >= self.max_files_per_user:
                oldest_file, _ = user_files.pop(0)
                file_size = oldest_file.stat().st_size / (1024 * 1024)
                oldest_file.unlink()
                self.space_freed_mb += file_size
                logger.info(f"🗑️ Limite por usuário: arquivo antigo removido {oldest_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar limites do usuário: {e}")
    
    async def emergency_cleanup(self) -> None:
        """🚨 LIMPEZA DE EMERGÊNCIA QUANDO ESPAÇO ESGOTA"""
        try:
            logger.warning("🚨 LIMPEZA DE EMERGÊNCIA ATIVADA!")
            
            # 🗑️ Remover 50% dos arquivos mais antigos
            all_files = []
            
            for user_dir in self.faturas_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.iterdir():
                        if file_path.is_file():
                            all_files.append((file_path, file_path.stat().st_mtime))
            
            # 🔄 Ordenar por data
            all_files.sort(key=lambda x: x[1])
            
            # 🗑️ Remover metade dos arquivos
            files_to_remove = len(all_files) // 2
            for i in range(files_to_remove):
                file_path, _ = all_files[i]
                file_size = file_path.stat().st_size / (1024 * 1024)
                file_path.unlink()
                self.space_freed_mb += file_size
            
            logger.warning(f"🚨 Limpeza de emergência: {files_to_remove} arquivos removidos")
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de emergência: {e}")
    
    async def get_total_storage_size(self) -> float:
        """📊 CALCULAR TAMANHO TOTAL EM MB"""
        try:
            if not self.faturas_dir.exists():
                return 0.0
            
            total_size = 0
            for user_dir in self.faturas_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.iterdir():
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
            
            return total_size / (1024 * 1024)  # Converter para MB
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular tamanho: {e}")
            return 0.0
    
    async def count_user_files(self, phone: str) -> int:
        """📊 CONTAR ARQUIVOS DO USUÁRIO"""
        try:
            user_dir = self.faturas_dir / phone
            if not user_dir.exists():
                return 0
            
            return len([f for f in user_dir.iterdir() if f.is_file()])
            
        except Exception as e:
            logger.error(f"❌ Erro ao contar arquivos: {e}")
            return 0
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """📊 ESTATÍSTICAS COMPLETAS DO ARMAZENAMENTO"""
        try:
            total_size = await self.get_total_storage_size()
            total_files = 0
            users_count = 0
            
            if self.faturas_dir.exists():
                for user_dir in self.faturas_dir.iterdir():
                    if user_dir.is_dir():
                        users_count += 1
                        total_files += len([f for f in user_dir.iterdir() if f.is_file()])
            
            return {
                'total_size_mb': total_size,
                'max_size_mb': self.max_storage_mb,
                'usage_percent': (total_size / self.max_storage_mb) * 100,
                'total_files': total_files,
                'users_count': users_count,
                'max_files_per_user': self.max_files_per_user,
                'max_file_age_hours': self.max_file_age_hours,
                'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
                'files_cleaned_total': self.files_cleaned,
                'space_freed_total_mb': self.space_freed_mb
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {'error': str(e)}
    
    async def schedule_periodic_cleanup(self) -> None:
        """⏰ AGENDAR LIMPEZA PERIÓDICA"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)  # Converter para segundos
                logger.info("⏰ Executando limpeza periódica...")
                await self.cleanup_expired_files()
                
                # 📊 Log das estatísticas
                stats = await self.get_storage_stats()
                logger.info(f"📊 Armazenamento: {stats['total_size_mb']:.2f}MB / {stats['max_size_mb']}MB ({stats['usage_percent']:.1f}%)")
                
        except Exception as e:
            logger.error(f"❌ Erro na limpeza periódica: {e}")

# 🎯 INSTÂNCIA GLOBAL
storage_manager = StorageManager()
# -*- coding: utf-8 -*-
"""
🗂️ GERENCIADOR DE ARMAZENAMENTO INTELIGENTE
Sistema que evita consumo excessivo de espaço no Railway
"""

import os
import time
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class StorageManager:
    """🗂️ GERENCIADOR INTELIGENTE DE ARMAZENAMENTO"""
    
    def __init__(self, faturas_dir: str = "faturas"):
        self.faturas_dir = Path(faturas_dir)
        self.faturas_dir.mkdir(exist_ok=True)
        
        # 🎯 CONFIGURAÇÕES DE LIMITE
        self.max_storage_mb = 50  # Máximo 50MB para faturas
        self.max_files_per_user = 5  # Máximo 5 faturas por usuário
        self.max_file_age_hours = 24  # Faturas expiram em 24h
        self.cleanup_interval_minutes = 30  # Limpeza a cada 30min
        
        # 📊 ESTATÍSTICAS
        self.last_cleanup = None
        self.files_cleaned = 0
        self.space_freed_mb = 0.0
        
        logger.info("🗂️ StorageManager inicializado com limite de 50MB")
    
    async def save_invoice(self, phone: str, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """💾 SALVAR FATURA COM CONTROLE INTELIGENTE DE ESPAÇO"""
        try:
            # 🧹 Limpeza preventiva antes de salvar
            await self.cleanup_expired_files()
            await self.enforce_user_limits(phone)
            
            # 📁 Criar pasta do usuário
            user_dir = self.faturas_dir / phone
            user_dir.mkdir(exist_ok=True)
            
            # 📄 Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fatura_{timestamp}.pdf"
            full_path = user_dir / filename
            
            # 💾 Salvar arquivo
            with open(full_path, 'wb') as f:
                f.write(file_data)
            
            file_size_mb = len(file_data) / (1024 * 1024)
            
            logger.info(f"💾 Fatura salva: {full_path} ({file_size_mb:.2f}MB)")
            
            # 📊 Verificar se ainda temos espaço
            total_size = await self.get_total_storage_size()
            if total_size > self.max_storage_mb:
                logger.warning(f"⚠️ Limite de armazenamento excedido: {total_size:.2f}MB")
                await self.emergency_cleanup()
            
            return {
                'success': True,
                'file_path': str(full_path),
                'file_size_mb': file_size_mb,
                'total_storage_mb': total_size,
                'files_for_user': await self.count_user_files(phone)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar fatura: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cleanup_expired_files(self) -> Dict[str, Any]:
        """🧹 LIMPEZA AUTOMÁTICA DE ARQUIVOS EXPIRADOS"""
        try:
            if not self.faturas_dir.exists():
                return {'files_removed': 0, 'space_freed_mb': 0.0}
            
            cutoff_time = datetime.now() - timedelta(hours=self.max_file_age_hours)
            files_removed = 0
            space_freed = 0.0
            
            # 🔍 Escanear todos os arquivos
            for user_dir in self.faturas_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.iterdir():
                        if file_path.is_file():
                            # ⏰ Verificar idade do arquivo
                            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            
                            if file_time < cutoff_time:
                                file_size = file_path.stat().st_size / (1024 * 1024)
                                file_path.unlink()  # Deletar arquivo
                                files_removed += 1
                                space_freed += file_size
                                logger.info(f"🗑️ Arquivo expirado removido: {file_path}")
                    
                    # 📁 Remover pasta vazia
                    if not any(user_dir.iterdir()):
                        user_dir.rmdir()
                        logger.info(f"📁 Pasta vazia removida: {user_dir}")
            
            self.last_cleanup = datetime.now()
            self.files_cleaned += files_removed
            self.space_freed_mb += space_freed
            
            logger.info(f"🧹 Limpeza concluída: {files_removed} arquivos, {space_freed:.2f}MB liberados")
            
            return {
                'files_removed': files_removed,
                'space_freed_mb': space_freed,
                'total_storage_mb': await self.get_total_storage_size()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")
            return {'files_removed': 0, 'space_freed_mb': 0.0, 'error': str(e)}
    
    async def enforce_user_limits(self, phone: str) -> None:
        """👤 APLICAR LIMITES POR USUÁRIO"""
        try:
            user_dir = self.faturas_dir / phone
            if not user_dir.exists():
                return
            
            # 📊 Listar arquivos do usuário por data
            user_files = []
            for file_path in user_dir.iterdir():
                if file_path.is_file():
                    user_files.append((file_path, file_path.stat().st_mtime))
            
            # 🔄 Ordenar por data (mais antigos primeiro)
            user_files.sort(key=lambda x: x[1])
            
            # 🗑️ Remover arquivos excedentes
            while len(user_files) >= self.max_files_per_user:
                oldest_file, _ = user_files.pop(0)
                file_size = oldest_file.stat().st_size / (1024 * 1024)
                oldest_file.unlink()
                self.space_freed_mb += file_size
                logger.info(f"🗑️ Limite por usuário: arquivo antigo removido {oldest_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar limites do usuário: {e}")
    
    async def emergency_cleanup(self) -> None:
        """🚨 LIMPEZA DE EMERGÊNCIA QUANDO ESPAÇO ESGOTA"""
        try:
            logger.warning("🚨 LIMPEZA DE EMERGÊNCIA ATIVADA!")
            
            # 🗑️ Remover 50% dos arquivos mais antigos
            all_files = []
            
            for user_dir in self.faturas_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.iterdir():
                        if file_path.is_file():
                            all_files.append((file_path, file_path.stat().st_mtime))
            
            # 🔄 Ordenar por data
            all_files.sort(key=lambda x: x[1])
            
            # 🗑️ Remover metade dos arquivos
            files_to_remove = len(all_files) // 2
            for i in range(files_to_remove):
                file_path, _ = all_files[i]
                file_size = file_path.stat().st_size / (1024 * 1024)
                file_path.unlink()
                self.space_freed_mb += file_size
            
            logger.warning(f"🚨 Limpeza de emergência: {files_to_remove} arquivos removidos")
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de emergência: {e}")
    
    async def get_total_storage_size(self) -> float:
        """📊 CALCULAR TAMANHO TOTAL EM MB"""
        try:
            if not self.faturas_dir.exists():
                return 0.0
            
            total_size = 0
            for user_dir in self.faturas_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.iterdir():
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
            
            return total_size / (1024 * 1024)  # Converter para MB
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular tamanho: {e}")
            return 0.0
    
    async def count_user_files(self, phone: str) -> int:
        """📊 CONTAR ARQUIVOS DO USUÁRIO"""
        try:
            user_dir = self.faturas_dir / phone
            if not user_dir.exists():
                return 0
            
            return len([f for f in user_dir.iterdir() if f.is_file()])
            
        except Exception as e:
            logger.error(f"❌ Erro ao contar arquivos: {e}")
            return 0
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """📊 ESTATÍSTICAS COMPLETAS DO ARMAZENAMENTO"""
        try:
            total_size = await self.get_total_storage_size()
            total_files = 0
            users_count = 0
            
            if self.faturas_dir.exists():
                for user_dir in self.faturas_dir.iterdir():
                    if user_dir.is_dir():
                        users_count += 1
                        total_files += len([f for f in user_dir.iterdir() if f.is_file()])
            
            return {
                'total_size_mb': total_size,
                'max_size_mb': self.max_storage_mb,
                'usage_percent': (total_size / self.max_storage_mb) * 100,
                'total_files': total_files,
                'users_count': users_count,
                'max_files_per_user': self.max_files_per_user,
                'max_file_age_hours': self.max_file_age_hours,
                'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
                'files_cleaned_total': self.files_cleaned,
                'space_freed_total_mb': self.space_freed_mb
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {'error': str(e)}
    
    async def schedule_periodic_cleanup(self) -> None:
        """⏰ AGENDAR LIMPEZA PERIÓDICA"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)  # Converter para segundos
                logger.info("⏰ Executando limpeza periódica...")
                await self.cleanup_expired_files()
                
                # 📊 Log das estatísticas
                stats = await self.get_storage_stats()
                logger.info(f"📊 Armazenamento: {stats['total_size_mb']:.2f}MB / {stats['max_size_mb']}MB ({stats['usage_percent']:.1f}%)")
                
        except Exception as e:
            logger.error(f"❌ Erro na limpeza periódica: {e}")

# 🎯 INSTÂNCIA GLOBAL
storage_manager = StorageManager()
 