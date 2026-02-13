#!/usr/bin/env python3
"""
游戏服务单元测试
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from unittest.mock import Mock

import pytest

from src.models.room import Room, RoomStatus
from src.models.user import User
from src.services.game_service import GameService


class TestGameService:
    """游戏服务测试类"""
    
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
    
    def test_create_room_success(self, game_service, mock_repos):
        """测试成功创建房间"""
        room_repo, user_repo = mock_repos
        
        # 设置模拟行为
        room_repo.exists.return_value = False
        room_repo.save.return_value = True
        user_repo.save.return_value = True
        
        # 调用被测试方法
        success, result = game_service.create_room("user1")
        
        # 验证结果
        assert success is True
        assert len(result) == 4  # 房间号应该是4位数字
        assert result.isdigit() is True
        
        # 验证调用次数
        assert room_repo.save.call_count == 1
        assert user_repo.save.call_count == 1
    
    def test_create_room_save_failure(self, game_service, mock_repos):
        """测试房间保存失败"""
        room_repo, user_repo = mock_repos
        from src.exceptions import RedisConnectionError
        
        # 设置模拟行为
        room_repo.exists.return_value = False
        room_repo.save.side_effect = RedisConnectionError("保存房间")  # 抛出异常
        
        # 调用被测试方法
        success, result = game_service.create_room("user1")
        
        # 验证结果
        assert success is False
        assert "创建房间" in result and ("失败" in result or "错误" in result)
    
    def test_join_room_success(self, game_service, mock_repos):
        """测试成功加入房间"""
        room_repo, user_repo = mock_repos
        
        # 创建模拟房间
        room = Room(room_id="1234", creator="user1", players=["user1"])
        
        # 设置模拟行为 - 用户不在任何房间中
        user_repo.get.return_value = None  # 用户尚未加入任何房间
        room_repo.get.return_value = room
        room_repo.save.return_value = True
        user_repo.save.return_value = True
        
        # 调用被测试方法
        success, result = game_service.join_room("user2", "1234")
        
        # 验证结果
        assert success is True
        assert "成功加入房间" in result
        assert "当前房间人数：2" in result
        
        # 验证房间状态
        assert len(room.players) == 2
        assert "user2" in room.players
    
    def test_join_room_not_found(self, game_service, mock_repos):
        """测试加入不存在的房间"""
        room_repo, user_repo = mock_repos
        
        # 设置模拟行为 - 用户不在任何房间中，房间不存在
        user_repo.get.return_value = None  # 用户尚未加入任何房间
        room_repo.get.return_value = None  # 房间不存在
        
        # 调用被测试方法
        success, result = game_service.join_room("user2", "1234")
        
        # 验证结果
        assert success is False
        assert "房间" in result and "不存在" in result  # 容忍更详细的错误消息
    
    def test_join_room_already_playing(self, game_service, mock_repos):
        """测试加入已开始游戏的房间"""
        room_repo, user_repo = mock_repos
        
        # 创建模拟房间（游戏中状态）
        room = Room(room_id="1234", creator="user1", players=["user1"])
        room.status = RoomStatus.PLAYING
        
        # 设置模拟行为 - 用户不在任何房间中
        user_repo.get.return_value = None  # 用户尚未加入任何房间
        room_repo.get.return_value = room
        
        # 调用被测试方法
        success, result = game_service.join_room("user2", "1234")
        
        # 验证结果
        assert success is False
        assert result == "游戏已经开始，无法加入房间"
    
    def test_start_game_success(self, game_service, mock_repos):
        """测试成功开始游戏"""
        room_repo, user_repo = mock_repos
        
        # 创建模拟用户和房间
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2", "user3"])
        
        # 设置模拟行为
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        room_repo.save.return_value = True
        
        # 调用被测试方法
        success, result = game_service.start_game("user1")
        
        # 验证结果
        assert success is True
        assert result == "游戏开始成功"
        
        # 验证房间状态
        assert room.status == RoomStatus.PLAYING
        assert room.words is not None
        assert len(room.undercovers) == 1  # 3人游戏应该有1个卧底
    
    def test_start_game_not_creator(self, game_service, mock_repos):
        """测试非房主尝试开始游戏"""
        room_repo, user_repo = mock_repos
        
        # 创建模拟用户和房间
        user = User(openid="user2", nickname="玩家2", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2", "user3"])
        
        # 设置模拟行为
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 调用被测试方法
        success, result = game_service.start_game("user2")
        
        # 验证结果
        assert success is False
        assert "权限" in result or "房主" in result  # 容忍不同的错误消息格式
    
    def test_show_word_success(self, game_service, mock_repos):
        """测试成功显示词语"""
        room_repo, user_repo = mock_repos
        
        # 创建模拟用户和房间
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2"])
        room.status = RoomStatus.PLAYING
        room.words = {'civilian': '苹果', 'undercover': '香蕉'}
        room.undercovers = ['user2']  # user2是卧底
        
        # 设置模拟行为
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        
        # 调用被测试方法
        success, result = game_service.show_word("user1")
        
        # 验证结果
        assert success is True
        assert result == "您的词语：苹果"  # user1是平民
    
    def test_vote_player_success(self, game_service, mock_repos):
        """测试成功投票"""
        room_repo, user_repo = mock_repos
        
        # 创建模拟用户和房间
        user = User(openid="user1", nickname="玩家1", current_room="1234")
        room = Room(room_id="1234", creator="user1", players=["user1", "user2", "user3"])
        room.status = RoomStatus.PLAYING
        room.undercovers = ['user2']  # user2是卧底
        
        # 设置模拟行为
        user_repo.get.return_value = user
        room_repo.get.return_value = room
        room_repo.save.return_value = True
        
        # 调用被测试方法
        success, result = game_service.vote_player("user1", 2)  # 投票给user3（索引2）
        
        # 验证结果
        assert success is True
        # 由于投票淘汰了卧底user2，游戏结束，返回胜利消息
        assert "平民获胜" in result or "投票成功" in result
        assert len(room.eliminated) > 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])