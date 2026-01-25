#!/usr/bin/env python3
"""
谁是卧底游戏主应用
"""
import os

from src.app_factory import AppFactory

# 创建应用实例
app = AppFactory.create_app()

def main():
    """主逻辑入口"""
    # 运行应用
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()