from __future__ import annotations

_states: dict[int, str | None] = {}
_data: dict[int, dict] = {}


def get_state(user_id: int) -> str | None:
    return _states.get(user_id)


def set_state(user_id: int, state: str | None) -> None:
    if state is None:
        _states.pop(user_id, None)
    else:
        _states[user_id] = state


def get_data(user_id: int) -> dict:
    return _data.get(user_id, {})


def update_data(user_id: int, **kwargs) -> None:
    _data.setdefault(user_id, {}).update(kwargs)


def clear(user_id: int) -> None:
    _states.pop(user_id, None)
    _data.pop(user_id, None)