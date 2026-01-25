#!/usr/bin/env python3
"""
房间模型单元测试
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import time
from datetime import datetime

import pytest

from src.models.room import Room, RoomStatus


class TestRoomModel:
    """房间模型测试类"""
    
    def test_room_creation(self):
        """测试房间创建"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        
        assert room.room_id == "1234"
        assert room.creator == "user1"
        assert room.players == ["user1"]
        assert room.status == RoomStatus.WAITING
        assert room.words is None
        assert room.undercovers == []
        assert room.current_round == 1
        assert room.eliminated == []
        assert isinstance(room.created_at, datetime)
        assert isinstance(room.last_active, datetime)
    
    def test_room_to_dict(self):
        """测试房间转字典"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        
        room_dict = room.to_dict()
        
        assert room_dict['room_id'] == "1234"
        assert room_dict['creator'] == "user1"
        assert room_dict['status'] == "waiting"
        assert 'created_at' in room_dict
        assert 'last_active' in room_dict
    
    def test_room_from_dict(self):
        """测试从字典创建房间"""
        room_data = {
            'room_id': '1234',
            'creator': 'user1',
            'players': ['user1', 'user2'],
            'status': 'playing',
            'words': {'civilian': '苹果', 'undercover': '香蕉'},
            'undercovers': ['user2'],
            'current_round': 2,
            'eliminated': [],
            'created_at': '2023-01-01T00:00:00+00:00',
            'last_active': '2023-01-01T00:00:00+00:00'
        }
        
        room = Room.from_dict(room_data)
        
        assert room.room_id == "1234"
        assert room.creator == "user1"
        assert room.players == ["user1", "user2"]
        assert room.status == RoomStatus.PLAYING
        assert room.words == {'civilian': '苹果', 'undercover': '香蕉'}
        assert room.undercovers == ["user2"]
        assert room.current_round == 2
        assert room.eliminated == []
    
    def test_is_creator(self):
        """测试房主检查"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        
        assert room.is_creator("user1") is True
        assert room.is_creator("user2") is False
    
    def test_is_player(self):
        """测试玩家检查"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        room.players.extend(["user2", "user3"])
        
        assert room.is_player("user1") is True
        assert room.is_player("user2") is True
        assert room.is_player("user4") is False
    
    def test_is_eliminated(self):
        """测试淘汰检查"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        room.eliminated.append("user2")
        
        assert room.is_eliminated("user2") is True
        assert room.is_eliminated("user1") is False
    
    def test_get_player_count(self):
        """测试获取玩家数量"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        room.players.extend(["user2", "user3"])
        
        assert room.get_player_count() == 3
    
    def test_get_remaining_players(self):
        """测试获取剩余玩家"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        room.players.extend(["user2", "user3", "user4"])
        room.eliminated.extend(["user2", "user3"])
        
        remaining = room.get_remaining_players()
        assert len(remaining) == 2
        assert "user1" in remaining
        assert "user4" in remaining
    
    def test_update_last_active(self):
        """测试更新最后活跃时间"""
        room = Room(
            room_id="1234",
            creator="user1"
        )
        
        old_time = room.last_active
        # 等待一小段时间确保时间不同
        time.sleep(0.001)
        room.update_last_active()
        
        assert room.last_active > old_time


if __name__ == "__main__":
    pytest.main(["-v", __file__])