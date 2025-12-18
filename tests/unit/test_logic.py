#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
谁是卧底游戏逻辑单元测试
"""

import pytest
import sys
import os
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入游戏逻辑相关函数
from app import (
    create_room, join_room, start_game, show_status, 
    handle_vote_by_index, get_room, get_user, save_room, save_user
)

class TestLogic:
    """游戏逻辑测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前准备"""
        # 可以在这里添加测试前的准备工作
        yield
        # 测试后清理工作
    
    def test_create_room(self):
        """测试创建房间功能"""
        user_id = "test_user_1"
        result = create_room(user_id)
        
        # 验证返回结果
        assert "房间创建成功" in result
        assert "房间号：" in result
        
        # 提取房间号
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 验证房间数据
        room = get_room(room_id)
        assert room is not None
        assert room['room_id'] == room_id
        assert room['creator'] == user_id
        assert len(room['players']) == 1
        assert user_id in room['players']
        assert room['status'] == 'waiting'
    
    def test_join_room(self):
        """测试加入房间功能"""
        # 先创建一个房间
        user_id = "test_creator"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 新用户加入房间
        new_user_id = "test_joiner"
        result = join_room(new_user_id, room_id)
        
        # 验证加入结果
        assert "成功加入房间" in result
        assert room_id in result
        
        # 验证房间数据
        room = get_room(room_id)
        assert len(room['players']) == 2
        assert new_user_id in room['players']
    
    def test_join_nonexistent_room(self):
        """测试加入不存在的房间"""
        user_id = "test_user"
        result = join_room(user_id, "9999")  # 不存在的房间号
        
        # 验证返回结果
        assert "房间不存在" in result
    
    def test_start_game_insufficient_players(self):
        """测试玩家不足时开始游戏"""
        # 创建房间但不加入足够玩家
        user_id = "test_user"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 尝试开始游戏
        result = start_game(user_id)
        
        # 验证返回结果
        assert "至少需要3人才能开始游戏" in result
    
    def test_show_status(self):
        """测试查看状态功能"""
        # 创建房间
        user_id = "test_user"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 查看状态
        result = show_status(user_id)
        
        # 验证返回结果
        assert "您的信息" in result
        assert "房间号" in result
        assert "房间状态" in result
    
    def test_vote_with_invalid_index(self):
        """测试使用无效序号投票"""
        # 创建房间
        user_id = "test_user"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够玩家开始游戏
        join_room("test_user_2", room_id)
        join_room("test_user_3", room_id)
        start_game(user_id)  # 房主开始游戏
        
        # 使用无效序号投票
        result = handle_vote_by_index(user_id, 99)
        
        # 验证返回结果
        assert "序号无效" in result

if __name__ == "__main__":
    pytest.main(["-v", __file__])