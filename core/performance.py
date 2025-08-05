#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Performance e Cache para Oracle Cloud
Otimizações específicas para ambiente Oracle Cloud
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional, Callable, Union
from functools import wraps, lru_cache
from datetime import datetime, timedelta
import aioredis
import pickle
import os
from .logger import logger, performance_metric

class MemoryCache:
    """Cache em memória com TTL"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        
    def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache"""
        if key not in self.cache:
            return None
            
        # Verificar TTL
        if time.time() - self.timestamps[key] > self.default_ttl:
            self.delete(key)
            return None
            
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Definir valor no cache"""
        self.cache[key] = value
        self.timestamps[key] = time.time()
        
    def delete(self, key: str) -> None:
        """Remover valor do cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        
    def clear(self) -> None:
        """Limpar cache completamente"""
        self.cache.clear()
        self.timestamps.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        return {
            'total_keys': len(self.cache),
            'memory_usage_bytes': sum(len(str(v)) for v in self.cache.values()),
            'oldest_entry': min(self.timestamps.values()) if self.timestamps else None
        }

class AsyncCache:
    """Sistema de cache assíncrono com múltiplos backends"""
    
    def __init__(self):
        self.memory_cache = MemoryCache()
        self.redis_client = None
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
    async def initialize_redis(self):
        """Inicializar conexão Redis (opcional)"""
        try:
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                self.redis_client = await aioredis.from_url(redis_url)
                logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis not available, using memory cache only: {e}")
            
    async def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache (tenta Redis primeiro, depois memória)"""
        try:
            # Tentar Redis primeiro
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats['hits'] += 1
                    return pickle.loads(value)
            
            # Fallback para cache em memória
            value = self.memory_cache.get(key)
            if value is not None:
                self.cache_stats['hits'] += 1
                return value
                
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Definir valor no cache"""
        try:
            # Redis
            if self.redis_client:
                await self.redis_client.setex(key, ttl, pickle.dumps(value))
            
            # Memory cache
            self.memory_cache.set(key, value, ttl)
            self.cache_stats['sets'] += 1
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    async def delete(self, key: str) -> None:
        """Remover valor do cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            self.memory_cache.delete(key)
            self.cache_stats['deletes'] += 1
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        stats = self.cache_stats.copy()
        stats['memory_cache'] = self.memory_cache.get_stats()
        if self.cache_stats['hits'] + self.cache_stats['misses'] > 0:
            stats['hit_rate'] = self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses'])
        else:
            stats['hit_rate'] = 0
        return stats

# Instância global do cache
cache = AsyncCache()

class PerformanceOptimizer:
    """Otimizador de performance para Oracle Cloud"""
    
    def __init__(self):
        self.metrics = {
            'function_calls': {},
            'async_tasks': {},
            'cache_usage': {},
            'db_queries': {},
        }
        
    def cache_result(self, ttl: int = 3600, key_prefix: str = ""):
        """Decorator para cache de resultados de função"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Gerar chave do cache
                cache_key = self._generate_cache_key(func, args, kwargs, key_prefix)
                
                # Tentar obter do cache
                start_time = time.time()
                cached_result = await cache.get(cache_key)
                
                if cached_result is not None:
                    duration = time.time() - start_time
                    performance_metric(f"cache_hit_{func.__name__}", duration)
                    return cached_result
                
                # Executar função
                result = await func(*args, **kwargs)
                
                # Salvar no cache
                await cache.set(cache_key, result, ttl)
                
                duration = time.time() - start_time
                performance_metric(f"cache_miss_{func.__name__}", duration)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Para funções síncronas
                cache_key = self._generate_cache_key(func, args, kwargs, key_prefix)
                
                start_time = time.time()
                cached_result = cache.memory_cache.get(cache_key)
                
                if cached_result is not None:
                    duration = time.time() - start_time
                    performance_metric(f"cache_hit_{func.__name__}", duration)
                    return cached_result
                
                result = func(*args, **kwargs)
                cache.memory_cache.set(cache_key, result, ttl)
                
                duration = time.time() - start_time
                performance_metric(f"cache_miss_{func.__name__}", duration)
                
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    def _generate_cache_key(self, func: Callable, args: tuple, kwargs: dict, prefix: str) -> str:
        """Gerar chave única para o cache"""
        # Criar hash dos argumentos
        args_str = str(args) + str(sorted(kwargs.items()))
        args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
        
        return f"{prefix}{func.__name__}:{args_hash}"
    
    def rate_limit(self, calls_per_second: float = 10.0):
        """Decorator para rate limiting"""
        def decorator(func: Callable):
            last_call_time = {'time': 0}
            min_interval = 1.0 / calls_per_second
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                now = time.time()
                time_since_last = now - last_call_time['time']
                
                if time_since_last < min_interval:
                    await asyncio.sleep(min_interval - time_since_last)
                
                last_call_time['time'] = time.time()
                return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                now = time.time()
                time_since_last = now - last_call_time['time']
                
                if time_since_last < min_interval:
                    time.sleep(min_interval - time_since_last)
                
                last_call_time['time'] = time.time()
                return func(*args, **kwargs)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    def batch_processor(self, batch_size: int = 10, max_wait: float = 1.0):
        """Decorator para processamento em lotes"""
        def decorator(func: Callable):
            batch_queue = []
            last_process_time = time.time()
            
            @wraps(func)
            async def wrapper(item):
                batch_queue.append(item)
                
                # Processar se batch cheio ou tempo limite
                if (len(batch_queue) >= batch_size or 
                    time.time() - last_process_time > max_wait):
                    
                    items_to_process = batch_queue.copy()
                    batch_queue.clear()
                    
                    # Processar lote
                    results = await func(items_to_process)
                    last_process_time = time.time()
                    
                    return results
                
                return None  # Item adicionado ao batch, aguardando processamento
                
            return wrapper
        return decorator

# Instância global do otimizador
optimizer = PerformanceOptimizer()

class AsyncPool:
    """Pool de conexões assíncronas"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.semaphore = asyncio.Semaphore(max_connections)
        self.active_connections = 0
        
    async def execute(self, coro):
        """Executar corrotina com controle de pool"""
        async with self.semaphore:
            self.active_connections += 1
            try:
                result = await coro
                return result
            finally:
                self.active_connections -= 1

class DataProcessor:
    """Processador de dados otimizado"""
    
    @staticmethod
    @optimizer.cache_result(ttl=1800)  # Cache por 30 minutos
    async def process_excel_data(file_hash: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processar dados do Excel com cache"""
        start_time = time.time()
        
        # Simulação de processamento pesado
        await asyncio.sleep(0.1)  # Simular I/O
        
        # Processamento real aqui
        processed_data = {
            'total_rows': len(data.get('rows', [])),
            'processed_at': datetime.utcnow().isoformat(),
            'file_hash': file_hash
        }
        
        duration = time.time() - start_time
        performance_metric("excel_processing", duration, rows=len(data.get('rows', [])))
        
        return processed_data
    
    @staticmethod
    @lru_cache(maxsize=100)
    def clean_phone_number(phone: str) -> str:
        """Limpar número de telefone (com cache LRU)"""
        if not phone:
            return ""
        return ''.join(filter(str.isdigit, phone))[-11:]
    
    @staticmethod
    @lru_cache(maxsize=50)
    def validate_cpf(cpf: str) -> bool:
        """Validar CPF (com cache LRU)"""
        if not cpf:
            return False
        
        # Remover caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
            
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
            
        # Validação dos dígitos verificadores
        def calculate_digit(cpf_partial):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, range(len(cpf_partial) + 1, 1, -1)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        return (calculate_digit(cpf[:9]) == int(cpf[9]) and 
                calculate_digit(cpf[:10]) == int(cpf[10]))

# Configurações de performance para Oracle Cloud
ORACLE_PERFORMANCE_CONFIG = {
    'max_workers': int(os.getenv('MAX_WORKERS', 4)),
    'cache_ttl': int(os.getenv('CACHE_TTL', 3600)),
    'upload_max_size': os.getenv('UPLOAD_MAX_SIZE', '50MB'),
    'concurrent_downloads': int(os.getenv('CONCURRENT_DOWNLOADS', 3)),
    'batch_size': int(os.getenv('BATCH_SIZE', 10)),
    'rate_limit_rps': float(os.getenv('RATE_LIMIT_RPS', 10.0))
}

# Inicialização do sistema de cache
async def initialize_performance_system():
    """Inicializar sistema de performance"""
    try:
        await cache.initialize_redis()
        logger.info("Performance system initialized", config=ORACLE_PERFORMANCE_CONFIG)
    except Exception as e:
        logger.error(f"Failed to initialize performance system: {e}")

# Pool global de conexões
connection_pool = AsyncPool(max_connections=ORACLE_PERFORMANCE_CONFIG['max_workers'])
# -*- coding: utf-8 -*-
"""
Sistema de Performance e Cache para Oracle Cloud
Otimizações específicas para ambiente Oracle Cloud
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional, Callable, Union
from functools import wraps, lru_cache
from datetime import datetime, timedelta
import aioredis
import pickle
import os
from .logger import logger, performance_metric

class MemoryCache:
    """Cache em memória com TTL"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        
    def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache"""
        if key not in self.cache:
            return None
            
        # Verificar TTL
        if time.time() - self.timestamps[key] > self.default_ttl:
            self.delete(key)
            return None
            
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Definir valor no cache"""
        self.cache[key] = value
        self.timestamps[key] = time.time()
        
    def delete(self, key: str) -> None:
        """Remover valor do cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        
    def clear(self) -> None:
        """Limpar cache completamente"""
        self.cache.clear()
        self.timestamps.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        return {
            'total_keys': len(self.cache),
            'memory_usage_bytes': sum(len(str(v)) for v in self.cache.values()),
            'oldest_entry': min(self.timestamps.values()) if self.timestamps else None
        }

class AsyncCache:
    """Sistema de cache assíncrono com múltiplos backends"""
    
    def __init__(self):
        self.memory_cache = MemoryCache()
        self.redis_client = None
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
    async def initialize_redis(self):
        """Inicializar conexão Redis (opcional)"""
        try:
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                self.redis_client = await aioredis.from_url(redis_url)
                logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis not available, using memory cache only: {e}")
            
    async def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache (tenta Redis primeiro, depois memória)"""
        try:
            # Tentar Redis primeiro
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats['hits'] += 1
                    return pickle.loads(value)
            
            # Fallback para cache em memória
            value = self.memory_cache.get(key)
            if value is not None:
                self.cache_stats['hits'] += 1
                return value
                
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Definir valor no cache"""
        try:
            # Redis
            if self.redis_client:
                await self.redis_client.setex(key, ttl, pickle.dumps(value))
            
            # Memory cache
            self.memory_cache.set(key, value, ttl)
            self.cache_stats['sets'] += 1
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    async def delete(self, key: str) -> None:
        """Remover valor do cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            self.memory_cache.delete(key)
            self.cache_stats['deletes'] += 1
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        stats = self.cache_stats.copy()
        stats['memory_cache'] = self.memory_cache.get_stats()
        if self.cache_stats['hits'] + self.cache_stats['misses'] > 0:
            stats['hit_rate'] = self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses'])
        else:
            stats['hit_rate'] = 0
        return stats

# Instância global do cache
cache = AsyncCache()

class PerformanceOptimizer:
    """Otimizador de performance para Oracle Cloud"""
    
    def __init__(self):
        self.metrics = {
            'function_calls': {},
            'async_tasks': {},
            'cache_usage': {},
            'db_queries': {},
        }
        
    def cache_result(self, ttl: int = 3600, key_prefix: str = ""):
        """Decorator para cache de resultados de função"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Gerar chave do cache
                cache_key = self._generate_cache_key(func, args, kwargs, key_prefix)
                
                # Tentar obter do cache
                start_time = time.time()
                cached_result = await cache.get(cache_key)
                
                if cached_result is not None:
                    duration = time.time() - start_time
                    performance_metric(f"cache_hit_{func.__name__}", duration)
                    return cached_result
                
                # Executar função
                result = await func(*args, **kwargs)
                
                # Salvar no cache
                await cache.set(cache_key, result, ttl)
                
                duration = time.time() - start_time
                performance_metric(f"cache_miss_{func.__name__}", duration)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Para funções síncronas
                cache_key = self._generate_cache_key(func, args, kwargs, key_prefix)
                
                start_time = time.time()
                cached_result = cache.memory_cache.get(cache_key)
                
                if cached_result is not None:
                    duration = time.time() - start_time
                    performance_metric(f"cache_hit_{func.__name__}", duration)
                    return cached_result
                
                result = func(*args, **kwargs)
                cache.memory_cache.set(cache_key, result, ttl)
                
                duration = time.time() - start_time
                performance_metric(f"cache_miss_{func.__name__}", duration)
                
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    def _generate_cache_key(self, func: Callable, args: tuple, kwargs: dict, prefix: str) -> str:
        """Gerar chave única para o cache"""
        # Criar hash dos argumentos
        args_str = str(args) + str(sorted(kwargs.items()))
        args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
        
        return f"{prefix}{func.__name__}:{args_hash}"
    
    def rate_limit(self, calls_per_second: float = 10.0):
        """Decorator para rate limiting"""
        def decorator(func: Callable):
            last_call_time = {'time': 0}
            min_interval = 1.0 / calls_per_second
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                now = time.time()
                time_since_last = now - last_call_time['time']
                
                if time_since_last < min_interval:
                    await asyncio.sleep(min_interval - time_since_last)
                
                last_call_time['time'] = time.time()
                return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                now = time.time()
                time_since_last = now - last_call_time['time']
                
                if time_since_last < min_interval:
                    time.sleep(min_interval - time_since_last)
                
                last_call_time['time'] = time.time()
                return func(*args, **kwargs)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    def batch_processor(self, batch_size: int = 10, max_wait: float = 1.0):
        """Decorator para processamento em lotes"""
        def decorator(func: Callable):
            batch_queue = []
            last_process_time = time.time()
            
            @wraps(func)
            async def wrapper(item):
                batch_queue.append(item)
                
                # Processar se batch cheio ou tempo limite
                if (len(batch_queue) >= batch_size or 
                    time.time() - last_process_time > max_wait):
                    
                    items_to_process = batch_queue.copy()
                    batch_queue.clear()
                    
                    # Processar lote
                    results = await func(items_to_process)
                    last_process_time = time.time()
                    
                    return results
                
                return None  # Item adicionado ao batch, aguardando processamento
                
            return wrapper
        return decorator

# Instância global do otimizador
optimizer = PerformanceOptimizer()

class AsyncPool:
    """Pool de conexões assíncronas"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.semaphore = asyncio.Semaphore(max_connections)
        self.active_connections = 0
        
    async def execute(self, coro):
        """Executar corrotina com controle de pool"""
        async with self.semaphore:
            self.active_connections += 1
            try:
                result = await coro
                return result
            finally:
                self.active_connections -= 1

class DataProcessor:
    """Processador de dados otimizado"""
    
    @staticmethod
    @optimizer.cache_result(ttl=1800)  # Cache por 30 minutos
    async def process_excel_data(file_hash: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processar dados do Excel com cache"""
        start_time = time.time()
        
        # Simulação de processamento pesado
        await asyncio.sleep(0.1)  # Simular I/O
        
        # Processamento real aqui
        processed_data = {
            'total_rows': len(data.get('rows', [])),
            'processed_at': datetime.utcnow().isoformat(),
            'file_hash': file_hash
        }
        
        duration = time.time() - start_time
        performance_metric("excel_processing", duration, rows=len(data.get('rows', [])))
        
        return processed_data
    
    @staticmethod
    @lru_cache(maxsize=100)
    def clean_phone_number(phone: str) -> str:
        """Limpar número de telefone (com cache LRU)"""
        if not phone:
            return ""
        return ''.join(filter(str.isdigit, phone))[-11:]
    
    @staticmethod
    @lru_cache(maxsize=50)
    def validate_cpf(cpf: str) -> bool:
        """Validar CPF (com cache LRU)"""
        if not cpf:
            return False
        
        # Remover caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
            
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
            
        # Validação dos dígitos verificadores
        def calculate_digit(cpf_partial):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, range(len(cpf_partial) + 1, 1, -1)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        return (calculate_digit(cpf[:9]) == int(cpf[9]) and 
                calculate_digit(cpf[:10]) == int(cpf[10]))

# Configurações de performance para Oracle Cloud
ORACLE_PERFORMANCE_CONFIG = {
    'max_workers': int(os.getenv('MAX_WORKERS', 4)),
    'cache_ttl': int(os.getenv('CACHE_TTL', 3600)),
    'upload_max_size': os.getenv('UPLOAD_MAX_SIZE', '50MB'),
    'concurrent_downloads': int(os.getenv('CONCURRENT_DOWNLOADS', 3)),
    'batch_size': int(os.getenv('BATCH_SIZE', 10)),
    'rate_limit_rps': float(os.getenv('RATE_LIMIT_RPS', 10.0))
}

# Inicialização do sistema de cache
async def initialize_performance_system():
    """Inicializar sistema de performance"""
    try:
        await cache.initialize_redis()
        logger.info("Performance system initialized", config=ORACLE_PERFORMANCE_CONFIG)
    except Exception as e:
        logger.error(f"Failed to initialize performance system: {e}")

# Pool global de conexões
connection_pool = AsyncPool(max_connections=ORACLE_PERFORMANCE_CONFIG['max_workers'])