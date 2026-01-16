#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息服务类
负责处理微信消息和响应
"""

import logging
from wechatpy import parse_message
from wechatpy.utils import check_signature
from wechatpy.replies import create_reply
from wechatpy.exceptions import InvalidSignatureException
from src.services.game_service import GameService
from src.messages import HELP_MESSAGES
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
        try:
            # 解析消息
            msg = parse_message(xml_data)
            
            # 根据消息类型处理
            if msg.type == 'text':
                response_content = self._handle_text_message(msg.from_user_id, msg.content)
            elif msg.type == 'event':
                response_content = self._handle_event_message(msg.from_user_id, msg.event)
            else:
                response_content = HELP_MESSAGES["INSTRUCTIONS"]
            
            # 构造响应
            reply = create_reply(response_content, msg)
            return reply.render()
            
        except Exception as e:
            logger.error(f"处理微信消息异常: {e}", exc_info=True)
            # 如果解析失败，尝试构建一个通用的错误回复（这需要 msg 对象，如果解析失败可能拿不到）
            # 在 SDK 下如果不解析成功，通常很难回复特定的用户，但我们可以回退到手动 XML 或者返回空
            return "抱歉，服务器异常，请稍后重试"
    
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
