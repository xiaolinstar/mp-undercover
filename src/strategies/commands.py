#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional
from src.services.game_service import GameService
from src.config.commands_config import COMMAND_ALIASES
import re

# 修复导入路径，messages.py 在项目根目录
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.messages import HELP_MESSAGES, ERROR_MESSAGES


class CommandStrategy:
    def matches(self, content: str) -> bool:
        return False

    def execute(self, user_id: str, content: str) -> str:
        raise NotImplementedError


class HelpCommand(CommandStrategy):
    def matches(self, content: str) -> bool:
        return content in COMMAND_ALIASES["help"]

    def execute(self, user_id: str, content: str) -> str:
        return HELP_MESSAGES["INSTRUCTIONS"]


class CreateRoomCommand(CommandStrategy):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    def matches(self, content: str) -> bool:
        return content in COMMAND_ALIASES["create_room"]

    def execute(self, user_id: str, content: str) -> str:
        success, result = self.game_service.create_room(user_id)
        if success:
            room_id = result
            return f"房间创建成功！房间号：{room_id}\n请其他玩家输入'加入房间{room_id}'\n房主输入'开始游戏'即可开始游戏"
        return result


class JoinRoomCommand(CommandStrategy):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    def matches(self, content: str) -> bool:
        return content.startswith(COMMAND_ALIASES["join_room_prefix"])

    def execute(self, user_id: str, content: str) -> str:
        # 去掉前缀长度
        prefix = COMMAND_ALIASES["join_room_prefix"]
        room_id = content[len(prefix):].strip()
        if not room_id:
            return "请输入房间号，格式：加入房间1234"
        success, result = self.game_service.join_room(user_id, room_id)
        return result


class StartGameCommand(CommandStrategy):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    def matches(self, content: str) -> bool:
        return content in COMMAND_ALIASES["start_game"]

    def execute(self, user_id: str, content: str) -> str:
        success, result = self.game_service.start_game(user_id)
        if success:
            word_success, word_result = self.game_service.show_word(user_id)
            if word_success:
                return f"游戏开始！\n{word_result}\n请根据您的词语进行描述，注意不要暴露自己的身份\n线下进行描述和讨论，结束后由房主进行最终投票决定胜负"
            return "游戏开始成功！\n请根据您的词语进行描述，注意不要暴露自己的身份\n线下进行描述和讨论，结束后由房主进行最终投票决定胜负"
        return result


class ShowStatusCommand(CommandStrategy):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    def matches(self, content: str) -> bool:
        return content in COMMAND_ALIASES["show_status"]

    def execute(self, user_id: str, content: str) -> str:
        success, result = self.game_service.show_status(user_id)
        return result


class ShowWordCommand(CommandStrategy):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    def matches(self, content: str) -> bool:
        return content in COMMAND_ALIASES["show_word"]

    def execute(self, user_id: str, content: str) -> str:
        success, result = self.game_service.show_word(user_id)
        return result


class VoteCommand(CommandStrategy):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    def matches(self, content: str) -> bool:
        vote_prefix = COMMAND_ALIASES["vote_prefix"]
        return re.fullmatch(rf"{re.escape(vote_prefix)}\d+", content) is not None

    def execute(self, user_id: str, content: str) -> str:
        try:
            vote_prefix = COMMAND_ALIASES["vote_prefix"]
            target_index = int(content[len(vote_prefix):])
            success, result = self.game_service.vote_player(user_id, target_index)
            return result
        except ValueError:
            return ERROR_MESSAGES["VOTE_FORMAT_ERROR"]


class CommandRouter:
    def __init__(self, game_service: GameService):
        self.strategies: List[CommandStrategy] = [
            HelpCommand(),
            CreateRoomCommand(game_service),
            JoinRoomCommand(game_service),
            StartGameCommand(game_service),
            ShowStatusCommand(game_service),
            ShowWordCommand(game_service),
            VoteCommand(game_service),
        ]

    def route(self, user_id: str, content: str) -> str:
        normalized = content.strip().lower()
        for strategy in self.strategies:
            if strategy.matches(normalized):
                return strategy.execute(user_id, normalized)
        return ERROR_MESSAGES["UNKNOWN_COMMAND"]
