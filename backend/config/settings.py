"""
Configurações centralizadas do sistema de cobrança
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base do sistema"""
    
    # Configurações da aplicação
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 8000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Configurações do JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 dias
    
    # Configurações da Waha
    WAHA_BASE_URL = os.getenv('WAHA_BASE_URL', 'http://localhost:3000')
    WAHA_API_KEY = os.getenv('WAHA_API_KEY')
    WAHA_SESSION_NAME = os.getenv('WAHA_SESSION_NAME', 'default')
    WAHA_WEBHOOK_URL = os.getenv('WAHA_WEBHOOK_URL')
    
    # Configurações de segurança
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 3600))
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # 🤖 CONFIGURAÇÕES DO MODELO SUPREMO
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/chatbot_model.pth')
    MODEL_CACHE_SIZE = int(os.getenv('MODEL_CACHE_SIZE', 100))
    MODEL_MAX_LENGTH = int(os.getenv('MODEL_MAX_LENGTH', 512))
    MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', 0.7))
    MODEL_DEVICE = 'cuda' if os.getenv('USE_GPU', 'False').lower() == 'true' else 'cpu'
    
    # 🧠 IA AVANÇADA
    ENABLE_EMOTIONAL_INTELLIGENCE = os.getenv('ENABLE_EMOTIONAL_INTELLIGENCE', 'True').lower() == 'true'
    ENABLE_MEMORY_SYSTEM = os.getenv('ENABLE_MEMORY_SYSTEM', 'True').lower() == 'true'
    ENABLE_SEMANTIC_ANALYSIS = os.getenv('ENABLE_SEMANTIC_ANALYSIS', 'True').lower() == 'true'
    ENABLE_CONTINUOUS_LEARNING = os.getenv('ENABLE_CONTINUOUS_LEARNING', 'True').lower() == 'true'
    
    # 💾 SISTEMA DE MEMÓRIA
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', 50))
    MAX_EMOTIONAL_TIMELINE = int(os.getenv('MAX_EMOTIONAL_TIMELINE', 20))
    MEMORY_PERSISTENCE = os.getenv('MEMORY_PERSISTENCE', 'True').lower() == 'true'
    
    # 🎯 CLASSIFICAÇÃO SUPREMA
    INTENT_CONFIDENCE_THRESHOLD = float(os.getenv('INTENT_CONFIDENCE_THRESHOLD', 0.6))
    EMOTIONAL_INTENSITY_THRESHOLD = float(os.getenv('EMOTIONAL_INTENSITY_THRESHOLD', 0.5))
    SEMANTIC_SIMILARITY_THRESHOLD = float(os.getenv('SEMANTIC_SIMILARITY_THRESHOLD', 0.7))
    
    # 🚀 PERFORMANCE SUPREMA
    BATCH_PROCESSING = os.getenv('BATCH_PROCESSING', 'True').lower() == 'true'
    ASYNC_PROCESSING = os.getenv('ASYNC_PROCESSING', 'True').lower() == 'true'
    CACHE_EMBEDDINGS = os.getenv('CACHE_EMBEDDINGS', 'True').lower() == 'true'
    
    # Configurações de arquivo
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/uploads')
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'json,txt,csv').split(',')
    
    # Configurações de banco de dados (opcional)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/app.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Configurações de monitoramento
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'True').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', 9090))
    
    # Caminhos de arquivos importantes
    CLIENTS_JSON_PATH = 'data/clients.json'
    TEMPLATES_PATH = 'data/templates/message_templates.json'
    CONVERSATIONS_LOG_PATH = 'data/conversations.log'
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Valida configurações críticas e retorna status"""
        issues = []
        
        # Verifica configurações obrigatórias para produção
        if not cls.DEBUG:
            if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
                issues.append("SECRET_KEY deve ser alterada em produção")
            
            if not cls.WAHA_API_KEY:
                issues.append("WAHA_API_KEY é obrigatória")
                
            if not cls.WAHA_WEBHOOK_URL:
                issues.append("WAHA_WEBHOOK_URL é obrigatória")
        
        # Verifica se diretórios existem
        import os
        directories = ['data', 'logs', 'models', cls.UPLOAD_FOLDER]
        for directory in directories:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    issues.append(f"Não foi possível criar diretório {directory}: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "debug_mode": cls.DEBUG,
            "waha_configured": bool(cls.WAHA_API_KEY and cls.WAHA_WEBHOOK_URL)
        }

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    DATABASE_URL = 'sqlite:///:memory:'

# Configuração ativa baseada na variável de ambiente
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

active_config = config_map.get(os.getenv('FLASK_ENV', 'development'), DevelopmentConfig)
