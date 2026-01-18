#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏服务类
实现游戏的核心业务逻辑
"""

import random
from typing import Optional, Tuple
from src.models.room import Room, RoomStatus
from src.models.user import User
from src.repositories.room_repository import RoomRepository
from src.repositories.user_repository import UserRepository
from src.config.game_config import GameConfig
from src.utils.word_generator import WordGenerator
from src.fsm.game_state_machine import GameStateMachine, GameState, GameEvent
from src.services.push_service import PushService
from src.exceptions import (
    RoomNotFoundError, RoomStateError, RoomFullError, RoomPermissionError,
    GameNotStartedError, GameAlreadyStartedError, GameEndedError,
    InsufficientPlayersError, PlayerEliminatedError, InvalidPlayerIndexError,
    UserNotInRoomError, UserAlreadyInRoomError, RepositoryException, DomainException
)
from src.utils.logger import setup_logger, log_exception, log_business_event

logger = setup_logger(__name__)


class GameService:
    """游戏服务类"""
    
    def __init__(self, room_repo: RoomRepository, user_repo: UserRepository, push_service: Optional[PushService] = None):
        self.room_repo = room_repo
        self.user_repo = user_repo
        self.word_generator = WordGenerator(GameConfig.WORD_PAIRS)
        self.fsm = GameStateMachine()
        self.push = push_service
    
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
            self.room_repo.save(room)
            self.user_repo.save(user)
            
            if self.push and self.push.enabled():
                nickname = self.push.get_user_nickname(user_id)
                if nickname:
                    user.nickname = nickname
                    self.user_repo.save(user)
            else:
                logger.warning("推送服务未启用，无法获取用户昵称")

            log_business_event(logger, "房间创建成功", user_id=user_id, room_id=room_id)
            return True, room_id
            
        except RepositoryException as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "创建房间失败，请稍后重试"
            
        except Exception as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "创建房间时发生错误"
    
    def join_room(self, user_id: str, room_id: str) -> Tuple[bool, str]:
        """加入房间"""
        try:
            # 检查房间是否存在
            room = self.room_repo.get(room_id)
            if not room:
                raise RoomNotFoundError(room_id)
            
            # 检查房间状态
            if room.status != RoomStatus.WAITING:
                raise RoomStateError(
                    message="游戏已经开始，无法加入房间",
                    error_code="ROOM-STATE-003",
                    details={'room_id': room_id, 'status': room.status.value}
                )
            
            # 检查是否已在房间中
            if room.is_player(user_id):
                raise UserAlreadyInRoomError(user_id, room_id)
            
            # 检查房间人数
            if room.get_player_count() >= GameConfig.MAX_PLAYERS:
                raise RoomFullError(room_id, GameConfig.MAX_PLAYERS)
            
            # 加入房间
            room.players.append(user_id)
            
            # 创建用户对象
            user = User(
                openid=user_id,
                nickname=f"玩家{room.get_player_count()}",
                current_room=room_id
            )
            
            # 保存房间和用户信息
            self.room_repo.save(room)
            self.user_repo.save(user)
            
            if self.push and self.push.enabled():
                nickname = self.push.get_user_nickname(user_id)
                if nickname:
                    user.nickname = nickname
                    self.user_repo.save(user)
            
            log_business_event(logger, "用户加入房间", user_id=user_id, room_id=room_id, player_count=room.get_player_count())
            return True, f"成功加入房间，当前房间人数：{room.get_player_count()}"
            
        except DomainException as e:
            logger.warning(f"业务异常: {e.error_code} - {e.message}", extra={'details': e.details})
            return False, e.message
            
        except RepositoryException as e:
            log_exception(logger, e, {'user_id': user_id, 'room_id': room_id})
            return False, "加入房间失败，请稍后重试"
            
        except Exception as e:
            log_exception(logger, e, {'user_id': user_id, 'room_id': room_id})
            return False, "加入房间时发生错误"
    
    def start_game(self, user_id: str) -> Tuple[bool, str]:
        """开始游戏"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                raise RoomNotFoundError(user.current_room)
            
            # 检查是否为房主
            if not room.is_creator(user_id):
                raise RoomPermissionError(user_id, "开始游戏")
            
            # 检查房间人数
            if room.get_player_count() < GameConfig.MIN_PLAYERS:
                raise InsufficientPlayersError(room.get_player_count(), GameConfig.MIN_PLAYERS)
            
            # 检查房间状态
            if room.status == RoomStatus.PLAYING:
                raise GameAlreadyStartedError()
            elif room.status == RoomStatus.ENDED:
                raise GameEndedError()

            # 状态机校验
            can_start = self.fsm.can_transition(GameState.WAITING, GameEvent.START)
            if not can_start:
                raise RoomStateError(
                    message="当前状态无法开始游戏",
                    error_code="ROOM-STATE-003",
                    details={'room_id': room.room_id, 'status': room.status.value}
                )
            
            # 根据人数确定卧底数量
            player_count = room.get_player_count()
            undercover_count = GameConfig.get_undercover_count(player_count)
            if undercover_count == 0:
                raise InsufficientPlayersError(player_count, GameConfig.MIN_PLAYERS)
            
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
            next_state = self.fsm.next_state(GameState.WAITING, GameEvent.START)
            room.status = RoomStatus(next_state.value)
            room.current_round = 1
            
            # 保存房间信息
            self.room_repo.save(room)
            
            if self.push and self.push.enabled():
                for pid in room.players:
                    if pid in room.undercovers:
                        w = room.words['undercover']
                    else:
                        w = room.words['civilian']
                    self.push.send_text(pid, f"您的词语：{w}")
            
            log_business_event(logger, "游戏开始", 
                             user_id=user_id, room_id=room.room_id, 
                             player_count=player_count, undercover_count=undercover_count)
            return True, "游戏开始成功"
            
        except DomainException as e:
            logger.warning(f"业务异常: {e.error_code} - {e.message}", extra={'details': e.details})
            return False, e.message
            
        except RepositoryException as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "开始游戏失败，请稍后重试"
            
        except Exception as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "开始游戏时发生错误"
    
    def show_word(self, user_id: str) -> Tuple[bool, str]:
        """显示词语"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                raise RoomNotFoundError(user.current_room)
            
            # 检查游戏状态
            if room.status != RoomStatus.PLAYING:
                raise GameNotStartedError()
            
            # 检查用户是否在房间中
            if not room.is_player(user_id):
                raise UserNotInRoomError(user_id)
            
            # 检查用户是否已被淘汰
            if room.is_eliminated(user_id):
                raise PlayerEliminatedError(user_id)
            
            # 根据用户身份返回对应词语
            if user_id in room.undercovers:
                word = room.words['undercover']
            else:
                word = room.words['civilian']

            return True, f"您的词语：{word}"
            
        except DomainException as e:
            logger.warning(f"业务异常: {e.error_code} - {e.message}", extra={'details': e.details})
            return False, e.message
            
        except RepositoryException as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "显示词语失败，请稍后重试"
            
        except Exception as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "显示词语时发生错误"
    
    def vote_player(self, user_id: str, target_index: int) -> Tuple[bool, str]:
        """投票淘汰玩家"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                raise RoomNotFoundError(user.current_room)
            
            # 检查游戏状态
            if room.status != RoomStatus.PLAYING:
                raise GameNotStartedError()
            
            # 检查是否为房主
            if not room.is_creator(user_id):
                raise RoomPermissionError(user_id, "投票")
            
            # 检查序号是否有效
            if target_index < 1 or target_index > room.get_player_count():
                raise InvalidPlayerIndexError(target_index, room.get_player_count())
            
            # 获取目标玩家
            target_player = room.players[target_index - 1]
            
            # 检查目标玩家是否已被淘汰
            if room.is_eliminated(target_player):
                raise PlayerEliminatedError(target_player)
            
            # 记录被淘汰的玩家
            room.eliminated.append(target_player)
            
            # 保存房间信息
            self.room_repo.save(room)
            
            # 状态机：投票事件保持在 PLAYING
            if not self.fsm.can_transition(GameState.PLAYING, GameEvent.VOTE):
                raise RoomStateError(
                    message="当前状态无法投票",
                    error_code="ROOM-STATE-003",
                    details={'room_id': room.room_id, 'status': room.status.value}
                )

            # 检查游戏是否结束
            game_ended, result_message = self._check_game_end(room)
            
            log_business_event(logger, "投票淘汰", 
                             user_id=user_id, room_id=room.room_id, 
                             target_index=target_index, target_player=target_player,
                             game_ended=game_ended)
            
            if game_ended:
                if self.push and self.push.enabled():
                    self._push_room_status(room)
                return True, result_message
            if self.push and self.push.enabled():
                self._push_room_status(room)
            return True, "投票成功"
            
        except DomainException as e:
            logger.warning(f"业务异常: {e.error_code} - {e.message}", extra={'details': e.details})
            return False, e.message
            
        except RepositoryException as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "投票失败，请稍后重试"
            
        except Exception as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "投票时发生错误"
    
    def show_status(self, user_id: str) -> Tuple[bool, str]:
        """显示状态"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)
            
            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                raise RoomNotFoundError(user.current_room)
            
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
            
        except DomainException as e:
            logger.warning(f"业务异常: {e.error_code} - {e.message}", extra={'details': e.details})
            return False, e.message
            
        except RepositoryException as e:
            log_exception(logger, e, {'user_id': user_id})
            return False, "显示状态失败，请稍后重试"
            
        except Exception as e:
            log_exception(logger, e, {'user_id': user_id})
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
            next_state = self.fsm.next_state(GameState.PLAYING, GameEvent.END)
            room.status = RoomStatus(next_state.value)
            self.room_repo.save(room)
            
            # 让所有玩家自动退出房间
            self._auto_leave_room(room)
            
            return True, "游戏结束！平民获胜，成功找出了所有卧底！"
        
        # 检查剩余玩家数量
        remaining_players = room.get_remaining_players()
        
        # 如果剩余玩家少于3人，游戏结束
        if len(remaining_players) < 3:
            next_state = self.fsm.next_state(GameState.PLAYING, GameEvent.END)
            room.status = RoomStatus(next_state.value)
            self.room_repo.save(room)
            
            # 让所有玩家自动退出房间
            self._auto_leave_room(room)
            
            return True, "游戏结束！卧底获胜！"
        
        # 检查卧底数量是否大于等于平民数量
        remaining_undercovers = [p for p in room.undercovers if p in remaining_players]
        remaining_civilians = [p for p in remaining_players if p not in room.undercovers]
        
        if len(remaining_undercovers) >= len(remaining_civilians):
            next_state = self.fsm.next_state(GameState.PLAYING, GameEvent.END)
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

    def _push_room_status(self, room: Room) -> None:
        lines = [
            f"房间号：{room.room_id}",
            f"房间状态：{room.status.value}",
            "房间成员：",
        ]
        for i, player in enumerate(room.players):
            u = self.user_repo.get(player)
            n = (u.nickname if u else f"玩家{i+1}")
            if player == room.creator:
                n += "(房主)"
            if room.is_eliminated(player):
                n += "(已淘汰)"
            lines.append(f"{i+1}. {n}")
        if room.status == RoomStatus.PLAYING:
            lines.append("")
            lines.append(f"当前轮次：第{room.current_round}轮")
            lines.append(f"已淘汰：{len(room.eliminated)}人")
        content = "\n".join(lines)
        for pid in room.players:
            if self.push and self.push.enabled():
                self.push.send_text(pid, content)
