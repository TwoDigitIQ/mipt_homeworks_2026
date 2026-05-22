from context import trim_context
from messages import assistant_message, user_message


def test_does_not_change_messages_without_limits() -> None:
    messages = [
        user_message('one'),
        assistant_message('two'),
    ]

    result = trim_context(messages, limit_message=None, limit_chars=None)

    assert result == messages


def test_returns_copy() -> None:
    messages = [user_message('hello')]

    result = trim_context(messages, limit_message=None, limit_chars=None)
    result.append(assistant_message('changed'))

    assert messages == [user_message('hello')]


def test_trims_by_message_limit() -> None:
    messages = [
        user_message('one'),
        assistant_message('two'),
        user_message('three'),
    ]

    result = trim_context(messages, limit_message=2, limit_chars=None)

    assert result == [
        assistant_message('two'),
        user_message('three'),
    ]


def test_trims_by_chars_limit() -> None:
    messages = [
        user_message('old'),
        assistant_message('middle'),
        user_message('new'),
    ]

    result = trim_context(messages, limit_message=None, limit_chars=9)

    assert result == [
        assistant_message('middle'),
        user_message('new'),
    ]


def test_trims_by_both_limits() -> None:
    messages = [
        user_message('first'),
        assistant_message('second'),
        user_message('third'),
        assistant_message('fourth'),
    ]

    result = trim_context(messages, limit_message=3, limit_chars=11)

    assert result == [
        user_message('third'),
        assistant_message('fourth'),
    ]


def test_trims_single_long_message_from_left() -> None:
    messages = [user_message('0123456789')]

    result = trim_context(messages, limit_message=None, limit_chars=4)

    assert result == [user_message('6789')]


def test_trims_long_last_message_after_removing_old_messages() -> None:
    messages = [
        user_message('old'),
        assistant_message('0123456789'),
    ]

    result = trim_context(messages, limit_message=None, limit_chars=4)

    assert result == [assistant_message('6789')]


def test_empty_history() -> None:
    assert trim_context([], limit_message=10, limit_chars=100) == []


def test_history_does_not_need_pairs() -> None:
    messages = [
        user_message('one'),
        user_message('two'),
        user_message('three'),
    ]

    result = trim_context(messages, limit_message=2, limit_chars=None)

    assert result == [
        user_message('two'),
        user_message('three'),
    ]