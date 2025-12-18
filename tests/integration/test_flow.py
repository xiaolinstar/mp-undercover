#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
谁是卧底游戏流程测试
用于测试核心游戏逻辑
"""

import sys
import os
import json
import random

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入游戏逻辑相关函数
from app import (
    create_room, join_room, start_game, show_status, 
    handle_vote_by_index, check_game_end, get_room, get_user
)

def test_create_room():
    """测试创建房间功能"""
    print("=== 测试创建房间 ===")
    user_id = "test_user_1"
    result = create_room(user_id)
    print(f"创建房间结果: {result}")
    
    # 验证房间是否创建成功
    # 从结果中提取房间号
    if "房间创建成功" in result and "房间号：" in result:
        room_id = result.split("房间号：")[1].split("\n")[0]
        print(f"提取到房间号: {room_id}")
        
        # 验证房间数据
        room = get_room(room_id)
        if room:
            print(f"房间数据验证通过: {room}")
            return room_id, user_id
        else:
            print("房间数据验证失败")
            return None, None
    else:
        print("房间创建失败")
        return None, None


def test_join_room(room_id, creator_id):
    """测试加入房间功能"""
    print("\n=== 测试加入房间 ===")
    # 创建测试用户
    test_users = [f"test_user_{i}" for i in range(2, 5)]
    
    for user_id in test_users:
        result = join_room(user_id, room_id)
        print(f"用户 {user_id} 加入房间结果: {result}")
    
    # 验证房间人数
    room = get_room(room_id)
    if room and len(room['players']) == 4:
        print(f"房间人数验证通过: {len(room['players'])}人")
        return test_users
    else:
        print("房间人数验证失败")
        return []


def test_start_game(room_id, creator_id):
    """测试开始游戏功能"""
    print("\n=== 测试开始游戏 ===")
    result = start_game(creator_id)
    print(f"开始游戏结果: {result}")
    
    # 验证游戏状态
    room = get_room(room_id)
    if room and room['status'] == 'playing':
        print("游戏状态验证通过")
        print(f"卧底数量: {len(room['undercovers'])}")
        print(f"卧底列表: {room['undercovers']}")
        return True
    else:
        print("游戏状态验证失败")
        return False


def test_show_status(room_id, user_id):
    """测试查看状态功能"""
    print("\n=== 测试查看状态 ===")
    result = show_status(user_id)
    print(f"查看状态结果:\n{result}")
    
    # 验证是否包含关键信息
    if "您的信息" in result and "房间号" in result:
        print("状态信息验证通过")
        return True
    else:
        print("状态信息验证失败")
        return False


def test_voting(room_id, creator_id):
    """测试投票功能"""
    print("\n=== 测试投票功能 ===")
    room = get_room(room_id)
    
    if not room or len(room['players']) < 2:
        print("房间玩家不足，无法测试投票")
        return False
    
    # 房主投票给2号玩家
    result = handle_vote_by_index(creator_id, 2)
    print(f"投票结果: {result}")
    
    # 验证投票结果
    room = get_room(room_id)
    if room and len(room['eliminated']) == 1:
        print(f"投票验证通过，已淘汰玩家: {room['eliminated']}")
        return True
    else:
        print("投票验证失败")
        return False


def test_game_flow():
    """测试完整游戏流程"""
    print("=====================================")
    print("    谁是卧底游戏完整流程测试")
    print("=====================================")
    
    # 1. 创建房间
    room_id, creator_id = test_create_room()
    if not room_id:
        print("创建房间失败，终止测试")
        return False
    
    # 2. 加入房间
    players = test_join_room(room_id, creator_id)
    if not players:
        print("加入房间失败，终止测试")
        return False
    
    # 3. 开始游戏
    if not test_start_game(room_id, creator_id):
        print("开始游戏失败，终止测试")
        return False
    
    # 4. 查看状态
    if not test_show_status(room_id, creator_id):
        print("查看状态失败")
        return False
    
    # 5. 投票
    if not test_voting(room_id, creator_id):
        print("投票测试失败")
        return False
    
    print("\n=====================================")
    print("    游戏流程测试完成")
    print("=====================================")
    return True


def main():
    """主函数"""
    print("谁是卧底游戏测试脚本")
    print("注意：此脚本需要Redis服务正在运行")
    
    try:
        success = test_game_flow()
        if success:
            print("\n✅ 所有测试通过！")
            return 0
        else:
            print("\n❌ 部分测试失败！")
            return 1
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())