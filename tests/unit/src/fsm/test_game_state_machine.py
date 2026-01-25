import pytest

from src.exceptions import InvalidStateTransitionError
from src.fsm.game_state_machine import GameEvent, GameState, GameStateMachine


def test_state_transitions_basic():
    fsm = GameStateMachine()

    # WAITING -> START -> PLAYING
    next_state = fsm.next_state(GameState.WAITING, GameEvent.START)
    assert next_state == GameState.PLAYING

    # PLAYING -> VOTE -> PLAYING
    next_state = fsm.next_state(GameState.PLAYING, GameEvent.VOTE)
    assert next_state == GameState.PLAYING

    # PLAYING -> END -> ENDED
    next_state = fsm.next_state(GameState.PLAYING, GameEvent.END)
    assert next_state == GameState.ENDED


def test_illegal_transitions():
    fsm = GameStateMachine()

    # ENDED cannot START
    with pytest.raises(InvalidStateTransitionError):
        fsm.next_state(GameState.ENDED, GameEvent.START)

