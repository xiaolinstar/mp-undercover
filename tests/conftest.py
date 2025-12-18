#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pytest配置文件
"""

import pytest
import redis
import os

@pytest.fixture(scope="session")
def redis_client():
    """Redis客户端fixture"""
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    client = redis.from_url(redis_url)
    yield client
    # 清理测试数据
    client.flushdb()

@pytest.fixture(autouse=True)
def clean_redis(redis_client):
    """自动清理Redis数据"""
    yield
    redis_client.flushdb()