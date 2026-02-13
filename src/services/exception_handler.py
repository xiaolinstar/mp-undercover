#!/usr/bin/env python3
"""
全局异常处理器
实现类似Spring AOP的全局异常处理机制
"""

from flask import Flask

from src.exceptions import BaseAppException, BusinessException, ClientException, ServerException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def register_global_exception_handlers(app: Flask):
    """
    注册全局异常处理器
    
    Args:
        app: Flask应用实例
    """
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有未被捕获的异常"""
        app.logger.error(f"未捕获的异常: {str(e)}", exc_info=True)
        return "系统繁忙，请稍后重试", 500
    
    @app.errorhandler(BaseAppException)
    def handle_base_app_exception(e):
        """处理应用基础异常"""
        app.logger.warning(f"应用异常 [{e.error_code}]: {e.message}")
        return e.message, 200  # 业务异常通常返回200，内容是错误信息
    
    @app.errorhandler(ServerException)
    def handle_server_exception(e):
        """处理服务端异常"""
        app.logger.error(f"服务端异常 [{e.error_code}]: {e.message}", exc_info=True)
        return "系统繁忙，请稍后重试", 500
    
    @app.errorhandler(ClientException)
    def handle_client_exception(e):
        """处理客户端异常"""
        app.logger.warning(f"客户端异常 [{e.error_code}]: {e.message}")
        return e.message, 400  # 客户端错误返回400状态码
    
    @app.errorhandler(BusinessException)
    def handle_business_exception(e):
        """处理业务异常"""
        app.logger.warning(f"业务异常 [{e.error_code}]: {e.message}")
        return e.message, 200  # 业务异常返回用户友好的提示


def handle_exception_response(exception: BaseAppException, app: Flask):
    """
    统一异常响应处理
    
    Args:
        exception: 异常实例
        app: Flask应用实例
        
    Returns:
        tuple: (响应内容, HTTP状态码)
    """
    if isinstance(exception, ServerException):
        app.logger.error(f"服务端异常 [{exception.error_code}]: {exception.message}", exc_info=True)
        return "系统繁忙，请稍后重试", 500
    elif isinstance(exception, ClientException):
        app.logger.warning(f"客户端异常 [{exception.error_code}]: {exception.message}")
        return exception.message, 400
    elif isinstance(exception, BusinessException):
        app.logger.warning(f"业务异常 [{exception.error_code}]: {exception.message}")
        return exception.message, 200
    else:
        app.logger.error(f"未知异常: {str(exception)}", exc_info=True)
        return "系统繁忙，请稍后重试", 500