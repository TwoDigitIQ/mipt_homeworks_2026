from pathlib import Path
import re
from re import Match

from gigavibe.errors import FileInjectionError


_FILE_PATTERN = re.compile(r'@::(.*?)::')
_MAX_FILE_SIZE = 5 * 1024 * 1024


def inject_files(text: str) -> str:
    def replace(match: Match[str]) -> str:
        path = Path(match.group(1)).expanduser()
        return '\n' + read_text_file(path)

    return _FILE_PATTERN.sub(replace, text)


def read_text_file(path: Path, max_size: int = _MAX_FILE_SIZE) -> str:
    if not path.exists():
        raise FileInjectionError(f'file not found: {path}')

    if not path.is_file():
        raise FileInjectionError(f'not a file: {path}')

    try:
        size = path.stat().st_size
    except OSError as exc:
        raise FileInjectionError(f'cannot read file info: {path}') from exc

    if size > max_size:
        raise FileInjectionError(f'file is too large: {path}')

    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError as exc:
        raise FileInjectionError(f'file is not a valid utf-8 text file: {path}') from exc
    except OSError as exc:
        raise FileInjectionError(f'cannot read file: {path}') from exc