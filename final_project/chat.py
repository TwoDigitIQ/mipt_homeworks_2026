from config import AppConfig
from context import trim_context
from files import inject_files
from messages import ChatHistory, OpenAIMessage, build_openai_messages, user_message


class ChatSession:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._history = ChatHistory()

    def reset(self) -> None:
        self._history.reset()

    def prepare_message(self, text: str) -> list[OpenAIMessage]:
        text = inject_files(text)
        self._history.add_user_message(text)
        self._trim_history()
        return build_openai_messages(self._history.messages(), self._config.system_prompt)

    def save_answer(self, answer: str) -> None:
        self._history.add_assistant_message(answer)

    def chunk_message(self, prompt: str, chunk: str) -> list[OpenAIMessage]:
        return build_openai_messages(
            [user_message(f'{prompt}\n\n{chunk}')],
            self._config.system_prompt,
        )

    def _trim_history(self) -> None:
        self._history.replace(
            trim_context(
                self._history.messages(),
                self._config.limit_message,
                self._config.limit_chars,
            ),
        )