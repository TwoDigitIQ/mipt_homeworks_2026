import pytest

from chunks import (
    ChunkOptions,
    is_chunk_command,
    parse_chunk_command,
    split_by_length,
    split_by_paragraphs,
    split_text,
)
from errors import ChunkCommandError


def test_detects_chunk_command() -> None:
    assert is_chunk_command('/filechunk')
    assert is_chunk_command('/file_chunk')
    assert is_chunk_command('/filechunk paragraph=3')
    assert not is_chunk_command('/reset')


def test_parses_default_filechunk() -> None:
    assert parse_chunk_command('/filechunk') == ChunkOptions(
        mode='paragraph',
        value=1,
        auto_confirm=False,
    )


def test_parses_default_file_chunk_alias() -> None:
    assert parse_chunk_command('/file_chunk') == ChunkOptions(
        mode='paragraph',
        value=1,
        auto_confirm=False,
    )


def test_parses_paragraph_count() -> None:
    assert parse_chunk_command('/filechunk paragraph=3') == ChunkOptions(
        mode='paragraph',
        value=3,
        auto_confirm=False,
    )


def test_parses_length() -> None:
    assert parse_chunk_command('/filechunk len=150') == ChunkOptions(
        mode='len',
        value=150,
        auto_confirm=False,
    )


def test_parses_auto_confirm() -> None:
    assert parse_chunk_command('/filechunk paragraph=3 -y') == ChunkOptions(
        mode='paragraph',
        value=3,
        auto_confirm=True,
    )


def test_parses_auto_confirm_before_option() -> None:
    assert parse_chunk_command('/filechunk -y len=150') == ChunkOptions(
        mode='len',
        value=150,
        auto_confirm=True,
    )


@pytest.mark.parametrize(
    'command',
    [
        '',
        '/unknown',
        '/filechunk abc',
        '/filechunk paragraph=0',
        '/filechunk paragraph=-1',
        '/filechunk paragraph=abc',
        '/filechunk len=0',
        '/filechunk len=-1',
        '/filechunk len=abc',
    ],
)
def test_invalid_command_fails(command: str) -> None:
    with pytest.raises(ChunkCommandError):
        parse_chunk_command(command)


def test_splits_by_one_paragraph() -> None:
    text = 'first\nsecond\nthird'

    assert split_by_paragraphs(text, 1) == ['first', 'second', 'third']


def test_splits_by_several_paragraphs() -> None:
    text = 'first\nsecond\nthird\nfourth'

    assert split_by_paragraphs(text, 2) == [
        'first\nsecond',
        'third\nfourth',
    ]


def test_ignores_empty_paragraphs() -> None:
    text = 'first\n\nsecond\n   \nthird'

    assert split_by_paragraphs(text, 1) == ['first', 'second', 'third']


def test_split_by_paragraphs_rejects_invalid_count() -> None:
    with pytest.raises(ChunkCommandError):
        split_by_paragraphs('text', 0)


def test_splits_by_length() -> None:
    assert split_by_length('abcdef', 2) == ['ab', 'cd', 'ef']


def test_splits_by_length_with_tail() -> None:
    assert split_by_length('abcde', 2) == ['ab', 'cd', 'e']


def test_split_by_length_rejects_invalid_length() -> None:
    with pytest.raises(ChunkCommandError):
        split_by_length('text', 0)


def test_split_text_uses_paragraph_mode() -> None:
    options = ChunkOptions(mode='paragraph', value=2, auto_confirm=False)

    assert split_text('one\ntwo\nthree', options) == ['one\ntwo', 'three']


def test_split_text_uses_length_mode() -> None:
    options = ChunkOptions(mode='len', value=3, auto_confirm=False)

    assert split_text('abcdef', options) == ['abc', 'def']