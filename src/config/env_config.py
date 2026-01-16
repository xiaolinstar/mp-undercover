import os

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', '')
    WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', '')
    WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET', '')
    ENABLE_WECHAT_PUSH = os.environ.get('ENABLE_WECHAT_PUSH', 'False').lower() in ('true', '1', 't')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    APP_ENV = os.environ.get('APP_ENV', 'dev')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    # 测试环境下通常使用内存数据库，逻辑将在 app_factory 中处理
    REDIS_URL = 'redis://localhost:6379/1' # 备用，实际会用 fakeredis

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境通常需要通过 K8s Secret 或环境变量强制提供敏感信息
    
config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}
