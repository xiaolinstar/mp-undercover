#!/usr/bin/env python3
"""
消息服务类
负责处理微信消息和响应
"""

import logging

from wechatpy import parse_message
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.replies import create_reply
from wechatpy.utils import check_signature

from src.config.messages import HELP_MESSAGES
from src.services.game_service import GameService
from src.strategies.commands import CommandRouter

logger = logging.getLogger(__name__)

class MessageService:
    """消息服务类"""
    
    def __init__(self, game_service: GameService, token: str):
        self.game_service = game_service
        self.token = token
        self.router = CommandRouter(game_service)
    
    def verify_wechat_signature(self, signature: str, timestamp: str, nonce: str) -> bool:
        """验证微信签名"""
        try:
            check_signature(self.token, signature, timestamp, nonce)
            return True
        except InvalidSignatureException:
            return False
    
    def handle_wechat_message(self, xml_data: str) -> str:
        """处理微信消息"""
        # 解析消息
        msg = parse_message(xml_data)
        
        # 检查消息是否成功解析
        if msg is None:
            logger.warning("未能解析微信消息，XML数据为空或格式不正确")
            return "抱歉，无法解析您的消息"
        
        logger.info(f"解析微信消息: 类型={msg.type}, 用户={msg.source}")
        
        # 根据消息类型处理
        if msg.type == 'text':
            response_content = self._handle_text_message(msg.source, msg.content)
        elif msg.type == 'event':
            response_content = self._handle_event_message(msg.source, msg.event)
        else:
            response_content = HELP_MESSAGES["INSTRUCTIONS"]
        
        # 构造响应
        reply = create_reply(response_content, msg)
        return reply.render()
    
    def _handle_text_message(self, user_id: str, content: str) -> str:
        """处理文本消息"""
        content = content.strip().lower()
        return self.router.route(user_id, content)

    def _handle_event_message(self, user_id: str, event: str) -> str:
        """处理事件消息"""
        if event == "subscribe":
            logger.info(f"用户 {user_id} 关注")
            return HELP_MESSAGES["WELCOME"]
        else:
            return HELP_MESSAGES["INSTRUCTIONS"]
