#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import Dict, Set, Tuple


class GameState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    ENDED = "ended"


class GameEvent(Enum):
    CREATE = "create"
    JOIN = "join"
    START = "start"
    VOTE = "vote"
    END = "end"


class GameStateMachine:
    def __init__(self):
        self.transitions: Dict[GameState, Dict[GameEvent, GameState]] = {
            GameState.WAITING: {
                GameEvent.CREATE: GameState.WAITING,
                GameEvent.JOIN: GameState.WAITING,
                GameEvent.START: GameState.PLAYING,
            },
            GameState.PLAYING: {
                GameEvent.VOTE: GameState.PLAYING,
                GameEvent.END: GameState.ENDED,
            },
            GameState.ENDED: {},
        }

    def can_transition(self, state: GameState, event: GameEvent) -> bool:
        return event in self.transitions.get(state, {})

    def next_state(self, state: GameState, event: GameEvent) -> Tuple[bool, GameState]:
        if not self.can_transition(state, event):
            return False, state
        return True, self.transitions[state][event]

