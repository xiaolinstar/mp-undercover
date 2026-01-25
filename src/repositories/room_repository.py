#!/usr/bin/env python3
"""
房间仓储类
负责房间数据的持久化操作
"""

import json

import redis

from src.config.game_config import GameConfig
from src.exceptions import DataAccessError, RedisConnectionError, SerializationError
from src.models.room import Room
from src.utils.logger import log_exception, setup_logger

logger = setup_logger(__name__)


class RoomRepository:
    """房间仓储类"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "room:"
    
    def _get_key(self, room_id: str) -> str:
        """获取房间在Redis中的键"""
        return f"{self.prefix}{room_id}"
    
    def save(self, room: Room) -> None:
        """
        保存房间信息
        
        Args:
            room: 房间对象
            
        Raises:
            RedisConnectionError: Redis连接失败
            SerializationError: 序列化失败
            DataAccessError: 其他数据访问错误
        """
        try:
            # 更新最后活跃时间
            room.update_last_active()
            
            # 转换为字典并序列化
            room_data = room.to_dict()
            room_json = json.dumps(room_data, ensure_ascii=False)
            
            # 保存到Redis，设置过期时间
            key = self._get_key(room.room_id)
            self.redis.setex(
                key, 
                GameConfig.ROOM_TIMEOUT_SECONDS, 
                room_json
            )
            
            logger.debug("房间保存成功", extra={'room_id': room.room_id})
            
        except redis.ConnectionError as e:
            error = RedisConnectionError("保存房间", cause=e)
            log_exception(logger, error, {'room_id': room.room_id})
            raise error from e
            
        except (TypeError, ValueError) as e:
            error = SerializationError(
                message="房间数据序列化失败",
                error_code="REPO-INVALID-002",
                details={'room_id': room.room_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
            
        except Exception as e:
            error = DataAccessError(
                message="保存房间数据失败",
                error_code="REPO-DATA-001",
                details={'room_id': room.room_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
    
    def get(self, room_id: str) -> Room | None:
        """
        获取房间信息
        
        Args:
            room_id: 房间号
            
        Returns:
            房间对象，不存在时返回 None
            
        Raises:
            RedisConnectionError: Redis连接失败
            SerializationError: 反序列化失败
            DataAccessError: 其他数据访问错误
        """
        try:
            key = self._get_key(room_id)
            room_json = self.redis.get(key)
            
            if room_json is None:
                logger.debug("房间不存在", extra={'room_id': room_id})
                return None
            
            # 处理bytes类型的JSON数据
            if isinstance(room_json, bytes):
                room_json = room_json.decode('utf-8')
            
            room_data = json.loads(room_json)
            room = Room.from_dict(room_data)
            
            logger.debug("房间获取成功", extra={'room_id': room_id})
            return room
            
        except redis.ConnectionError as e:
            error = RedisConnectionError("获取房间", cause=e)
            log_exception(logger, error, {'room_id': room_id})
            raise error from e
            
        except (TypeError, ValueError, KeyError) as e:
            error = SerializationError(
                message="房间数据反序列化失败",
                error_code="REPO-INVALID-002",
                details={'room_id': room_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
            
        except Exception as e:
            error = DataAccessError(
                message="获取房间数据失败",
                error_code="REPO-DATA-001",
                details={'room_id': room_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
    
    def delete(self, room_id: str) -> None:
        """
        删除房间
        
        Args:
            room_id: 房间号
            
        Raises:
            RedisConnectionError: Redis连接失败
            DataAccessError: 其他数据访问错误
        """
        try:
            key = self._get_key(room_id)
            self.redis.delete(key)
            logger.debug("房间删除成功", extra={'room_id': room_id})
            
        except redis.ConnectionError as e:
            error = RedisConnectionError("删除房间", cause=e)
            log_exception(logger, error, {'room_id': room_id})
            raise error from e
            
        except Exception as e:
            error = DataAccessError(
                message="删除房间数据失败",
                error_code="REPO-DATA-001",
                details={'room_id': room_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
    
    def exists(self, room_id: str) -> bool:
        """
        检查房间是否存在
        
        Args:
            room_id: 房间号
            
        Returns:
            存在返回 True，否则返回 False
            
        Raises:
            RedisConnectionError: Redis连接失败
            DataAccessError: 其他数据访问错误
        """
        try:
            key = self._get_key(room_id)
            exists = self.redis.exists(key) > 0
            logger.debug("房间存在性检查", extra={'room_id': room_id, 'exists': exists})
            return exists
            
        except redis.ConnectionError as e:
            error = RedisConnectionError("检查房间存在性", cause=e)
            log_exception(logger, error, {'room_id': room_id})
            raise error from e
            
        except Exception as e:
            error = DataAccessError(
                message="检查房间存在性失败",
                error_code="REPO-DATA-001",
                details={'room_id': room_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e