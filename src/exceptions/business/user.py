#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户状态业务异常
"""

from src.exceptions.base import BusinessException


class UserException(BusinessException):
    """用户业务异常基类"""
    pass


class UserNotInRoomError(UserException):
    """在该上下文中，用户应在房间内但实际不在"""
    def __init__(self, user_id: str):
        super().__init__(
            message="您尚未加入任何房间",
            error_code="USER-BIZ-002",
            details={'user_id': user_id}
        )


class UserAlreadyInRoomError(UserException):
    """用户尝试加入房间但已经在其中一个房间了"""
    def __init__(self, user_id: str, room_id: str):
        super().__init__(
            message="您已在其他房间中，请勿重复加入",
            error_code="USER-BIZ-003",
            details={'user_id': user_id, 'room_id': room_id}
        )
