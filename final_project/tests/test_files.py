from pathlib import Path

import pytest

from gigavibe.errors import FileInjectionError
from gigavibe.files import inject_files, read_text_file


def write_file(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding='utf-8')
    return path


def test_text_without_file_references_does_not_change() -> None:
    text = 'hello world'

    assert inject_files(text) == text


def test_injects_one_file(tmp_path: Path) -> None:
    path = write_file(tmp_path, 'main.py', 'print(1)')

    result = inject_files(f'check this @::{path}::')

    assert result == 'check this \nprint(1)'


def test_injects_several_files(tmp_path: Path) -> None:
    first = write_file(tmp_path, 'first.txt', 'one')
    second = write_file(tmp_path, 'second.txt', 'two')

    result = inject_files(f'files: @::{first}:: and @::{second}::')

    assert result == 'files: \none and \ntwo'


def test_missing_file_fails(tmp_path: Path) -> None:
    path = tmp_path / 'missing.txt'

    with pytest.raises(FileInjectionError):
        inject_files(f'check @::{path}::')


def test_directory_fails(tmp_path: Path) -> None:
    with pytest.raises(FileInjectionError):
        inject_files(f'check @::{tmp_path}::')


def test_large_file_fails(tmp_path: Path) -> None:
    path = write_file(tmp_path, 'large.txt', 'abcdef')

    with pytest.raises(FileInjectionError):
        read_text_file(path, max_size=5)


def test_invalid_utf8_file_fails(tmp_path: Path) -> None:
    path = tmp_path / 'binary.bin'
    path.write_bytes(b'\xff\xfe\x00')

    with pytest.raises(FileInjectionError):
        inject_files(f'check @::{path}::')


def test_keeps_text_around_reference(tmp_path: Path) -> None:
    path = write_file(tmp_path, 'data.txt', 'content')

    result = inject_files(f'before @::{path}:: after')

    assert result == 'before \ncontent after'