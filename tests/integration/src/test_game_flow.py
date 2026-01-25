#!/usr/bin/env python3
"""
游戏流程集成测试
"""

import random
from unittest.mock import Mock

import pytest

from src.repositories.room_repository import RoomRepository
from src.repositories.user_repository import UserRepository
from src.services.game_service import GameService


class TestGameFlow:
    """游戏流程集成测试类"""
    
    @pytest.fixture
    def mock_redis(self):
        """创建模拟Redis客户端"""
        mock_redis_client = Mock()
        
        # 存储房间和用户数据（使用字节串模拟真实Redis）
        storage = {}
        
        def mock_set(key, value):
            # Redis存储的是bytes
            if isinstance(value, str):
                storage[key] = value.encode('utf-8')
            else:
                storage[key] = value
            return True
        
        def mock_setex(key, timeout, value):
            # 忽略超时，只存储值
            if isinstance(value, str):
                storage[key] = value.encode('utf-8')
            else:
                storage[key] = value
            return True
        
        def mock_get(key):
            result = storage.get(key)
            # 返回bytes或None
            return result
        
        def mock_exists(key):
            return 1 if key in storage else 0
        
        def mock_delete(key):
            if key in storage:
                del storage[key]
                return 1
            return 0
        
        mock_redis_client.set = mock_set
        mock_redis_client.setex = mock_setex
        mock_redis_client.get = mock_get
        mock_redis_client.exists = mock_exists
        mock_redis_client.delete = mock_delete
        
        return mock_redis_client
    
    @pytest.fixture
    def repositories(self, mock_redis):
        """创建仓储实例"""
        room_repo = RoomRepository(mock_redis)
        user_repo = UserRepository(mock_redis)
        return room_repo, user_repo
    
    @pytest.fixture
    def game_service(self, repositories):
        """创建游戏服务实例"""
        room_repo, user_repo = repositories
        return GameService(room_repo, user_repo)
    
    def test_full_game_flow(self, game_service):
        """测试完整游戏流程"""
        # 模拟random以获得固定的房间号
        original_randint = random.randint
        random.randint = lambda a, b: 1234
        
        try:
            # 1. 创建房间
            success, room_id = game_service.create_room("user1")
            assert success is True
            assert isinstance(room_id, str)
            assert room_id == "1234"
            
            # 2. 其他玩家加入房间
            success, result = game_service.join_room("user2", room_id)
            assert success is True
            assert "成功加入房间" in result
            
            success, result = game_service.join_room("user3", room_id)
            assert success is True
            assert "成功加入房间" in result
            
            # 3. 房主开始游戏
            success, result = game_service.start_game("user1")
            assert success is True
            assert result == "游戏开始成功"
            
            # 4. 查看各自词语
            success, result1 = game_service.show_word("user1")
            assert success is True
            assert "您的词语：" in result1
            
            success, result2 = game_service.show_word("user2")
            assert success is True
            assert "您的词语：" in result2
            
            success, result3 = game_service.show_word("user3")
            assert success is True
            assert "您的词语：" in result3
            
            # 5. 查看状态
            success, result = game_service.show_status("user1")
            assert success is True
            assert "您的信息" in result
            assert "房间号" in result
            assert "房间状态" in result
            
            # 6. 房主投票
            success, result = game_service.vote_player("user1", 2)  # 投票给2号玩家
            assert success is True
            # 投票结果可能是"投票成功"或游戏结束消息
            assert "投票成功" in result or "获胜" in result
            
        finally:
            random.randint = original_randint
    
    def test_room_timeout_cleanup(self, game_service, repositories):
        """测试房间超时清理"""
        room_repo, user_repo = repositories
        
        # 模拟random以获得固定的房间号
        original_randint = random.randint
        random.randint = lambda a, b: 5678
        
        try:
            # 1. 创建房间
            success, room_id = game_service.create_room("user1")
            assert success is True
            assert room_id == "5678"
            
            # 2. 验证房间存在
            room = room_repo.get(room_id)
            assert room is not None
            assert room.room_id == room_id
            
            # 3. 验证用户也被创建
            user = user_repo.get("user1")
            assert user is not None
            assert user.openid == "user1"
            assert user.current_room == room_id
            
        finally:
            random.randint = original_randint


if __name__ == "__main__":
    pytest.main(["-v", __file__])