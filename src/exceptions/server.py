#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务端异常模块
定义基础设施、数据层及外部系统相关的异常
"""

from typing import Optional
from src.exceptions.base import ServerException


class RepositoryException(ServerException):
    """仓储/持久化层异常"""
    pass


class DataAccessError(RepositoryException):
    """底层数据访问错误 (如：Redis 命令执行失败)"""
    pass


class SerializationError(RepositoryException):
    """数据读写时的序列化/反序列化错误"""
    pass


class CacheError(RepositoryException):
    """缓存操作相关的通用错误"""
    pass


# ============================================================================
# 外部系统异常 (External System Exceptions)
# ============================================================================

class ExternalServiceException(ServerException):
    """外部服务调用异常基类"""
    pass


class WeChatAPIError(ExternalServiceException):
    """微信开放平台 API 调用失败"""
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(
            message=f"微信服务暂时不可用: {message}",
            error_code="SYS-EXTERNAL-002",
            cause=cause
        )


class RedisConnectionError(ExternalServiceException):
    """Redis 数据库连接失败"""
    def __init__(self, operation: str, cause: Optional[Exception] = None):
        super().__init__(
            message="系统数据连接失败",
            error_code="SYS-CONN-001",
            details={'operation': operation},
            cause=cause
        )
