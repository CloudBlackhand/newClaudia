"""
Configurações do Sistema - Otimizado para Railway
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações centralizadas do sistema"""
    
    # Configurações básicas
    app_name: str = Field(default="Sistema de Cobrança Avançado", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Configurações de servidor
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Configurações do Waha
    waha_base_url: str = Field(default="", env="WAHA_BASE_URL")
    waha_api_key: Optional[str] = Field(default=None, env="WAHA_API_KEY")
    waha_session: str = Field(default="default", env="WAHA_SESSION")
    
    # Configurações de segurança
    secret_key: str = Field(default="sua-chave-secreta-super-segura", env="SECRET_KEY")
    webhook_secret: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    
    # Configurações de logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Configurações de performance
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    batch_size: int = Field(default=50, env="BATCH_SIZE")
    
    # Configurações de templates
    default_billing_template: str = Field(
        default="""
🔔 *Lembrete de Pagamento*

Olá {nome}!

Identificamos que há uma pendência em sua conta:
💰 Valor: R$ {valor}
📅 Vencimento: {vencimento}
📋 Descrição: {descricao}

Para regularizar sua situação, por favor realize o pagamento o quanto antes.

Se já efetuou o pagamento, desconsidere esta mensagem.

Qualquer dúvida, estou aqui para ajudar! 😊
        """.strip(),
        env="DEFAULT_BILLING_TEMPLATE"
    )
    
    # Configurações de arquivos
    json_upload_path: str = Field(default="uploads/", env="JSON_UPLOAD_PATH")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Criar diretórios necessários
        os.makedirs(self.json_upload_path, exist_ok=True)
        os.makedirs("logs", exist_ok=True)

# Instância global das configurações
settings = Settings()
