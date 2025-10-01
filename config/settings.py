"""
配置管理模块
集中管理应用的所有配置项和环境变量
"""
import os
import secrets
from dotenv import load_dotenv
from .constants import (
    DEFAULT_MAX_FILE_SIZE, DEFAULT_PORT, DEFAULT_HOST, 
    DEFAULT_UPLOAD_FOLDER, DEFAULT_LOG_LEVEL, DEFAULT_LOG_FILE,
    ERROR_MESSAGES
)

# 加载环境变量
load_dotenv()


class Config:
    """基础配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', DEFAULT_MAX_FILE_SIZE))
    
    # Dify API配置
    DIFY_API_BASE_URL = os.environ.get('DIFY_API_BASE_URL', 'http://localhost/v1')
    DIFY_API_TOKEN = os.environ.get('DIFY_API_TOKEN')
    
    # 应用配置
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', DEFAULT_PORT))
    HOST = os.environ.get('HOST', DEFAULT_HOST)
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', DEFAULT_UPLOAD_FOLDER)
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', DEFAULT_LOG_LEVEL)
    LOG_FILE = os.environ.get('LOG_FILE', DEFAULT_LOG_FILE)
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # 安全配置
    CSRF_ENABLED = os.environ.get('CSRF_ENABLED', 'True').lower() == 'true'
    
    @classmethod
    def validate_required_config(cls):
        """验证必需的配置项"""
        if not cls.DIFY_API_TOKEN:
            raise ValueError(ERROR_MESSAGES['MISSING_DIFY_TOKEN'])
    
    @classmethod
    def get_max_file_size_mb(cls):
        """获取最大文件大小（MB）"""
        return cls.MAX_CONTENT_LENGTH // (1024 * 1024)
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        directories = [
            cls.UPLOAD_FOLDER,
            os.path.dirname(cls.LOG_FILE) if os.path.dirname(cls.LOG_FILE) else 'logs'
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    # 测试时使用内存数据库等


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    获取配置对象
    
    Args:
        config_name: 配置名称，如果为None则从环境变量FLASK_ENV获取
        
    Returns:
        Config: 配置对象
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    config_class = config_map.get(config_name, DevelopmentConfig)
    
    # 验证配置
    config_class.validate_required_config()
    
    # 确保目录存在
    config_class.ensure_directories()
    
    return config_class