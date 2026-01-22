#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口/客户端异常模块
定义请求验证、权限、资源不存在等异常
"""

from src.exceptions.base import ClientException


class ValidationException(ClientException):
    """请求验证异常基类"""
    pass


class InvalidInputError(ValidationException):
    """请求参数格式或内容错误"""
    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"请求参数无效: {field}",
            error_code="CLIENT-VAL-001",
            details={'field': field, 'value': value}
        )


class InvalidCommandError(ValidationException):
    """用户发送了系统无法识别的指令"""
    def __init__(self, command: str):
        super().__init__(
            message=f"无法识别该指令: {command}",
            error_code="CLIENT-CMD-003",
            details={'command': command}
        )


class ResourceNotFoundError(ClientException):
    """资源不存在 (如：404 类错误)"""
    pass


class RoomNotFoundError(ResourceNotFoundError):
    """请求的房间 ID 不存在"""
    def __init__(self, room_id: str):
        super().__init__(
            message=f"房间 {room_id} 不存在",
            error_code="ROOM-NOT_FOUND-001",
            details={'room_id': room_id}
        )


class UserNotFoundError(ResourceNotFoundError):
    """请求的用户 OpenID 不存在"""
    def __init__(self, user_id: str):
        super().__init__(
            message="用户不存在或未初始化",
            error_code="USER-NOT_FOUND-001",
            details={'user_id': user_id}
        )
