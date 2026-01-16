#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常类模块
定义项目中使用的所有自定义异常

异常类层次结构：
- BaseGameException (基础异常)
  - DomainException (领域异常)
    - RoomException (房间异常)
    - GameException (游戏异常)
    - UserException (用户异常)
  - InfrastructureException (基础设施异常)
    - RepositoryException (仓储异常)
    - ExternalServiceException (外部服务异常)
  - ValidationException (验证异常)
"""

# 基础异常
from src.exceptions.base import BaseGameException

# 领域异常
from src.exceptions.domain import DomainException

from src.exceptions.room import (
    RoomException,
    RoomNotFoundError,
    RoomFullError,
    RoomStateError,
    RoomPermissionError,
    InvalidStateTransitionError,
)

# 游戏异常
from src.exceptions.game import (
    GameException,
    GameNotStartedError,
    GameAlreadyStartedError,
    GameEndedError,
    InsufficientPlayersError,
    InvalidPlayerStateError,
    PlayerEliminatedError,
    InvalidPlayerIndexError,
)

# 用户异常
from src.exceptions.user import (
    UserException,
    UserNotFoundError,
    UserNotInRoomError,
    UserAlreadyInRoomError,
)

# 基础设施异常
from src.exceptions.infrastructure import (
    InfrastructureException,
    RepositoryException,
    DataAccessError,
    SerializationError,
    CacheError,
    ExternalServiceException,
    WeChatAPIError,
    RedisConnectionError,
)

# 验证异常
from src.exceptions.validation import (
    ValidationException,
    InvalidInputError,
    InvalidRoomIdError,
    InvalidCommandError,
)

__all__ = [
    # 基础异常
    'BaseGameException',
    
    # 领域异常
    'DomainException',
    
    # 房间异常
    'RoomException',
    'RoomNotFoundError',
    'RoomFullError',
    'RoomStateError',
    'RoomPermissionError',
    'InvalidStateTransitionError',
    
    # 游戏异常
    'GameException',
    'GameNotStartedError',
    'GameAlreadyStartedError',
    'GameEndedError',
    'InsufficientPlayersError',
    'InvalidPlayerStateError',
    'PlayerEliminatedError',
    'InvalidPlayerIndexError',
    
    # 用户异常
    'UserException',
    'UserNotFoundError',
    'UserNotInRoomError',
    'UserAlreadyInRoomError',
    
    # 基础设施异常
    'InfrastructureException',
    'RepositoryException',
    'DataAccessError',
    'SerializationError',
    'CacheError',
    'ExternalServiceException',
    'WeChatAPIError',
    'RedisConnectionError',
    
    # 验证异常
    'ValidationException',
    'InvalidInputError',
    'InvalidRoomIdError',
    'InvalidCommandError',
]
