#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房间相关异常
"""

from src.exceptions.domain import DomainException


class RoomException(DomainException):
    """房间异常基类"""
    pass


class RoomNotFoundError(RoomException):
    """房间不存在"""
    def __init__(self, room_id: str):
        super().__init__(
            message=f"房间 {room_id} 不存在",
            error_code="ROOM-NOT_FOUND-001",
            details={'room_id': room_id}
        )


class RoomFullError(RoomException):
    """房间已满"""
    def __init__(self, room_id: str, max_players: int):
        super().__init__(
            message=f"房间已满，无法加入（最多{max_players}人）",
            error_code="ROOM-STATE-002",
            details={'room_id': room_id, 'max_players': max_players}
        )


class RoomStateError(RoomException):
    """房间状态错误"""
    pass


class InvalidStateTransitionError(RoomStateError):
    """状态转换非法"""
    def __init__(self, current_state: str, event: str):
        super().__init__(
            message=f"游戏当前处于 {current_state} 状态，无法执行 {event} 操作",
            error_code="ROOM-STATE-005",
            details={'current_state': current_state, 'event': event}
        )


class RoomPermissionError(RoomException):
    """房间权限错误"""
    def __init__(self, user_id: str, action: str):
        super().__init__(
            message=f"您没有权限执行此操作：{action}",
            error_code="ROOM-PERMISSION-004",
            details={'user_id': user_id, 'action': action}
        )
