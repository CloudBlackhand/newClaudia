#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Monitoramento Oracle Cloud
Métricas, alertas e health checks para produção
"""

import asyncio
import time
import psutil
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import aiohttp
from .logger import logger

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    uptime_seconds: float
    
@dataclass
class ApplicationMetrics:
    """Métricas da aplicação"""
    timestamp: str
    whatsapp_connected: bool
    messages_sent_last_hour: int
    messages_sent_today: int
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
        self.alerts = []
        self.start_time = time.time()
        
        # Registrar health checks padrão
        self._register_default_checks()
        
    def _register_default_checks(self):
        """Registrar health checks padrão"""
        
        async def database_check():
            # Verificar se diretórios essenciais existem
            dirs = ['uploads', 'faturas', 'sessions', 'logs']
            for dir_name in dirs:
                if not os.path.exists(dir_name):
                    raise Exception(f"Directory {dir_name} not found")
            return {'directories': 'ok'}
            
        async def whatsapp_check():
            # Verificar se processo WhatsApp está responsivo
            # Aqui seria conectado com o WhatsAppClient real
            return {'whatsapp': 'checking'}
            
        async def disk_space_check():
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_percent < 10:
                raise Exception(f"Low disk space: {free_percent:.1f}% free")
                
            return {'disk_free_percent': round(free_percent, 1)}
            
        async def memory_check():
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                raise Exception(f"High memory usage: {memory.percent}%")
                
            return {'memory_used_percent': memory.percent}
            
        self.health_checker.register_check('database', database_check)
        self.health_checker.register_check('whatsapp', whatsapp_check)
        self.health_checker.register_check('disk_space', disk_space_check)
        self.health_checker.register_check('memory', memory_check)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Coletar métricas do sistema"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memória
        memory = psutil.virtual_memory()
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Rede
        network = psutil.net_io_counters()
        
        # Processos
        process_count = len(psutil.pids())
        
        # Uptime
        uptime = time.time() - self.start_time
        
        return SystemMetrics(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk_percent,
            network_io={
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            },
            process_count=process_count,
            uptime_seconds=uptime
        )
    
    def get_application_metrics(self, app_state: Dict[str, Any]) -> ApplicationMetrics:
        """Coletar métricas da aplicação"""
        # Process info
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return ApplicationMetrics(
            timestamp=datetime.utcnow().isoformat(),
            whatsapp_connected=app_state.get('whatsapp_connected', False),
            messages_sent_last_hour=app_state.get('messages_sent_last_hour', 0),
            messages_sent_today=app_state.get('messages_sent_today', 0),
            active_conversations=app_state.get('active_conversations', 0),
            error_count_last_hour=app_state.get('error_count_last_hour', 0),
            avg_response_time=app_state.get('avg_response_time', 0.0),
            memory_usage_mb=memory_info.rss / 1024 / 1024
        )
    
    def check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Verificar condições de alerta"""
        alerts = []
        
        # Alertas de sistema
        if system_metrics.cpu_percent > 80:
            alerts.append({
                'type': 'system',
                'level': 'warning',
                'message': f'High CPU usage: {system_metrics.cpu_percent}%',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        if system_metrics.memory_percent > 85:
            alerts.append({
                'type': 'system',
                'level': 'critical',
                'message': f'High memory usage: {system_metrics.memory_percent}%',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        if system_metrics.disk_percent > 90:
            alerts.append({
                'type': 'system',
                'level': 'critical',
                'message': f'Low disk space: {100 - system_metrics.disk_percent:.1f}% free',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Alertas de aplicação
        if not app_metrics.whatsapp_connected:
            alerts.append({
                'type': 'application',
                'level': 'warning',
                'message': 'WhatsApp not connected',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        if app_metrics.error_count_last_hour > 10:
            alerts.append({
                'type': 'application',
                'level': 'warning',
                'message': f'High error rate: {app_metrics.error_count_last_hour} errors in last hour',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Armazenar alertas
        self.alerts.extend(alerts)
        
        # Manter apenas últimos 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
            
        # Log críticos
        for alert in alerts:
            if alert['level'] == 'critical':
                logger.error(f"CRITICAL ALERT: {alert['message']}", alert_data=alert)
            elif alert['level'] == 'warning':
                logger.warning(f"WARNING ALERT: {alert['message']}", alert_data=alert)
                
        return alerts
    
    async def collect_metrics(self, app_state: Dict[str, Any]) -> Dict[str, Any]:
        """Coletar todas as métricas"""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics(app_state)
        health_status = await self.health_checker.run_all_checks()
        alerts = self.check_alerts(system_metrics, app_metrics)
        
        metrics_data = {
            'system': asdict(system_metrics),
            'application': asdict(app_metrics),
            'health': health_status,
            'alerts': alerts[-10:],  # Últimos 10 alertas
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Armazenar no histórico
        self.metrics_history.append(metrics_data)
        
        # Manter apenas última hora de métricas (assumindo coleta a cada 30s)
        if len(self.metrics_history) > 120:
            self.metrics_history = self.metrics_history[-120:]
            
        # Log métricas principais
        logger.info("Metrics collected",
                   cpu_percent=system_metrics.cpu_percent,
                   memory_percent=system_metrics.memory_percent,
                   whatsapp_connected=app_metrics.whatsapp_connected,
                   active_conversations=app_metrics.active_conversations)
        
        return metrics_data
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard"""
        if not self.metrics_history:
            return {'error': 'No metrics available'}
            
        latest = self.metrics_history[-1]
        
        # Calcular trends (última hora)
        if len(self.metrics_history) >= 2:
            previous = self.metrics_history[-2]
            cpu_trend = latest['system']['cpu_percent'] - previous['system']['cpu_percent']
            memory_trend = latest['system']['memory_percent'] - previous['system']['memory_percent']
        else:
            cpu_trend = 0
            memory_trend = 0
            
        return {
            'current': latest,
            'trends': {
                'cpu': cpu_trend,
                'memory': memory_trend
            },
            'recent_alerts': self.alerts[-5:],
            'uptime_hours': round(latest['system']['uptime_seconds'] / 3600, 1),
            'metrics_history': self.metrics_history[-20:]  # Últimas 20 coletas
        }

# Instância global do monitor
monitor = SystemMonitor()