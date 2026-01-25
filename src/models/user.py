#!/usr/bin/env python3
"""
用户模型类
定义用户的数据结构和相关操作
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class User:
    """用户模型"""
    openid: str
    nickname: str = ""
    current_room: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式，用于存储到Redis"""
        return {
            'openid': self.openid,
            'nickname': self.nickname,
            'current_room': self.current_room
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'User':
        """从字典数据创建用户实例"""
        return cls(
            openid=data.get('openid', ''),
            nickname=data.get('nickname', ''),
            current_room=data.get('current_room')
        )
    
    def join_room(self, room_id: str) -> None:
        """加入房间"""
        self.current_room = room_id
    
    def leave_room(self) -> None:
        """离开房间"""
        self.current_room = None
    
    def has_joined_room(self) -> bool:
        """检查是否已加入房间"""
        return self.current_room is not None