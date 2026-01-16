#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏配置类
定义游戏的各种配置参数
"""

from typing import Dict, Tuple, List


class GameConfig:
    """游戏配置类"""
    
    # 房间超时时间（秒）
    ROOM_TIMEOUT_SECONDS = 2 * 60 * 60  # 2小时
    
    # 房间最大人数
    MAX_PLAYERS = 12
    
    # 最少游戏人数
    MIN_PLAYERS = 3
    
    # 卧底分配规则
    UNDERCOVER_COUNT_RULES: Dict[Tuple[int, int], int] = {
        (3, 5): 1,   # 3-5人：1个卧底
        (6, 8): 2,   # 6-8人：2个卧底
        (9, 12): 3   # 9-12人：3个卧底
    }
    
    # 词语库
    WORD_PAIRS: List[Tuple[str, str]] = [
        ('苹果', '香蕉'),
        ('夏天', '冬天'),
        ('篮球', '足球'),
        ('钢琴', '小提琴'),
        ('飞机', '火车'),
        ('眼镜', '手表'),
        ('大象', '狮子'),
        ('玫瑰', '百合'),
        ('手机', '电脑'),
        ('雨伞', '帽子'),
        ('书包', '钱包'),
        ('企鹅', '海豚'),
        ('周杰伦', '王力宏'),
        ('方便面', '挂面')
    ]
    
    @classmethod
    def get_undercover_count(cls, player_count: int) -> int:
        """根据玩家数量获取卧底数量"""
        for (min_players, max_players), count in cls.UNDERCOVER_COUNT_RULES.items():
            if min_players <= player_count <= max_players:
                return count
        return 0
    
    @classmethod
    def is_valid_player_count(cls, player_count: int) -> bool:
        """检查玩家数量是否有效"""
        return cls.MIN_PLAYERS <= player_count <= cls.MAX_PLAYERS