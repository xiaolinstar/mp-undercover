#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
提供统一的日志配置和工具函数
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    配置日志器
    
    Args:
        name: 日志器名称，建议使用项目根包名（如 'src'）以支持子模块日志冒泡
        log_level: 日志级别，默认从环境变量读取或使用 INFO
    """
    logger = logging.getLogger(name)
    
    # 设置日志级别
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 获取环境标识
    env = os.environ.get('APP_ENV', 'dev').upper()
    
    # 创建格式化器
    formatter = logging.Formatter(
        f'[%(asctime)s] [{env}] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（仅在非容器环境或指定日志目录时启用）
    log_dir = os.environ.get('LOG_DIR', 'logs')
    if os.environ.get('ENABLE_FILE_LOGGING', 'false').lower() == 'true':
        try:
            os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, 'app.log'),
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建文件日志处理器: {e}")
    
    return logger


def log_exception(logger: logging.Logger, exception: Exception, context: Optional[dict] = None):
    """
    记录异常信息
    
    Args:
        logger: 日志器
        exception: 异常对象
        context: 额外的上下文信息
    """
    from src.exceptions import BaseGameException
    
    extra_info = context or {}
    
    if isinstance(exception, BaseGameException):
        # 自定义异常，记录详细信息
        extra_info.update({
            'error_code': exception.error_code,
            'details': exception.details,
            'cause': str(exception.cause) if exception.cause else None
        })
        logger.error(
            f"业务异常: {exception.error_code} - {exception.message}",
            extra=extra_info,
            exc_info=exception.cause is not None
        )
    else:
        # 系统异常，记录完整堆栈
        logger.error(
            f"系统异常: {str(exception)}",
            extra=extra_info,
            exc_info=True
        )


def log_business_event(logger: logging.Logger, event: str, **kwargs):
    """
    记录业务事件
    
    Args:
        logger: 日志器
        event: 事件名称
        **kwargs: 事件相关的键值对
    """
    logger.info(f"业务事件: {event}", extra=kwargs)
