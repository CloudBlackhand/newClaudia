"""
Processador JSON otimizado para dados de clientes
"""
import json
import ijson
import asyncio
from typing import List, Dict, Any, Iterator, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from backend.utils.validators import JSONValidator, ClientData
from backend.utils.logger import billing_logger, app_logger
from backend.config.settings import active_config

class JSONProcessor:
    """Processador otimizado para arquivos JSON de clientes"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.config = active_config
        
    def load_clients_from_file(self, file_path: str) -> Dict[str, Any]:
        """Carrega e valida clientes de arquivo JSON"""
        result = {
            "success": False,
            "clients": [],
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            billing_logger.info("JSON_PROCESSING_STARTED", {"file_path": file_path})
            
            # Verifica se arquivo existe
            if not Path(file_path).exists():
                result["errors"].append(f"Arquivo não encontrado: {file_path}")
                return result
            
            # Carrega JSON dependendo do tamanho
            file_size = Path(file_path).stat().st_size
            
            if file_size > 10 * 1024 * 1024:  # > 10MB, usa streaming
                clients_data = list(self._stream_json_array(file_path))
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    clients_data = json.load(f)
            
            # Valida estrutura básica
            structure_validation = JSONValidator.validate_json_structure(clients_data)
            if not structure_validation["valid"]:
                result["errors"].extend(structure_validation["errors"])
                return result
            
            result["warnings"].extend(structure_validation["warnings"])
            
            # Processa clientes em lotes para eficiência
            batch_size = 1000
            all_valid_clients = []
            all_invalid_clients = []
            
            for i in range(0, len(clients_data), batch_size):
                batch = clients_data[i:i + batch_size]
                batch_result = self._process_batch(batch, i // batch_size + 1)
                
                all_valid_clients.extend(batch_result["valid_clients"])
                all_invalid_clients.extend(batch_result["invalid_clients"])
                
                if batch_result["errors"]:
                    result["warnings"].extend(batch_result["errors"])
            
            # Compila resultado final
            result.update({
                "success": True,
                "clients": all_valid_clients,
                "total": len(clients_data),
                "valid": len(all_valid_clients),
                "invalid": len(all_invalid_clients)
            })
            
            billing_logger.info("JSON_PROCESSING_COMPLETED", {
                "total_clients": result["total"],
                "valid_clients": result["valid"],
                "invalid_clients": result["invalid"],
                "success_rate": (result["valid"] / result["total"] * 100) if result["total"] > 0 else 0
            })
            
        except Exception as e:
            billing_logger.error("JSON_PROCESSING_FAILED", e, {"file_path": file_path})
            result["errors"].append(f"Erro ao processar JSON: {str(e)}")
        
        return result
    
    def _stream_json_array(self, file_path: str) -> Iterator[Dict]:
        """Stream de array JSON grande usando ijson"""
        try:
            with open(file_path, 'rb') as f:
                parser = ijson.items(f, 'item')
                for item in parser:
                    yield item
        except Exception as e:
            app_logger.error("JSON_STREAMING_FAILED", e, {"file_path": file_path})
            raise
    
    def _process_batch(self, batch: List[Dict], batch_number: int) -> Dict[str, Any]:
        """Processa lote de clientes com validação"""
        try:
            return JSONValidator.validate_clients_batch(batch)
        except Exception as e:
            app_logger.error("BATCH_PROCESSING_FAILED", e, {"batch_number": batch_number})
            return {
                "valid_clients": [],
                "invalid_clients": batch,
                "errors": [f"Erro no lote {batch_number}: {str(e)}"]
            }
    
    async def process_clients_async(self, clients_data: List[Dict]) -> Dict[str, Any]:
        """Processamento assíncrono de clientes"""
        loop = asyncio.get_event_loop()
        
        # Divide em chunks para processamento paralelo
        chunk_size = max(100, len(clients_data) // self.max_workers)
        chunks = [clients_data[i:i + chunk_size] for i in range(0, len(clients_data), chunk_size)]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                loop.run_in_executor(
                    executor, 
                    self._process_batch, 
                    chunk, 
                    idx + 1
                )
                for idx, chunk in enumerate(chunks)
            ]
            
            results = await asyncio.gather(*futures)
        
        # Consolida resultados
        consolidated_result = {
            "valid_clients": [],
            "invalid_clients": [],
            "errors": [],
            "warnings": []
        }
        
        for result in results:
            consolidated_result["valid_clients"].extend(result["valid_clients"])
            consolidated_result["invalid_clients"].extend(result["invalid_clients"])
            consolidated_result["errors"].extend(result.get("errors", []))
            consolidated_result["warnings"].extend(result.get("warnings", []))
        
        return consolidated_result
    
    def save_processed_clients(self, clients: List[ClientData], output_path: str) -> bool:
        """Salva clientes processados em arquivo"""
        try:
            # Converte para dict serializável
            clients_dict = [client.dict() for client in clients]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(clients_dict, f, ensure_ascii=False, indent=2)
            
            billing_logger.info("CLIENTS_SAVED", {
                "output_path": output_path,
                "count": len(clients)
            })
            return True
            
        except Exception as e:
            billing_logger.error("CLIENTS_SAVE_FAILED", e, {
                "output_path": output_path,
                "count": len(clients)
            })
            return False
    
    def filter_clients(self, clients: List[ClientData], filters: Dict[str, Any]) -> List[ClientData]:
        """Filtra clientes com base em critérios"""
        filtered_clients = []
        
        for client in clients:
            if self._client_matches_filters(client, filters):
                filtered_clients.append(client)
        
        billing_logger.info("CLIENTS_FILTERED", {
            "original_count": len(clients),
            "filtered_count": len(filtered_clients),
            "filters": filters
        })
        
        return filtered_clients
    
    def _client_matches_filters(self, client: ClientData, filters: Dict[str, Any]) -> bool:
        """Verifica se cliente atende aos filtros"""
        for key, value in filters.items():
            if key == "min_amount" and client.amount < value:
                return False
            elif key == "max_amount" and client.amount > value:
                return False
            elif key == "name_contains" and value.lower() not in client.name.lower():
                return False
            elif key == "phone_starts_with" and not client.phone.endswith(value):
                return False
        
        return True
    
    def get_processing_stats(self, file_path: str) -> Dict[str, Any]:
        """Retorna estatísticas de processamento sem carregar arquivo completo"""
        stats = {
            "file_exists": False,
            "file_size_mb": 0,
            "estimated_count": 0,
            "processing_method": "unknown"
        }
        
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                stats["file_exists"] = True
                stats["file_size_mb"] = file_path_obj.stat().st_size / (1024 * 1024)
                
                # Estima quantidade baseada no tamanho
                # Assume ~200 bytes por cliente em média
                stats["estimated_count"] = int(stats["file_size_mb"] * 1024 * 1024 / 200)
                
                if stats["file_size_mb"] > 10:
                    stats["processing_method"] = "streaming"
                else:
                    stats["processing_method"] = "standard"
        
        except Exception as e:
            app_logger.error("STATS_CALCULATION_FAILED", e, {"file_path": file_path})
        
        return stats

class ClientsBatchProcessor:
    """Processador especializado para grandes volumes de clientes"""
    
    def __init__(self, batch_size: int = 500):
        self.batch_size = batch_size
        self.processor = JSONProcessor()
    
    async def process_large_dataset(
        self, 
        file_path: str, 
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """Processa dataset grande com callback de progresso"""
        
        result = {
            "success": False,
            "processed_batches": 0,
            "total_clients": 0,
            "valid_clients": 0,
            "invalid_clients": 0,
            "errors": []
        }
        
        try:
            # Primeiro, conta total de itens para progresso
            total_count = self._count_json_items(file_path)
            result["total_clients"] = total_count
            
            valid_count = 0
            invalid_count = 0
            batch_count = 0
            
            # Processa em streaming
            current_batch = []
            
            for item in self.processor._stream_json_array(file_path):
                current_batch.append(item)
                
                if len(current_batch) >= self.batch_size:
                    # Processa lote atual
                    batch_result = await self._process_single_batch(current_batch)
                    valid_count += len(batch_result["valid_clients"])
                    invalid_count += len(batch_result["invalid_clients"])
                    batch_count += 1
                    
                    # Callback de progresso
                    if progress_callback:
                        progress_callback(batch_count * self.batch_size, total_count)
                    
                    current_batch = []
            
            # Processa último lote se não vazio
            if current_batch:
                batch_result = await self._process_single_batch(current_batch)
                valid_count += len(batch_result["valid_clients"])
                invalid_count += len(batch_result["invalid_clients"])
                batch_count += 1
            
            result.update({
                "success": True,
                "processed_batches": batch_count,
                "valid_clients": valid_count,
                "invalid_clients": invalid_count
            })
            
        except Exception as e:
            billing_logger.error("LARGE_DATASET_PROCESSING_FAILED", e, {"file_path": file_path})
            result["errors"].append(str(e))
        
        return result
    
    def _count_json_items(self, file_path: str) -> int:
        """Conta itens em array JSON sem carregar na memória"""
        count = 0
        try:
            with open(file_path, 'rb') as f:
                parser = ijson.items(f, 'item')
                for _ in parser:
                    count += 1
        except Exception:
            # Fallback: estima baseado no tamanho do arquivo
            file_size = Path(file_path).stat().st_size
            count = int(file_size / 200)  # Estimativa conservadora
        
        return count
    
    async def _process_single_batch(self, batch: List[Dict]) -> Dict[str, Any]:
        """Processa um único lote de forma assíncrona"""
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            None, 
            JSONValidator.validate_clients_batch, 
            batch
        )

