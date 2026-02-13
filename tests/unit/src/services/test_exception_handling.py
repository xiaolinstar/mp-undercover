#!/usr/bin/env python3
"""
异常处理单元测试
测试各种业务异常的处理和全局异常处理器
"""

import os
import sys
from unittest.mock import Mock

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from src.exceptions import InvalidCommandError  # Client Exceptions
from src.models.room import Room, RoomStatus
from src.models.user import User
from src.services.game_service import GameService


class TestGameServiceExceptions:
    """测试游戏服务中的各种异常情况"""

    @pytest.fixture
    def mock_repos(self):
        """创建模拟的仓储对象"""
        room_repo = Mock()
        user_repo = Mock()
        return room_repo, user_repo

    @pytest.fixture
    def game_service(self, mock_repos):
        """创建游戏服务实例"""
        room_repo, user_repo = mock_repos
        return GameService(room_repo, user_repo)

    def test_user_not_in_room_exception(self, game_service, mock_repos):
        """测试用户不在房间的异常"""
        room_repo, user_repo = mock_repos
        
        # 模拟用户不在房间中
        user_repo.get.return_value = User(openid="user1", nickname="玩家1", current_room=None)
        
        # 调用需要用户在房间中的方法
        success, result = game_service.show_word("user1")
        
        # 验证返回了预期的错误信息
        assert success is False
        assert "尚未加入任何房间" in result

    def test_room_not_found_exception(self, game_service, mock_repos):
        """测试房间不存在的异常"""
        room_repo, user_repo = mock_repos
        
        # 模拟房间不存在
        room_repo.get.return_value = None
        
        # 创建用户
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        user_repo.get.return_value = user
        
        # 尝试执行需要房间的操作
        success, result = game_service.show_word("user1")
        
        assert success is False
        assert "房间" in result and "不存在" in result

    def test_game_not_started_exception(self, game_service, mock_repos):
        """测试游戏未开始的异常"""
        room_repo, user_repo = mock_repos
        
        # 创建用户和房间
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1"])
        room.status = RoomStatus.WAITING  # 游戏未开始
        
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 尝试执行游戏中才能执行的操作
        success, result = game_service.show_word("user1")
        
        assert success is False
        assert "游戏尚未开始" in result

    def test_game_already_started_exception(self, game_service, mock_repos):
        """测试尝试重复开始游戏的异常"""
        room_repo, user_repo = mock_repos
        
        # 创建用户和已开始的房间
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2", "user3"])
        room.status = RoomStatus.PLAYING  # 游戏已开始
        
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 尝试再次开始游戏
        success, result = game_service.start_game("user1")
        
        assert success is False
        assert "游戏已经开始了" in result

    def test_insufficient_players_exception(self, game_service, mock_repos):
        """测试玩家数量不足的异常"""
        room_repo, user_repo = mock_repos
        
        # 创建用户和只有2人的房间（少于最低玩家数）
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2"])  # 只有2人
        room.status = RoomStatus.WAITING  # 游戏未开始
        
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 尝试开始游戏（需要至少3人）
        success, result = game_service.start_game("user1")
        
        assert success is False
        assert "人数不足以开启游戏" in result

    def test_room_permission_error(self, game_service, mock_repos):
        """测试权限错误异常"""
        room_repo, user_repo = mock_repos
        
        # 创建用户和房间，但user2不是房主
        user = User(openid="user2", nickname="玩家2", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2", "user3"])
        room.status = RoomStatus.WAITING
        
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 非房主尝试开始游戏
        success, result = game_service.start_game("user2")
        
        assert success is False
        assert "只有房主可以进行" in result

    def test_player_eliminated_error(self, game_service, mock_repos):
        """测试玩家已被淘汰的异常"""
        room_repo, user_repo = mock_repos
        
        # 创建用户和房间，用户已被淘汰
        user = User(openid="user2", nickname="玩家2", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2", "user3"])
        room.status = RoomStatus.PLAYING
        room.eliminated = ["user2"]  # user2已被淘汰
        room.words = {'civilian': '苹果', 'undercover': '香蕉'}
        
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 已淘汰的玩家尝试查看词语
        success, result = game_service.show_word("user2")
        
        assert success is False
        assert "您已被淘汰" in result

    def test_invalid_player_index_error(self, game_service, mock_repos):
        """测试无效玩家索引的异常"""
        room_repo, user_repo = mock_repos
        
        # 创建用户和房间
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2", "user3"])
        room.status = RoomStatus.PLAYING
        room.words = {'civilian': '苹果', 'undercover': '香蕉'}
        
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 使用超出范围的索引进行投票
        success, result = game_service.vote_player("user1", 10)  # 索引10不存在
        
        assert success is False
        assert "无效的玩家序号" in result

    def test_room_full_error(self, game_service, mock_repos):
        """测试房间已满的异常"""
        room_repo, user_repo = mock_repos
        
        from src.config.game_config import GameConfig
        
        # 创建一个已经有最大玩家数量的房间，确保不包含要加入的用户
        players_list = [f"user{i}" for i in range(1, GameConfig.MAX_PLAYERS + 1)]
        room = Room(room_id="1234", creator="user1", players=players_list)
        room.status = RoomStatus.WAITING
        
        # 确保用户repo返回当前用户不在任何房间
        def mock_get(user_id):
            if user_id == "user50":
                return User(openid="user50", nickname="玩家50", current_room=None)
            else:
                # 为房间中的其他玩家返回适当用户对象
                return User(openid=user_id, nickname=f"玩家{user_id}", current_room="1234")
        
        user_repo.get.side_effect = mock_get
        room_repo.get.return_value = room
        
        # 尝试加入已满的房间
        success, result = game_service.join_room("user50", "1234")
        
        assert success is False
        assert "该房间已满" in result

    def test_user_already_in_room_error(self, game_service, mock_repos):
        """测试用户已在房间中的异常"""
        room_repo, user_repo = mock_repos
        
        # 用户已经在当前房间中
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2"])
        room.status = RoomStatus.WAITING
        
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 尝试加入同一个房间
        success, result = game_service.join_room("user1", "1234")
        
        assert success is False
        assert "您已在其他房间中" in result or "已在房间中" in result


class TestGlobalExceptionHandler:
    """测试全局异常处理器的行为"""
    
    def test_server_exception_handling(self):
        """测试服务器异常的处理"""
        # 这个测试需要启动Flask应用来验证全局异常处理器
        # 由于这不是单元测试而是集成测试，我们会验证异常类的定义
        from src.exceptions.server import RedisConnectionError
        
        try:
            raise RedisConnectionError(operation="test_operation")
        except RedisConnectionError as e:
            assert e.message == "系统数据连接失败"
            assert e.error_code == "SYS-CONN-001"
            assert e.details['operation'] == "test_operation"
    
    def test_client_exception_handling(self):
        """测试客户端异常的处理"""
        try:
            raise InvalidCommandError(command="invalid_cmd")
        except InvalidCommandError as e:
            assert "无法识别该指令" in e.message
            assert e.error_code == "CLIENT-CMD-003"
            assert e.details['command'] == "invalid_cmd"


if __name__ == "__main__":
    pytest.main(["-v", __file__])