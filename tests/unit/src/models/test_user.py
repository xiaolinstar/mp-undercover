#!/usr/bin/env python3
"""
用户模型单元测试
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest

from src.models.user import User


class TestUserModel:
    """用户模型测试类"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User(
            openid="user1",
            nickname="玩家1"
        )
        
        assert user.openid == "user1"
        assert user.nickname == "玩家1"
        assert user.current_room is None
    
    def test_user_with_room(self):
        """测试带房间的用户创建"""
        user = User(
            openid="user1",
            nickname="玩家1",
            current_room="1234"
        )
        
        assert user.openid == "user1"
        assert user.nickname == "玩家1"
        assert user.current_room == "1234"
    
    def test_user_to_dict(self):
        """测试用户转字典"""
        user = User(
            openid="user1",
            nickname="玩家1",
            current_room="1234"
        )
        
        user_dict = user.to_dict()
        
        assert user_dict['openid'] == "user1"
        assert user_dict['nickname'] == "玩家1"
        assert user_dict['current_room'] == "1234"
    
    def test_user_from_dict(self):
        """测试从字典创建用户"""
        user_data = {
            'openid': 'user1',
            'nickname': '玩家1',
            'current_room': '1234'
        }
        
        user = User.from_dict(user_data)
        
        assert user.openid == "user1"
        assert user.nickname == "玩家1"
        assert user.current_room == "1234"
    
    def test_join_room(self):
        """测试加入房间"""
        user = User(
            openid="user1",
            nickname="玩家1"
        )
        
        assert user.has_joined_room() is False
        
        user.join_room("1234")
        assert user.current_room == "1234"
        assert user.has_joined_room() is True
    
    def test_leave_room(self):
        """测试离开房间"""
        user = User(
            openid="user1",
            nickname="玩家1",
            current_room="1234"
        )
        
        assert user.has_joined_room() is True
        
        user.leave_room()
        assert user.current_room is None
        assert user.has_joined_room() is False


if __name__ == "__main__":
    pytest.main(["-v", __file__])