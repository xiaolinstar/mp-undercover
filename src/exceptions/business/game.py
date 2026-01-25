#!/usr/bin/env python3
"""
游戏业务逻辑异常
"""

from src.exceptions.base import BusinessException


class GameException(BusinessException):
    """游戏逻辑异常基类"""
    pass


class GameNotStartedError(GameException):
    """尝试操作一个尚未开始的游戏"""
    def __init__(self):
        super().__init__(
            message="游戏尚未开始",
            error_code="GAME-BIZ-001"
        )


class GameAlreadyStartedError(GameException):
    """尝试重置或加入一个已在进行中的游戏"""
    def __init__(self):
        super().__init__(
            message="游戏已经开始了",
            error_code="GAME-BIZ-002"
        )


class GameEndedError(GameException):
    """尝试操作一个已经结束的游戏"""
    def __init__(self):
        super().__init__(
            message="游戏已结束",
            error_code="GAME-BIZ-003"
        )


class InsufficientPlayersError(GameException):
    """玩家数量不满足游戏开始要求"""
    def __init__(self, current_count: int, min_count: int):
        super().__init__(
            message=f"人数不足以开启游戏（还差 {min_count - current_count} 人）",
            error_code="GAME-BIZ-004",
            details={'current_players': current_count, 'min_players': min_count}
        )


class InvalidPlayerStateError(GameException):
    """玩家状态在当前游戏逻辑下是非法的"""
    pass


class PlayerEliminatedError(GameException):
    """已被淘汰的玩家执行了动作"""
    def __init__(self, user_id: str):
        super().__init__(
            message="您已被淘汰，只能旁观哦",
            error_code="GAME-BIZ-005",
            details={'user_id': user_id}
        )


class InvalidPlayerIndexError(GameException):
    """玩家序号索引无效"""
    def __init__(self, index: int, max_index: int):
        super().__init__(
            message=f"无效的玩家序号 (可选范围: 1-{max_index})",
            error_code="GAME-VAL-006",
            details={'index': index, 'max_index': max_index}
        )
