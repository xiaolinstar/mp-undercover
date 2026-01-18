#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.strategies.commands import CommandRouter
from src.messages import HELP_MESSAGES, ERROR_MESSAGES


class StubGameService:
    def create_room(self, user_id):
        return True, "1234"

    def join_room(self, user_id, room_id):
        return True, "成功加入房间，当前房间人数：2"

    def start_game(self, user_id):
        return True, "游戏开始成功"

    def show_word(self, user_id):
        return True, "您的词语：苹果"

    def show_status(self, user_id):
        return True, "房间号：1234\n房间状态：playing"

    def vote_player(self, user_id, target_index):
        return True, "投票成功"


def test_help_command():
    router = CommandRouter(StubGameService())
    resp = router.route("u1", "帮助")
    assert resp.startswith(HELP_MESSAGES["INSTRUCTIONS"])
    assert "房间号：1234" in resp
    assert "您的词语：苹果" in resp


def test_vote_command_success():
    router = CommandRouter(StubGameService())
    resp = router.route("u1", "t1")
    assert "投票成功" in resp
    assert "房间号：1234" in resp


def test_unknown_command():
    router = CommandRouter(StubGameService())
    resp = router.route("u1", "不存在的命令")
    assert ERROR_MESSAGES["UNKNOWN_COMMAND"] in resp
    assert "房间号：1234" in resp

