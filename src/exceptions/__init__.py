#!/usr/bin/env python3
"""
异常导出模块
将分散在各个分层文件中的异常统一聚合导出，方便外部引用
"""

# ============================================================================
# 1. 基础分类导出
# ============================================================================
from src.exceptions.base import BaseAppException, BusinessException, ClientException, ServerException
from src.exceptions.business.game import (
    GameAlreadyStartedError,
    GameEndedError,
    GameException,
    GameNotStartedError,
    InsufficientPlayersError,
    InvalidPlayerIndexError,
    InvalidPlayerStateError,
    PlayerEliminatedError,
)

# ============================================================================
# 4. 业务逻辑异常 (Business Exceptions)
# ============================================================================
from src.exceptions.business.room import (
    InvalidStateTransitionError,
    RoomException,
    RoomFullError,
    RoomPermissionError,
    RoomStateError,
)
from src.exceptions.business.user import UserAlreadyInRoomError, UserException, UserNotInRoomError

# ============================================================================
# 3. 客户端异常 (Client Exceptions)
# ============================================================================
from src.exceptions.client import (
    InvalidCommandError,
    InvalidInputError,
    ResourceNotFoundError,
    RoomNotFoundError,
    UserNotFoundError,
    ValidationException,
)

# ============================================================================
# 2. 服务端异常 (Server Exceptions)
# ============================================================================
from src.exceptions.server import (
    CacheError,
    DataAccessError,
    ExternalServiceException,
    RedisConnectionError,
    RepositoryException,
    SerializationError,
    WeChatAPIError,
)

# 为了向后兼容，导出一些别名 (Alias for backward compatibility)
BaseGameException = BaseAppException
DomainException = BusinessException
InfrastructureException = ServerException

__all__ = [
    # 基础分类
    'BaseAppException', 'BaseGameException',
    'ServerException', 'InfrastructureException',
    'ClientException',
    'BusinessException', 'DomainException',

    # 服务端
    'RepositoryException', 'DataAccessError', 'SerializationError', 'CacheError',
    'ExternalServiceException', 'WeChatAPIError', 'RedisConnectionError',

    # 客户端
    'ValidationException', 'InvalidInputError', 'InvalidCommandError',
    'ResourceNotFoundError', 'RoomNotFoundError', 'UserNotFoundError',

    # 业务: 房间
    'RoomException', 'RoomFullError', 'RoomStateError', 'RoomPermissionError', 'InvalidStateTransitionError',

    # 业务: 游戏
    'GameException', 'GameNotStartedError', 'GameAlreadyStartedError', 'GameEndedError',
    'InsufficientPlayersError', 'InvalidPlayerStateError', 'PlayerEliminatedError', 'InvalidPlayerIndexError',

    # 业务: 用户
    'UserException', 'UserNotInRoomError', 'UserAlreadyInRoomError'
]
