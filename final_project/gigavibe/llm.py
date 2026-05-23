from collections.abc import Iterator
from typing import Any, cast

from openai import OpenAI, OpenAIError

from gigavibe.config import AppConfig
from gigavibe.errors import LLMError
from gigavibe.messages import OpenAIMessage


class LLMClient:
    def __init__(self, config: AppConfig) -> None:
        self._client = OpenAI(api_key=config.api_key, base_url=config.api_host)
        self._model = config.model
        self._temperature = config.temperature

    def complete(self, messages: list[OpenAIMessage]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=cast(Any, messages),
                temperature=self._temperature,
            )
        except OpenAIError as exc:
            raise LLMError('LLM request failed') from exc

        if not response.choices:
            raise LLMError('LLM returned empty response')

        return response.choices[0].message.content or ''

    def stream_complete(self, messages: list[OpenAIMessage]) -> Iterator[str]:
        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=cast(Any, messages),
                temperature=self._temperature,
                stream=True,
            )

            for chunk in stream:
                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except OpenAIError as exc:
            raise LLMError('LLM stream request failed') from exc