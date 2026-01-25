#!/usr/bin/env python3
"""
房间模型类
定义房间的数据结构和相关操作
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class RoomStatus(Enum):
    """房间状态枚举"""
    WAITING = "waiting"    # 等待中
    PLAYING = "playing"    # 游戏中
    ENDED = "ended"        # 已结束


@dataclass
class Room:
    """房间模型"""
    room_id: str
    creator: str
    players: list[str] = field(default_factory=list)
    status: RoomStatus = RoomStatus.WAITING
    words: dict[str, str] | None = None
    undercovers: list[str] = field(default_factory=list)
    current_round: int = 1
    eliminated: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_active: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        """初始化后自动将创建者添加到玩家列表"""
        if not self.players:
            self.players = [self.creator]
        elif self.creator not in self.players:
            self.players.insert(0, self.creator)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式，用于存储到Redis"""
        return {
            'room_id': self.room_id,
            'creator': self.creator,
            'players': self.players,
            'status': self.status.value,
            'words': self.words,
            'undercovers': self.undercovers,
            'current_round': self.current_round,
            'eliminated': self.eliminated,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Room':
        """从字典数据创建房间实例"""
        # 处理枚举类型
        status = RoomStatus(data.get('status', 'waiting'))
        
        # 处理时间戳
        created_at = datetime.fromisoformat(data.get('created_at', datetime.now(UTC).isoformat()))
        last_active = datetime.fromisoformat(data.get('last_active', datetime.now(UTC).isoformat()))
        
        return cls(
            room_id=data.get('room_id', ''),
            creator=data.get('creator', ''),
            players=data.get('players', []),
            status=status,
            words=data.get('words'),
            undercovers=data.get('undercovers', []),
            current_round=data.get('current_round', 1),
            eliminated=data.get('eliminated', []),
            created_at=created_at,
            last_active=last_active
        )
    
    def is_creator(self, user_id: str) -> bool:
        """检查用户是否为房主"""
        return self.creator == user_id
    
    def is_player(self, user_id: str) -> bool:
        """检查用户是否在房间中"""
        return user_id in self.players
    
    def is_eliminated(self, user_id: str) -> bool:
        """检查玩家是否已被淘汰"""
        return user_id in self.eliminated
    
    def get_player_count(self) -> int:
        """获取房间玩家数量"""
        return len(self.players)
    
    def get_remaining_players(self) -> list[str]:
        """获取剩余玩家列表"""
        return [player for player in self.players if player not in self.eliminated]
    
    def update_last_active(self) -> None:
        """更新最后活跃时间"""
        self.last_active = datetime.now(UTC)