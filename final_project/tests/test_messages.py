from messages import (
    ChatHistory,
    Message,
    assistant_message,
    build_openai_messages,
    user_message,
)


def test_creates_user_message() -> None:
    message = user_message('hello')

    assert message.role == 'user'
    assert message.content == 'hello'


def test_creates_assistant_message() -> None:
    message = assistant_message('hi')

    assert message.role == 'assistant'
    assert message.content == 'hi'


def test_converts_message_to_openai_format() -> None:
    message = user_message('hello')

    assert message.as_openai() == {'role': 'user', 'content': 'hello'}


def test_history_preserves_order() -> None:
    history = ChatHistory()

    history.add_user_message('first')
    history.add_assistant_message('second')
    history.add_user_message('third')

    assert history.messages() == [
        user_message('first'),
        assistant_message('second'),
        user_message('third'),
    ]


def test_history_returns_copy() -> None:
    history = ChatHistory()
    history.add_user_message('hello')

    messages = history.messages()
    messages.append(assistant_message('changed'))

    assert history.messages() == [user_message('hello')]


def test_history_replace_copies_messages() -> None:
    history = ChatHistory()
    messages = [user_message('hello')]

    history.replace(messages)
    messages.append(assistant_message('changed'))

    assert history.messages() == [user_message('hello')]


def test_history_reset() -> None:
    history = ChatHistory()

    history.add_user_message('hello')
    history.add_assistant_message('hi')
    history.reset()

    assert history.messages() == []


def test_build_openai_messages_with_system_prompt() -> None:
    messages = [user_message('hello'), assistant_message('hi')]

    result = build_openai_messages(messages, 'be helpful')

    assert result == [
        {'role': 'system', 'content': 'be helpful'},
        {'role': 'user', 'content': 'hello'},
        {'role': 'assistant', 'content': 'hi'},
    ]


def test_build_openai_messages_without_system_prompt() -> None:
    messages = [user_message('hello')]

    result = build_openai_messages(messages, None)

    assert result == [{'role': 'user', 'content': 'hello'}]


def test_history_does_not_require_user_assistant_pairs() -> None:
    history = ChatHistory()

    history.add_user_message('message without answer')

    assert build_openai_messages(history.messages(), None) == [
        {'role': 'user', 'content': 'message without answer'},
    ]


def test_can_create_system_message_directly() -> None:
    message = Message('system', 'be helpful')

    assert message.as_openai() == {'role': 'system', 'content': 'be helpful'}