import os
from pathlib import Path

from chat import ChatSession
from chunks import is_chunk_command, parse_chunk_command, split_text
from config import load_config
from errors import ChunkCommandError, ConfigError, FileInjectionError, LLMError
from files import read_text_file
from llm import LLMClient
from messages import OpenAIMessage


_EXIT_COMMAND = r'\q'
_RESET_COMMAND = '/reset'


def run() -> None:
    try:
        config = load_config(Path(__file__).with_name('config.yaml'))
    except ConfigError as exc:
        print(f'Config error: {exc}')
        return

    client = LLMClient(config)
    session = ChatSession(config)

    while True:
        user_input = input('>>> ').strip()

        if not user_input:
            continue

        if user_input == _EXIT_COMMAND:
            return

        if user_input == _RESET_COMMAND:
            session.reset()
            _clear_screen()
            continue

        if is_chunk_command(user_input):
            _run_chunk_mode(client, session, user_input, stream=config.stream)
            continue

        _handle_chat_message(user_input, session, client, stream=config.stream)


def _handle_chat_message(
    user_input: str,
    session: ChatSession,
    client: LLMClient,
    *,
    stream: bool,
) -> None:
    try:
        messages = session.prepare_message(user_input)
    except FileInjectionError as exc:
        print(f'File error: {exc}')
        return

    answer = _ask_llm(client, messages, stream=stream)

    if answer is not None:
        session.save_answer(answer)


def _run_chunk_mode(
    client: LLMClient,
    session: ChatSession,
    command: str,
    *,
    stream: bool,
) -> None:
    try:
        options = parse_chunk_command(command)
    except ChunkCommandError as exc:
        print(f'Chunk error: {exc}')
        return

    path_input = input('File path: ').strip()
    if path_input == _EXIT_COMMAND:
        return

    prompt = input('Prompt for each chunk: ').strip()
    if prompt == _EXIT_COMMAND:
        return

    try:
        text = read_text_file(Path(path_input).expanduser())
        chunks = split_text(text, options)
    except (FileInjectionError, ChunkCommandError) as exc:
        print(f'Chunk error: {exc}')
        return

    print('Starting file processing.')

    for index, chunk in enumerate(chunks, start=1):
        if not options.auto_confirm and index > 1:
            next_input = input('Press Enter for the next chunk or \\q to exit: ')
            if next_input.strip() == _EXIT_COMMAND:
                return

        print(f'\n Chunk {index}/{len(chunks)}')

        messages = session.chunk_message(prompt, chunk)
        answer = _ask_llm(client, messages, stream=stream)

        if answer is None:
            return

    print('File processing finished.')


def _ask_llm(
    client: LLMClient,
    messages: list[OpenAIMessage],
    *,
    stream: bool,
) -> str | None:
    try:
        if stream:
            return _ask_llm_stream(client, messages)

        answer = client.complete(messages)
        print(answer)
        return answer
    except KeyboardInterrupt:
        print('\nRequest interrupted.')
        return None
    except LLMError as exc:
        print(f'LLM error: {exc}')
        return None


def _ask_llm_stream(client: LLMClient, messages: list[OpenAIMessage]) -> str:
    parts: list[str] = []

    for part in client.stream_complete(messages):
        print(part, end='', flush=True)
        parts.append(part)

    print()
    return ''.join(parts)


def _clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')