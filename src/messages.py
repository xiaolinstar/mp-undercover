#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏消息配置文件
所有游戏中的回复消息都定义在这里，便于统一管理和调整
"""

# 房间相关消息
ROOM_MESSAGES = {
    "CREATE_SUCCESS": "房间创建成功！房间号：{room_id}\n请其他玩家输入'加入{room_id}'加入房间\n房主输入'开始'即可开始游戏",
    "CREATE_ERROR": "创建房间失败，请稍后重试",
    
    "NOT_FOUND": "房间不存在，请检查房间号",
    "ALREADY_IN_ROOM": "您已经在房间中",
    "GAME_STARTED": "游戏已经开始，无法加入房间",
    "ROOM_FULL": "房间已满，无法加入",
    
    "JOIN_SUCCESS": "成功加入房间{room_id}！当前房间人数：{player_count}",
    "JOIN_NOTIFICATION": "新玩家加入房间，当前房间人数：{player_count}",
    
    "INSUFFICIENT_PLAYERS": "至少需要3人才能开始游戏",
    "NOT_OWNER": "只有房主才能开始游戏",
    "GAME_ALREADY_STARTED": "游戏已经开始",
    "GAME_ENDED": "游戏已结束",
    "INVALID_PLAYER_COUNT": "房间人数不符合游戏要求"
}

# 游戏相关消息
GAME_MESSAGES = {
    "START_NOTIFICATION": "游戏开始！\n词语：{word}\n请根据您的词语进行描述，注意不要暴露自己的身份\n线下进行描述和讨论，结束后由房主进行最终投票决定胜负",
    "OWNER_REMINDER": "\n您是房主，请在线下游戏结束后，通过't+序号'的方式来决定被淘汰的玩家",
    
    "INVALID_INDEX": "无效的玩家序号",
    "PLAYER_ELIMINATED": "该玩家已被淘汰",
    
    "ROUND_NOTIFICATION": "进入第{round_number}轮，请继续线下进行游戏",
    
    "CIVILIAN_WIN": "游戏结束！平民获胜，成功找出了所有卧底！",
    "UNDERCOVER_WIN": "游戏结束！卧底获胜！"
}

# 用户相关消息
USER_MESSAGES = {
    "NOT_IN_ROOM": "您不在任何房间中",
    "NOT_IN_CURRENT_ROOM": "您不在当前房间中",
    "GAME_NOT_STARTED": "游戏尚未开始，无法查看词语信息"
}

# 投票相关消息
VOTE_MESSAGES = {
    "NOT_OWNER": "只有房主才能进行投票",
    "GAME_NOT_PLAYING": "游戏未开始或已结束",
    "INVALID_INDEX": "序号无效，请输入1-{max_index}之间的数字",
    "PLAYER_ELIMINATED": "该玩家已被淘汰",
    "SUCCESS": "success",
    "ELIMINATION_RESULT": "房主投票决定：{nickname}被淘汰"
}

# 帮助信息
HELP_MESSAGES = {
    "INSTRUCTIONS": """谁是卧底文字命令：
🎮谁是卧底（或帮助），查看帮助信息
✅创建，创建游戏房间
✅加入+房间号（例如：加入1234）
✅开始，房主开始游戏（至少3人）
👑t+序号，房主投票给指定玩家（例如：t1）
💡发送任意消息时，系统都会自动显示当前的游戏状态和您的词语
""",

"WELCOME": """欢迎您的关注👏
✨ 运维知识分享：SRE运维、职场生活、编程实践、AI与人工智能等
🚀 桌游发牌：聚会游戏辅助功能已开放测试，优化上新敬请期待...
"""
}

# 错误消息
ERROR_MESSAGES = {
    "UNKNOWN_COMMAND": "未知命令，请输入'帮助'查看可用命令",
    "VOTE_FORMAT_ERROR": "投票格式错误，请使用't+序号'的格式，例如't1'",
    "SYSTEM_ERROR": "系统繁忙，请稍后再试"
}