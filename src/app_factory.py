#!/usr/bin/env python3
"""
应用工厂
负责创建和配置Flask应用
"""

import redis
from flask import Flask

from src.config.settings import settings
from src.repositories.room_repository import RoomRepository
from src.repositories.user_repository import UserRepository
from src.services.game_service import GameService
from src.services.message_service import MessageService
from src.services.push_service import PushService
from src.services.wechat_client import WeChatClient
from src.utils.logger import setup_logger


class AppFactory:
    """应用工厂类"""
    
    @staticmethod
    def create_app() -> Flask:
        """创建Flask应用"""
        app = Flask(__name__)
        
        # 配置日志
        app.logger = setup_logger(app.name)
        app.logger.info(f"Application starting in {settings.APP_ENV} mode")
        
        # 配置应用
        app.config.from_object(settings)
        
        # 生产环境校验
        if settings.APP_ENV == 'prod':
            AppFactory._validate_prod_config(app)
        
        # 初始化服务
        room_repo, user_repo, game_service, message_service = AppFactory._init_services(app)
        
        # 注册路由
        AppFactory._register_routes(app, message_service)
        
        # 将服务存储在应用上下文中
        app.room_repo = room_repo
        app.user_repo = user_repo
        app.game_service = game_service
        app.message_service = message_service
        
        return app
    
    @staticmethod
    def _validate_prod_config(app: Flask) -> None:
        """校验生产环境配置是否安全（非默认值）"""
        critical_configs = {
            'WECHAT_TOKEN': ['', 'your_token_here'],
            'WECHAT_APP_ID': ['', 'your_app_id_here'],
            'WECHAT_APP_SECRET': ['', 'your_app_secret_here'],
            'SECRET_KEY': ['default-secret-key', 'your-secret-key-here']
        }
        
        missing_or_default = []
        for key, defaults in critical_configs.items():
            val = app.config.get(key)
            if not val or val in defaults:
                missing_or_default.append(key)
        
        if missing_or_default:
            missing_str = ", ".join(missing_or_default)
            error_msg = (
                "Production environment security check failed! "
                f"The following configs are missing or using defaults: {missing_str}"
            )
            app.logger.error(error_msg)
            # 在生产环境下，配置不安全应该拒绝启动
            raise ValueError(error_msg)
        
        app.logger.info("Production environment security check passed.")
    
    @staticmethod
    def _init_services(app: Flask) -> tuple:
        """初始化服务"""
        # 创建Redis客户端
        if app.config.get('TESTING'):
            import fakeredis
            redis_client = fakeredis.FakeRedis(decode_responses=False)
            app.logger.info("Using fakeredis for testing")
        else:
            redis_client = redis.Redis.from_url(app.config['REDIS_URL'])
        
        # 创建仓储
        room_repo = RoomRepository(redis_client)
        user_repo = UserRepository(redis_client)
        
        # 创建服务
        client = None
        push_service = None
        # Pydantic settings will have boolean logic already applied if using bool type
        # But app.config might hold the value. If from_object copied it, it's boolean.
        # Verify: app.config['ENABLE_WECHAT_PUSH'] will be bool True/False from settings
        if app.config.get('ENABLE_WECHAT_PUSH'):
            client = WeChatClient(
                app.config['WECHAT_APP_ID'], 
                app.config['WECHAT_APP_SECRET'],
                redis_client=redis_client
            )
            push_service = PushService(client)
        game_service = GameService(room_repo, user_repo, push_service)
        message_service = MessageService(game_service, app.config['WECHAT_TOKEN'])
        
        return room_repo, user_repo, game_service, message_service
    
    @staticmethod
    def _register_routes(app: Flask, message_service: MessageService) -> None:
        """注册路由"""
        import time

        from flask import Response, request
        
        @app.route('/', methods=['GET', 'POST'])
        def wechat():
            if request.method == 'GET':
                # 微信验证接口
                signature = request.args.get('signature', '')
                timestamp = request.args.get('timestamp', '')
                nonce = request.args.get('nonce', '')
                echostr = request.args.get('echostr', '')
                
                if message_service.verify_wechat_signature(signature, timestamp, nonce):
                    return echostr
                else:
                    return '验证失败', 400
            else:
                # 微信消息处理接口
                xml_data = request.data.decode('utf-8')
                response_xml = message_service.handle_wechat_message(xml_data)
                return Response(response_xml, mimetype='application/xml')
        
        @app.route('/health')
        def health_check():
            """健康检查接口，可用于kube-probe"""
            return {'status': 'healthy', 'timestamp': int(time.time())}
