"""
Configuration settings for Hindi to Santali Translator
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Flask Server
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5000
    
    # Translation Configuration
    SOURCE_LANGUAGE = 'hi'  # Hindi
    TARGET_LANGUAGE = 'sat'  # Santali
    
    # Model Configuration
    USE_PRETRAINED_MODEL = True
    MODEL_NAME = 'Helsinki-NLP/Opus-MT-hi-en'  # Pretrained model for Hindi
    
    # Dictionary Configuration
    DICTIONARY_PATH = 'data/dictionary.csv'
    ENABLE_DICTIONARY_LOOKUP = True
    
    # API Configuration
    API_BASE_URL = '/api'
    API_TIMEOUT = 30
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/translator.log'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Config mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
