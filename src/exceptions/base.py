#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常基础模块
定义项目中所有异常的根基类及三大分类
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class BaseAppException(Exception):
    """
    项目基础异常
    所有自定义异常都应该继承自此类
    """
    message: str                    # 用户友好的错误消息
    error_code: str                 # 唯一错误码 (格式: 模块-类型-序号)
    details: Optional[Dict] = None  # 详细上下文信息 (用于日志，不展示给用户)
    cause: Optional[Exception] = None  # 原始异常 (用于异常链)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ServerException(BaseAppException):
    """
    服务端异常 (Internal Server Error)
    指系统内部错误、基础设施故障、第三方服务调用失败等
    通常这类错误对于终端用户是不可修复的，系统应记录详细日志以便排查
    """
    pass


class ClientException(BaseAppException):
    """
    接口/客户端异常 (Bad Request / Client Error)
    指请求参数错误、认证失败、请求了不存在的资源等
    通常这类错误是由于客户端请求不当引起的，用户可以通过修正请求来解决
    """
    pass


class BusinessException(BaseAppException):
    """
    业务异常 (Business Logic Error / Domain Error)
    指违反了业务逻辑规则 (如：余额不足、游戏人数不合规等)
    通常这类错误是正常的业务校验逻辑，用户需要根据业务提示进行下一步操作
    """
    pass
