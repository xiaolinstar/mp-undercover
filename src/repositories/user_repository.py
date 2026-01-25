#!/usr/bin/env python3
"""
用户仓储类
负责用户数据的持久化操作
"""

import json

import redis

from src.exceptions import DataAccessError, RedisConnectionError, SerializationError
from src.models.user import User
from src.utils.logger import log_exception, setup_logger

logger = setup_logger(__name__)


class UserRepository:
    """用户仓储类"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "user:"
    
    def _get_key(self, user_id: str) -> str:
        """获取用户在Redis中的键"""
        return f"{self.prefix}{user_id}"
    
    def save(self, user: User) -> None:
        """
        保存用户信息
        
        Args:
            user: 用户对象
            
        Raises:
            RedisConnectionError: Redis连接失败
            SerializationError: 序列化失败
            DataAccessError: 其他数据访问错误
        """
        try:
            # 转换为字典并序列化
            user_data = user.to_dict()
            user_json = json.dumps(user_data, ensure_ascii=False)
            
            # 保存到Redis
            key = self._get_key(user.openid)
            self.redis.set(key, user_json)
            
            logger.debug("用户保存成功", extra={'user_id': user.openid})
            
        except redis.ConnectionError as e:
            error = RedisConnectionError("保存用户", cause=e)
            log_exception(logger, error, {'user_id': user.openid})
            raise error from e
            
        except (TypeError, ValueError) as e:
            error = SerializationError(
                message="用户数据序列化失败",
                error_code="REPO-INVALID-002",
                details={'user_id': user.openid},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
            
        except Exception as e:
            error = DataAccessError(
                message="保存用户数据失败",
                error_code="REPO-DATA-001",
                details={'user_id': user.openid},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
    
    def get(self, user_id: str) -> User | None:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象，不存在时返回 None
            
        Raises:
            RedisConnectionError: Redis连接失败
            SerializationError: 反序列化失败
            DataAccessError: 其他数据访问错误
        """
        try:
            key = self._get_key(user_id)
            user_json = self.redis.get(key)
            
            if user_json is None:
                logger.debug("用户不存在", extra={'user_id': user_id})
                return None
            
            # 处理bytes类型的JSON数据
            if isinstance(user_json, bytes):
                user_json = user_json.decode('utf-8')
            
            user_data = json.loads(user_json)
            user = User.from_dict(user_data)
            
            logger.debug("用户获取成功", extra={'user_id': user_id})
            return user
            
        except redis.ConnectionError as e:
            error = RedisConnectionError("获取用户", cause=e)
            log_exception(logger, error, {'user_id': user_id})
            raise error from e
            
        except (TypeError, ValueError, KeyError) as e:
            error = SerializationError(
                message="用户数据反序列化失败",
                error_code="REPO-INVALID-002",
                details={'user_id': user_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
            
        except Exception as e:
            error = DataAccessError(
                message="获取用户数据失败",
                error_code="REPO-DATA-001",
                details={'user_id': user_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e
    
    def delete(self, user_id: str) -> None:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Raises:
            RedisConnectionError: Redis连接失败
            DataAccessError: 其他数据访问错误
        """
        try:
            key = self._get_key(user_id)
            self.redis.delete(key)
            logger.debug("用户删除成功", extra={'user_id': user_id})
            
        except redis.ConnectionError as e:
            error = RedisConnectionError("删除用户", cause=e)
            log_exception(logger, error, {'user_id': user_id})
            raise error from e
            
        except Exception as e:
            error = DataAccessError(
                message="删除用户数据失败",
                error_code="REPO-DATA-001",
                details={'user_id': user_id},
                cause=e
            )
            log_exception(logger, error)
            raise error from e