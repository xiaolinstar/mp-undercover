#!/usr/bin/env python3
"""
房间业务规则异常
"""

from src.exceptions.base import BusinessException


class RoomException(BusinessException):
    """房间业务异常基类"""
    pass


class RoomFullError(RoomException):
    """房间人数已达到上限"""
    def __init__(self, room_id: str, max_players: int):
        super().__init__(
            message=f"该房间已满（最多可容纳 {max_players} 人）",
            error_code="ROOM-BIZ-002",
            details={'room_id': room_id, 'max_players': max_players}
        )


class RoomStateError(RoomException):
    """房间状态与所执行操作不匹配"""
    pass


class InvalidStateTransitionError(RoomStateError):
    """状态机转换错误"""
    def __init__(self, current_state: str, event: str):
        super().__init__(
            message=f"当前处于 {current_state} 状态，无法进行 {event} 操作",
            error_code="ROOM-STATE-005",
            details={'current_state': current_state, 'event': event}
        )


class RoomPermissionError(RoomException):
    """业务层面的权限检查失败 (如：非房主不能开始游戏)"""
    def __init__(self, user_id: str, action: str):
        super().__init__(
            message=f"操作受限：只有房主可以进行{action}",
            error_code="ROOM-PERM-004",
            details={'user_id': user_id, 'action': action}
        )
