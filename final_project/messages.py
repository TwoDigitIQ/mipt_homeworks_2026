from dataclasses import dataclass
from typing import Literal, TypeAlias


Role: TypeAlias = Literal['system', 'user', 'assistant']
OpenAIMessage: TypeAlias = dict[str, str]


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str

    def as_openai(self) -> OpenAIMessage:
        return {'role': self.role, 'content': self.content}


class ChatHistory:
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def add_user_message(self, content: str) -> None:
        self._messages.append(user_message(content))

    def add_assistant_message(self, content: str) -> None:
        self._messages.append(assistant_message(content))

    def replace(self, messages: list[Message]) -> None:
        self._messages = messages.copy()

    def reset(self) -> None:
        self._messages.clear()

    def messages(self) -> list[Message]:
        return self._messages.copy()


def user_message(content: str) -> Message:
    return Message('user', content)


def assistant_message(content: str) -> Message:
    return Message('assistant', content)


def build_openai_messages(
    messages: list[Message],
    system_prompt: str | None,
) -> list[OpenAIMessage]:
    result: list[OpenAIMessage] = []

    if system_prompt:
        result.append(Message('system', system_prompt).as_openai())

    result.extend(message.as_openai() for message in messages)
    return result