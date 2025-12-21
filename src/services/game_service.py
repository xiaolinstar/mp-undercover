#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏服务类
实现游戏的核心业务逻辑
"""

import random
from typing import Optional, List, Tuple
from src.models.room import Room, RoomStatus
from src.models.user import User
from src.repositories.room_repository import RoomRepository
from src.repositories.user_repository import UserRepository
from src.config.game_config import GameConfig
from src.utils.word_generator import WordGenerator
from src.fsm.game_state_machine import GameStateMachine, GameState, GameEvent


class GameService:
    """游戏服务类"""
    
    def __init__(self, room_repo: RoomRepository, user_repo: UserRepository):
        self.room_repo = room_repo
        self.user_repo = user_repo
        self.word_generator = WordGenerator(GameConfig.WORD_PAIRS)
        self.fsm = GameStateMachine()
    
    def create_room(self, user_id: str) -> Tuple[bool, str]:
        """创建房间"""
        try:
            # 生成唯一的房间号
            room_id = self._generate_unique_room_id()
            
            # 创建房间对象
            room = Room(
                room_id=room_id,
                creator=user_id,
                players=[user_id]
            )
            
            # 创建用户对象
            user = User(
                openid=user_id,
                nickname="玩家1",
                current_room=room_id
            )
            
            # 保存房间和用户信息
            if not self.room_repo.save(room):
                return False, "创建房间失败"
            
            if not self.user_repo.save(user):
                return False, "保存用户信息失败"
            
            return True, room_id
        except Exception as e:
            print(f"创建房间异常: {e}")
            return False, "创建房间时发生错误"
    
    def join_room(self, user_id: str, room_id: str) -> Tuple[bool, str]:
        """加入房间"""
        try:
            # 检查房间是否存在
            room = self.room_repo.get(room_id)
            if not room:
                return False, "房间不存在"
            
            # 检查房间状态
            if room.status != RoomStatus.WAITING:
                return False, "游戏已经开始，无法加入房间"
            
            # 检查是否已在房间中
            if room.is_player(user_id):
                return False, "您已经在房间中"
            
            # 检查房间人数
            if room.get_player_count() >= GameConfig.MAX_PLAYERS:
                return False, "房间已满，无法加入"
            
            # 加入房间
            room.players.append(user_id)
            
            # 创建用户对象
            user = User(
                openid=user_id,
                nickname=f"玩家{room.get_player_count()}",
                current_room=room_id
            )
            
            # 保存房间和用户信息
            if not self.room_repo.save(room):
                return False, "加入房间失败"
            
            if not self.user_repo.save(user):
                return False, "保存用户信息失败"
            
            return True, f"成功加入房间，当前房间人数：{room.get_player_count()}"
        except Exception as e:
            print(f"加入房间异常: {e}")
            return False, "加入房间时发生错误"
    
    def start_game(self, user_id: str) -> Tuple[bool, str]:
        """开始游戏"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                return False, "您不在任何房间中"
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                return False, "房间不存在"
            
            # 检查是否为房主
            if not room.is_creator(user_id):
                return False, "只有房主才能开始游戏"
            
            # 检查房间人数
            if room.get_player_count() < GameConfig.MIN_PLAYERS:
                return False, f"至少需要{GameConfig.MIN_PLAYERS}人才能开始游戏"
            
            # 检查房间状态
            if room.status == RoomStatus.PLAYING:
                return False, "游戏已经开始"
            elif room.status == RoomStatus.ENDED:
                return False, "游戏已结束"

            # 状态机校验
            can_start = self.fsm.can_transition(GameState.WAITING, GameEvent.START)
            if not can_start:
                return False, "当前状态无法开始游戏"
            
            # 根据人数确定卧底数量
            player_count = room.get_player_count()
            undercover_count = GameConfig.get_undercover_count(player_count)
            if undercover_count == 0:
                return False, "房间人数不符合游戏要求"
            
            # 随机选择卧底
            room.undercovers = random.sample(room.players, undercover_count)
            
            # 随机选择词语对
            word_pair = self.word_generator.get_random_word_pair()
            
            # 分配词语
            room.words = {
                'civilian': word_pair[0],
                'undercover': word_pair[1]
            }
            
            # 更新房间状态
            _, next_state = self.fsm.next_state(GameState.WAITING, GameEvent.START)
            room.status = RoomStatus(next_state.value)
            room.current_round = 1
            
            # 保存房间信息
            if not self.room_repo.save(room):
                return False, "开始游戏失败"
            
            return True, "游戏开始成功"
        except Exception as e:
            print(f"开始游戏异常: {e}")
            return False, "开始游戏时发生错误"
    
    def show_word(self, user_id: str) -> Tuple[bool, str]:
        """显示词语"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                return False, "您不在任何房间中"
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                return False, "房间不存在"
            
            # 检查游戏状态
            if room.status != RoomStatus.PLAYING:
                return False, "游戏尚未开始"
            
            # 检查用户是否在房间中
            if not room.is_player(user_id):
                return False, "您不在房间中"
            
            # 检查用户是否已被淘汰
            if room.is_eliminated(user_id):
                return False, "您已被淘汰"
            
            # 根据用户身份返回对应词语
            if user_id in room.undercovers:
                word = room.words['undercover']
            else:
                word = room.words['civilian']

            return True, f"您的词语：{word}"
        except Exception as e:
            print(f"显示词语异常: {e}")
            return False, "显示词语时发生错误"
    
    def vote_player(self, user_id: str, target_index: int) -> Tuple[bool, str]:
        """投票淘汰玩家"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                return False, "您不在任何房间中"
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                return False, "房间不存在"
            
            # 检查游戏状态
            if room.status != RoomStatus.PLAYING:
                return False, "游戏尚未开始"
            
            # 检查是否为房主
            if not room.is_creator(user_id):
                return False, "只有房主才能投票"
            
            # 检查序号是否有效
            if target_index < 1 or target_index > room.get_player_count():
                return False, "序号无效"
            
            # 获取目标玩家
            target_player = room.players[target_index - 1]
            
            # 检查目标玩家是否已被淘汰
            if room.is_eliminated(target_player):
                return False, "该玩家已被淘汰"
            
            # 记录被淘汰的玩家
            room.eliminated.append(target_player)
            
            # 保存房间信息
            if not self.room_repo.save(room):
                return False, "投票失败"
            
            # 状态机：投票事件保持在 PLAYING
            if not self.fsm.can_transition(GameState.PLAYING, GameEvent.VOTE):
                return False, "当前状态无法投票"

            # 检查游戏是否结束
            game_ended, result_message = self._check_game_end(room)
            if game_ended:
                return True, result_message
            
            return True, "投票成功"
        except Exception as e:
            print(f"投票异常: {e}")
            return False, "投票时发生错误"
    
    def show_status(self, user_id: str) -> Tuple[bool, str]:
        """显示状态"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                return False, "您不在任何房间中"
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                return False, "房间不存在"
            
            # 构建状态信息
            status_lines = []
            
            # 用户信息
            user_index = -1
            for i, player in enumerate(room.players):
                if player == user_id:
                    user_index = i + 1
                    break
            
            status_lines.append(f"您的信息：{user.nickname} (序号: {user_index})")
            status_lines.append("")
            
            # 房间信息
            status_lines.append(f"房间号：{room.room_id}")
            status_lines.append(f"房间状态：{room.status.value}")
            status_lines.append("房间成员：")
            
            # 玩家列表
            for i, player in enumerate(room.players):
                player_obj = self.user_repo.get(player)
                nickname = player_obj.nickname if player_obj else f"玩家{i+1}"
                
                # 添加角色标识
                if player == room.creator:
                    nickname += "(房主)"
                if room.is_eliminated(player):
                    nickname += "(已淘汰)"
                
                status_lines.append(f"{i+1}. {nickname}")
            
            # 游戏信息
            if room.status == RoomStatus.PLAYING:
                status_lines.append("")
                status_lines.append(f"当前轮次：第{room.current_round}轮")
                status_lines.append(f"已淘汰：{len(room.eliminated)}人")
                
                # 如果是房主，提示投票方式
                if room.is_creator(user_id):
                    status_lines.append("")
                    status_lines.append("您是房主，可通过't+序号'投票淘汰玩家")
            
            return True, "\n".join(status_lines)
        except Exception as e:
            print(f"显示状态异常: {e}")
            return False, "显示状态时发生错误"
    
    def _generate_unique_room_id(self) -> str:
        """生成唯一的房间号"""
        while True:
            room_id = str(random.randint(1000, 9999))
            if not self.room_repo.exists(room_id):
                return room_id
    
    def _check_game_end(self, room: Room) -> Tuple[bool, str]:
        """检查游戏是否结束"""
        # 检查是否有卧底被淘汰
        eliminated_undercovers = set(room.undercovers) & set(room.eliminated)
        
        # 如果所有卧底都被淘汰，平民获胜
        if len(eliminated_undercovers) == len(room.undercovers):
            _, next_state = self.fsm.next_state(GameState.PLAYING, GameEvent.END)
            room.status = RoomStatus(next_state.value)
            self.room_repo.save(room)
            
            # 让所有玩家自动退出房间
            self._auto_leave_room(room)
            
            return True, "游戏结束！平民获胜，成功找出了所有卧底！"
        
        # 检查剩余玩家数量
        remaining_players = room.get_remaining_players()
        
        # 如果剩余玩家少于3人，游戏结束
        if len(remaining_players) < 3:
            _, next_state = self.fsm.next_state(GameState.PLAYING, GameEvent.END)
            room.status = RoomStatus(next_state.value)
            self.room_repo.save(room)
            
            # 让所有玩家自动退出房间
            self._auto_leave_room(room)
            
            return True, "游戏结束！卧底获胜！"
        
        # 检查卧底数量是否大于等于平民数量
        remaining_undercovers = [p for p in room.undercovers if p in remaining_players]
        remaining_civilians = [p for p in remaining_players if p not in room.undercovers]
        
        if len(remaining_undercovers) >= len(remaining_civilians):
            _, next_state = self.fsm.next_state(GameState.PLAYING, GameEvent.END)
            room.status = RoomStatus(next_state.value)
            self.room_repo.save(room)
            
            # 让所有玩家自动退出房间
            self._auto_leave_room(room)
            
            return True, "游戏结束！卧底获胜！"
        
        return False, ""
    
    def _auto_leave_room(self, room: Room) -> None:
        """自动让玩家离开房间"""
        for player_id in room.players:
            user = self.user_repo.get(player_id)
            if user and user.current_room == room.room_id:
                user.leave_room()
                self.user_repo.save(user)
