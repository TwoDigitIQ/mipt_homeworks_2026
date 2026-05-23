from gigavibe.messages import Message


def trim_context(
    messages: list[Message],
    limit_message: int | None,
    limit_chars: int | None,
) -> list[Message]:
    result = messages.copy()

    if limit_message is not None:
        result = result[-limit_message:]

    if limit_chars is not None:
        result = _fit_chars(result, limit_chars)

    return result


def _fit_chars(messages: list[Message], limit: int) -> list[Message]:
    result = messages.copy()
    total = sum(len(message.content) for message in result)

    while len(result) > 1 and total > limit:
        removed = result.pop(0)
        total -= len(removed.content)

    if result and total > limit:
        message = result[0]
        result[0] = Message(message.role, message.content[-limit:])

    return result