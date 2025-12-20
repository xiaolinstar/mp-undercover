#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试查看词语功能
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import show_word, create_room, join_room, start_game, get_user, get_room, save_user, save_room
import unittest
from unittest.mock import patch, MagicMock


class TestShowWord(unittest.TestCase):
    """测试查看词语功能"""

    def setUp(self):
        """测试前准备"""
        # 创建测试用户
        self.user1_id = "test_user_1"
        self.user2_id = "test_user_2"
        self.user3_id = "test_user_3"
        
        # 保存原始的redis_client
        import app
        self.original_redis_client = app.redis_client
        
        # 创建mock的redis_client
        self.mock_redis_client = MagicMock()
        app.redis_client = self.mock_redis_client
        
        # 设置mock返回值
        self.users_data = {}
        self.rooms_data = {}
        
        def mock_get(key):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            if key_str.startswith('user:'):
                user_id = key_str.split(':')[1]
                user_data = self.users_data.get(user_id)
                if user_data:
                    import json
                    return json.dumps(user_data).encode('utf-8')
            elif key_str.startswith('room:'):
                room_id = key_str.split(':')[1]
                room_data = self.rooms_data.get(room_id)
                if room_data:
                    import json
                    return json.dumps(room_data).encode('utf-8')
            return None
            
        def mock_set(key, value, ex=None):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            value_str = value.decode('utf-8') if isinstance(value, bytes) else value
            import json
            if key_str.startswith('user:'):
                user_id = key_str.split(':')[1]
                self.users_data[user_id] = json.loads(value_str)
            elif key_str.startswith('room:'):
                room_id = key_str.split(':')[1]
                self.rooms_data[room_id] = json.loads(value_str)
            return True
            
        def mock_setex(key, ex, value):
            return mock_set(key, value, ex)
            
        self.mock_redis_client.get.side_effect = mock_get
        self.mock_redis_client.set.side_effect = mock_set
        self.mock_redis_client.setex.side_effect = mock_setex

    def tearDown(self):
        """测试后清理"""
        # 恢复原始的redis_client
        import app
        app.redis_client = self.original_redis_client

    def test_show_word_not_in_room(self):
        """测试用户不在房间中时查看词语"""
        result = show_word(self.user1_id)
        self.assertEqual(result, "您不在任何房间中")

    def test_show_word_game_not_started(self):
        """测试游戏未开始时查看词语"""
        # 创建房间
        with patch('app.random.randint', return_value=1234):
            create_room(self.user1_id)
        
        result = show_word(self.user1_id)
        self.assertEqual(result, "游戏尚未开始，无法查看词语信息")

    def test_show_word_user_not_in_room(self):
        """测试用户不在当前房间中时查看词语"""
        # 创建房间并开始游戏
        with patch('app.random.randint', return_value=1234):
            with patch('app.random.sample', return_value=[self.user1_id]):  # user1是卧底
                with patch('app.random.choice', side_effect=['动物类', ('企鹅', '海豚')]):
                    create_room(self.user1_id)
                    join_room(self.user2_id, '1234')
                    start_game(self.user1_id)
        
        # 尝试让不在房间中的用户查看词语
        result = show_word(self.user3_id)
        self.assertEqual(result, "您不在任何房间中")

    @patch('app.random')
    def test_show_word_civilian(self, mock_random):
        """测试平民查看词语"""
        # 设置随机数返回值，确保user2是平民
        mock_random.randint.return_value = 1234
        mock_random.sample.return_value = [self.user1_id]  # user1是卧底
        mock_random.choice.side_effect = [
            '动物类',  # 词语类别
            ('企鹅', '海豚')  # 词语对
        ]
        
        # 创建房间并开始游戏
        create_room(self.user1_id)
        join_room(self.user2_id, '1234')
        join_room(self.user3_id, '1234')  # 添加第三个玩家
        start_game(self.user1_id)
        
        # user2查看词语（应该是平民词）
        result = show_word(self.user2_id)
        expected = "您的词语：企鹅\n请根据您的词语进行描述，注意不要暴露自己的身份"
        self.assertEqual(result, expected)

    @patch('app.random')
    def test_show_word_undercover(self, mock_random):
        """测试卧底查看词语"""
        # 设置随机数返回值，确保user1是卧底
        mock_random.randint.return_value = 1234
        mock_random.sample.return_value = [self.user1_id]  # user1是卧底
        mock_random.choice.side_effect = [
            '动物类',  # 词语类别
            ('企鹅', '海豚')  # 词语对
        ]
        
        # 创建房间并开始游戏
        create_room(self.user1_id)
        join_room(self.user2_id, '1234')
        join_room(self.user3_id, '1234')  # 添加第三个玩家
        start_game(self.user1_id)
        
        # user1查看词语（应该是卧底词）
        result = show_word(self.user1_id)
        expected = "您的词语：海豚\n请根据您的词语进行描述，注意不要暴露自己的身份"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()