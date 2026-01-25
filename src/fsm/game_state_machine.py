#!/usr/bin/env python3

from enum import Enum

from src.exceptions import InvalidStateTransitionError


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
        self.transitions: dict[GameState, dict[GameEvent, GameState]] = {
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

    def next_state(self, state: GameState, event: GameEvent) -> GameState:
        if not self.can_transition(state, event):
            raise InvalidStateTransitionError(state.value, event.value)
        return self.transitions[state][event]

