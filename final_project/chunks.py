from dataclasses import dataclass
from typing import Literal

from errors import ChunkCommandError


ChunkMode = Literal['paragraph', 'len']
_CHUNK_COMMANDS = {'/filechunk', '/file_chunk'}


@dataclass(frozen=True, slots=True)
class ChunkOptions:
    mode: ChunkMode = 'paragraph'
    value: int = 1
    auto_confirm: bool = False


def is_chunk_command(command: str) -> bool:
    parts = command.split(maxsplit=1)
    return bool(parts) and parts[0] in _CHUNK_COMMANDS


def parse_chunk_command(command: str) -> ChunkOptions:
    parts = command.split()

    if not parts or parts[0] not in _CHUNK_COMMANDS:
        raise ChunkCommandError('unknown chunk command')

    mode: ChunkMode = 'paragraph'
    value = 1
    auto_confirm = False

    for option in parts[1:]:
        if option == '-y':
            auto_confirm = True
            continue

        name, separator, raw_value = option.partition('=')
        if separator != '=' or name not in {'paragraph', 'len'}:
            raise ChunkCommandError(f'unknown chunk option: {option}')

        value = _positive_int(raw_value, name)
        mode = 'paragraph' if name == 'paragraph' else 'len'

    return ChunkOptions(mode=mode, value=value, auto_confirm=auto_confirm)


def split_text(text: str, options: ChunkOptions) -> list[str]:
    if options.mode == 'paragraph':
        return split_by_paragraphs(text, options.value)

    return split_by_length(text, options.value)


def split_by_paragraphs(text: str, paragraph_count: int) -> list[str]:
    if paragraph_count <= 0:
        raise ChunkCommandError('paragraph must be a positive integer')

    paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
    return [
        '\n'.join(paragraphs[index : index + paragraph_count])
        for index in range(0, len(paragraphs), paragraph_count)
    ]


def split_by_length(text: str, length: int) -> list[str]:
    if length <= 0:
        raise ChunkCommandError('len must be a positive integer')

    return [text[index : index + length] for index in range(0, len(text), length)]


def _positive_int(value: str, name: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise ChunkCommandError(f'{name} must be a positive integer') from exc

    if result <= 0:
        raise ChunkCommandError(f'{name} must be a positive integer')

    return result