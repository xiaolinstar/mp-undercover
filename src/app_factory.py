#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用工厂
负责创建和配置Flask应用
"""

import os
import redis
from flask import Flask
from src.repositories.room_repository import RoomRepository
from src.repositories.user_repository import UserRepository
from src.services.game_service import GameService
from src.services.message_service import MessageService
from src.services.wechat_client import WeChatClient
from src.services.push_service import PushService


class AppFactory:
    """应用工厂类"""
    
    @staticmethod
    def create_app() -> Flask:
        """创建Flask应用"""
        app = Flask(__name__)
        
        # 配置应用
        AppFactory._configure_app(app)
        
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
    def _configure_app(app: Flask) -> None:
        """配置应用"""
        # 从环境变量获取配置
        app.config['WECHAT_TOKEN'] = os.environ.get('WECHAT_TOKEN', 'your_token_here')
        app.config['WECHAT_APP_ID'] = os.environ.get('WECHAT_APP_ID', 'your_app_id_here')
        app.config['WECHAT_APP_SECRET'] = os.environ.get('WECHAT_APP_SECRET', 'your_app_secret_here')
        app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
        app.config['ENABLE_WECHAT_PUSH'] = os.environ.get('ENABLE_WECHAT_PUSH', 'False')
        
        # 配置密钥
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    @staticmethod
    def _init_services(app: Flask) -> tuple:
        """初始化服务"""
        # 创建Redis客户端 - 使用redis.Redis()而不是redis.from_url()
        redis_client = redis.Redis.from_url(app.config['REDIS_URL'])
        
        # 创建仓储
        room_repo = RoomRepository(redis_client)
        user_repo = UserRepository(redis_client)
        
        # 创建服务
        client = None
        push_service = None
        if app.config['ENABLE_WECHAT_PUSH'] in ('1', 'true', 'True'):
            client = WeChatClient(app.config['WECHAT_APP_ID'], app.config['WECHAT_APP_SECRET'])
            push_service = PushService(client)
        game_service = GameService(room_repo, user_repo, push_service)
        message_service = MessageService(game_service, app.config['WECHAT_TOKEN'])
        
        return room_repo, user_repo, game_service, message_service
    
    @staticmethod
    def _register_routes(app: Flask, message_service: MessageService) -> None:
        """注册路由"""
        from flask import request, Response
        import time
        
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
            """健康检查接口"""
            return {'status': 'healthy', 'timestamp': int(time.time())}
