#!/usr/bin/env python3

import re
from asyncio.log import logger

from src.config.commands_config import COMMAND_ALIASES
from src.config.messages import ERROR_MESSAGES, HELP_MESSAGES
from src.services.game_service import GameService


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
            return f"房间创建成功！房间号：{room_id}\n请其他玩家输入'加入{room_id}'\n房主输入'开始'即可开始游戏"
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
            return "请输入房间号，格式：加入1234"
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
                return (
                    f"游戏开始！\n{word_result}\n"
                    "请根据您的词语进行描述，注意不要暴露自己的身份\n"
                    "线下进行描述和讨论，结束后由房主进行最终投票决定胜负"
                )
            return (
                "游戏开始成功！\n"
                "请根据您的词语进行描述，注意不要暴露自己的身份\n"
                "线下进行描述和讨论，结束后由房主进行最终投票决定胜负"
            )
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
        self.game_service = game_service
        self.strategies: list[CommandStrategy] = [
            HelpCommand(),
            CreateRoomCommand(game_service),
            JoinRoomCommand(game_service),
            StartGameCommand(game_service),
            VoteCommand(game_service),
        ]

    def route(self, user_id: str, content: str) -> str:
        normalized = content.strip().lower()
        response = ERROR_MESSAGES["UNKNOWN_COMMAND"]
        
        for strategy in self.strategies:
            if strategy.matches(normalized):
                logger.info(f"用户 {user_id} 执行命令 {normalized}")
                response = strategy.execute(user_id, normalized)
                break
        
        # 无论执行什么命令（包括未知命令），都尝试追加状态和词语信息
        status_success, status_msg = self.game_service.show_status(user_id)
        if status_success:
            response += f"\n\n{status_msg}"
            
        word_success, word_msg = self.game_service.show_word(user_id)
        if word_success:
            response += f"\n\n{word_msg}"
            
        return response
