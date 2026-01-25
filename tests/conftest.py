#!/usr/bin/env python3
"""
测试配置文件
"""

import os
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def app():
    """创建应用实例"""
    os.environ['APP_ENV'] = 'test'
    from src.app_factory import AppFactory
    app = AppFactory.create_app()
    return app


@pytest.fixture(scope="session")
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """创建CLI运行器"""
    return app.test_cli_runner()