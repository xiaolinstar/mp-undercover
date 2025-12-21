#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.fsm.game_state_machine import GameStateMachine, GameState, GameEvent


def test_state_transitions_basic():
    fsm = GameStateMachine()

    # WAITING -> START -> PLAYING
    ok, next_state = fsm.next_state(GameState.WAITING, GameEvent.START)
    assert ok is True
    assert next_state == GameState.PLAYING

    # PLAYING -> VOTE -> PLAYING
    ok, next_state = fsm.next_state(GameState.PLAYING, GameEvent.VOTE)
    assert ok is True
    assert next_state == GameState.PLAYING

    # PLAYING -> END -> ENDED
    ok, next_state = fsm.next_state(GameState.PLAYING, GameEvent.END)
    assert ok is True
    assert next_state == GameState.ENDED


def test_illegal_transitions():
    fsm = GameStateMachine()

    # ENDED cannot START
    ok, next_state = fsm.next_state(GameState.ENDED, GameEvent.START)
    assert ok is False
    assert next_state == GameState.ENDED

