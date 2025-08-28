#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDIA COBRANÇAS - System Monitoring
Monitoramento do sistema de cobrança
"""

import asyncio
import time
import psutil
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, float]

@dataclass
class ApplicationMetrics:
    """Métricas da aplicação"""
    timestamp: str
    bot_active: bool
    messages_processed_last_hour: int
    messages_processed_today: int
    active_conversations: int
    error_count_last_hour: int
    avg_response_time: float
    memory_usage_mb: float

class HealthChecker:
    """Sistema de health checks"""
    
    def __init__(self):
        self.checks = {}
        self.last_results = {}
        
    def register_check(self, name: str, check_func, timeout: int = 10):
        """Registrar um health check"""
        self.checks[name] = {
            'func': check_func,
            'timeout': timeout
        }
        
    async def run_check(self, name: str) -> Dict[str, Any]:
        """Executar um health check específico"""
        if name not in self.checks:
            return {'status': 'unknown', 'error': 'Check not found'}
            
        check = self.checks[name]
        start_time = time.time()
        
        try:
            # Executar check com timeout
            result = await asyncio.wait_for(
                check['func'](), 
                timeout=check['timeout']
            )
            
            duration = time.time() - start_time
            
            return {
                'status': 'healthy',
                'duration_ms': round(duration * 1000, 2),
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            return {
                'status': 'timeout',
                'duration_ms': check['timeout'] * 1000,
                'error': f'Check timed out after {check["timeout"]}s',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'status': 'unhealthy',
                'duration_ms': round(duration * 1000, 2),
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Executar todos os health checks"""
        results = {}
        
        # Executar todos os checks em paralelo
        tasks = []
        for name in self.checks:
            tasks.append(self.run_check(name))
            
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organizar resultados
        for i, name in enumerate(self.checks):
            results[name] = check_results[i]
            
        # Determinar status geral
        all_healthy = all(
            result.get('status') == 'healthy' 
            for result in results.values()
        )
        
        return {
            'overall_status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': results
        }

class SystemMonitor:
    """Monitor completo do sistema"""
    
    def __init__(self):
        self.health_checker = HealthChecker()
        self.metrics_history = []
        self.max_history_size = 1000
        self.app_state = {
            'bot_active': False,
            'messages_processed': 0,
            'conversations': 0,
            'errors': 0,
            'start_time': datetime.utcnow()
        }
        
        # Registrar health checks básicos
        self._register_basic_checks()
    
    def _register_basic_checks(self):
        """Registrar health checks básicos"""
        self.health_checker.register_check('system', self._system_check)
        self.health_checker.register_check('memory', self._memory_check)
        self.health_checker.register_check('disk', self._disk_check)
        self.health_checker.register_check('application', self._application_check)
    
    async def _system_check(self) -> Dict[str, Any]:
        """Check do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            return {
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count(),
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"Erro no system check: {e}")
            raise
    
    async def _memory_check(self) -> Dict[str, Any]:
        """Check de memória"""
        try:
            memory = psutil.virtual_memory()
            return {
                'total_mb': memory.total / 1024 / 1024,
                'available_mb': memory.available / 1024 / 1024,
                'percent': memory.percent,
                'used_mb': memory.used / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"Erro no memory check: {e}")
            raise
    
    async def _disk_check(self) -> Dict[str, Any]:
        """Check de disco"""
        try:
            disk = psutil.disk_usage('/')
            return {
                'total_gb': disk.total / 1024 / 1024 / 1024,
                'free_gb': disk.free / 1024 / 1024 / 1024,
                'percent': (disk.used / disk.total) * 100
            }
        except Exception as e:
            logger.error(f"Erro no disk check: {e}")
            raise
    
    async def _application_check(self) -> Dict[str, Any]:
        """Check da aplicação"""
        try:
            uptime = (datetime.utcnow() - self.app_state['start_time']).total_seconds()
            return {
                'bot_active': self.app_state['bot_active'],
                'uptime_seconds': uptime,
                'messages_processed': self.app_state['messages_processed'],
                'conversations': self.app_state['conversations'],
                'errors': self.app_state['errors']
            }
        except Exception as e:
            logger.error(f"Erro no application check: {e}")
            raise
    
    def get_system_metrics(self) -> SystemMetrics:
        """Obter métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return SystemMetrics(
                timestamp=datetime.utcnow().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_usage_percent=(disk.used / disk.total) * 100,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                }
            )
        except Exception as e:
            logger.error(f"Erro ao obter métricas do sistema: {e}")
            raise
    
    def get_application_metrics(self) -> ApplicationMetrics:
        """Obter métricas da aplicação"""
        try:
            # Calcular métricas da última hora
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)
            
            # Filtrar métricas da última hora
            recent_metrics = [
                m for m in self.metrics_history 
                if datetime.fromisoformat(m['timestamp']) > one_hour_ago
            ]
            
            messages_last_hour = sum(m.get('messages_processed', 0) for m in recent_metrics)
            errors_last_hour = sum(m.get('errors', 0) for m in recent_metrics)
            
            return ApplicationMetrics(
                timestamp=now.isoformat(),
                bot_active=self.app_state['bot_active'],
                messages_processed_last_hour=messages_last_hour,
                messages_processed_today=self.app_state['messages_processed'],
                active_conversations=self.app_state['conversations'],
                error_count_last_hour=errors_last_hour,
                avg_response_time=0.0,  # Implementar se necessário
                memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024
            )
        except Exception as e:
            logger.error(f"Erro ao obter métricas da aplicação: {e}")
            raise
    
    def update_app_state(self, **kwargs):
        """Atualizar estado da aplicação"""
        self.app_state.update(kwargs)
        
        # Adicionar à história
        self.metrics_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            **self.app_state.copy()
        })
        
        # Manter tamanho da história
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    async def get_full_status(self) -> Dict[str, Any]:
        """Obter status completo do sistema"""
        try:
            # Executar health checks
            health_status = await self.health_checker.run_all_checks()
            
            # Obter métricas
            system_metrics = self.get_system_metrics()
            app_metrics = self.get_application_metrics()
            
            return {
                'status': 'healthy' if health_status['overall_status'] == 'healthy' else 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'health_checks': health_status,
                'system_metrics': {
                    'cpu_percent': system_metrics.cpu_percent,
                    'memory_percent': system_metrics.memory_percent,
                    'memory_used_mb': system_metrics.memory_used_mb,
                    'disk_usage_percent': system_metrics.disk_usage_percent
                },
                'application_metrics': {
                    'bot_active': app_metrics.bot_active,
                    'messages_processed_last_hour': app_metrics.messages_processed_last_hour,
                    'messages_processed_today': app_metrics.messages_processed_today,
                    'active_conversations': app_metrics.active_conversations,
                    'error_count_last_hour': app_metrics.error_count_last_hour,
                    'avg_response_time': app_metrics.avg_response_time,
                    'memory_usage_mb': app_metrics.memory_usage_mb
                },
                'uptime_seconds': (datetime.utcnow() - self.app_state['start_time']).total_seconds()
            }
        except Exception as e:
            logger.error(f"Erro ao obter status completo: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def export_metrics(self, format: str = 'json') -> str:
        """Exportar métricas"""
        try:
            if format == 'json':
                return json.dumps({
                    'system_metrics': self.get_system_metrics().__dict__,
                    'application_metrics': self.get_application_metrics().__dict__,
                    'app_state': self.app_state,
                    'history_size': len(self.metrics_history)
                }, indent=2)
            else:
                raise ValueError(f"Formato não suportado: {format}")
        except Exception as e:
            logger.error(f"Erro ao exportar métricas: {e}")
            raise

# Instância global
system_monitor = SystemMonitor()
 