#!/usr/bin/env python3
"""
游戏配置类
定义游戏的各种配置参数
"""


class GameConfig:
    """游戏配置类"""

    # 房间超时时间（秒）
    ROOM_TIMEOUT_SECONDS = 2 * 60 * 60  # 2小时

    # 房间最大人数
    MAX_PLAYERS = 12

    # 最少游戏人数
    MIN_PLAYERS = 3

    # 卧底分配规则
    UNDERCOVER_COUNT_RULES: dict[tuple[int, int], int] = {
        (3, 5): 1,  # 3-5人：1个卧底
        (6, 8): 2,  # 6-8人：2个卧底
        (9, 12): 3,  # 9-12人：3个卧底
    }

    # 词语库
    WORD_PAIRS: list[tuple[str, str]] = [
        ("苹果", "香蕉"),
        ("夏天", "冬天"),
        ("篮球", "足球"),
        ("钢琴", "小提琴"),
        ("飞机", "火车"),
        ("眼镜", "手表"),
        ("大象", "狮子"),
        ("男同", "同志"),
        ("手机", "电脑"),
        ("雨伞", "帽子"),
        ("书包", "钱包"),
        ("企鹅", "海豚"),
        ("周杰伦", "王力宏"),
        ("方便面", "挂面"),
        ("火车", "地铁"),
        ("饺子", "馄饨"),
        ("烤鸭", "盐水鸭"),
        ("张凌赫", "宋威龙"),
        ("刘德华", "梁朝伟"),
        ("杨幂", "高圆圆"),
        ("王一博", "肖战"),
        ("王者荣耀", "英雄联盟"),
        ("绝地求生", "和平精英"),
        ("打底裤", "秋裤"),
        ("丝袜", "渔网袜"),
        ("肯德基", "吮指原味鸡"),
        ("麻辣烫", "火锅"),
        ("体香", "狐臭"),
        ("公主", "商K"),
        ("洗脚", "按摩"),
        ("眼泪", "眼药水"),
        ("烩面", "大盘鸡"),
        ("约会", "搭讪"),
        ("男模", "男神"),
        ("老婆", "老板"),
        ("上班", "上坟"),
        ("夫子庙", "秦淮河"),
        ("电磁炉", "空气炸锅"),
        ("炸鸡", "啤酒"),
        ("韩剧", "癌症"),
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
