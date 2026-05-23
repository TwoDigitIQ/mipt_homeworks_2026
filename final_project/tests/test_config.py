from pathlib import Path

import pytest

from gigavibe.config import load_config
from gigavibe.errors import ConfigError


_ENV_NAMES = (
    'API_KEY',
    'API_HOST',
    'MODEL',
    'LIMIT_MESSAGE',
    'LIMIT_MESSAGES',
    'LIMIT_CHARS',
    'TEMPERATURE',
    'STREAM',
)


def clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def write_config(tmp_path: Path, content: str) -> Path:
    path = tmp_path / 'config.yaml'
    path.write_text(content, encoding='utf-8')
    return path


def test_loads_yaml_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_env(monkeypatch)
    path = write_config(
        tmp_path,
        """
api_key: yaml-key
api_host: http://localhost:11434/v1/
model: test-model
limit_message: 10
limit_chars: 2000
temperature: 0.5
system_prompt: Act like an assistant
stream: false
""",
    )

    config = load_config(path)

    assert config.api_key == 'yaml-key'
    assert config.api_host == 'http://localhost:11434/v1/'
    assert config.model == 'test-model'
    assert config.limit_message == 10
    assert config.limit_chars == 2000
    assert config.temperature == 0.5
    assert config.system_prompt == 'Act like an assistant'
    assert config.stream is False


def test_env_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_env(monkeypatch)
    path = write_config(
        tmp_path,
        """
api_key: yaml-key
api_host: yaml-host
model: yaml-model
""",
    )
    monkeypatch.setenv('API_KEY', 'env-key')
    monkeypatch.setenv('API_HOST', 'env-host')
    monkeypatch.setenv('MODEL', 'env-model')

    config = load_config(path)

    assert config.api_key == 'env-key'
    assert config.api_host == 'env-host'
    assert config.model == 'env-model'


def test_missing_config_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_env(monkeypatch)

    with pytest.raises(ConfigError):
        load_config(tmp_path / 'missing.yaml')


def test_missing_api_key_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_env(monkeypatch)
    path = write_config(
        tmp_path,
        """
api_host: http://localhost:11434/v1/
""",
    )

    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_api_host_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_env(monkeypatch)
    path = write_config(
        tmp_path,
        """
api_key: test-key
""",
    )

    with pytest.raises(ConfigError):
        load_config(path)


@pytest.mark.parametrize('temperature', ['-0.1', '1.1', 'abc'])
def test_invalid_temperature_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    temperature: str,
) -> None:
    clear_env(monkeypatch)
    path = write_config(
        tmp_path,
        f"""
api_key: test-key
api_host: test-host
temperature: {temperature}
""",
    )

    with pytest.raises(ConfigError):
        load_config(path)


@pytest.mark.parametrize('limit_value', ['0', '-1', 'abc'])
def test_invalid_limit_message_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    limit_value: str,
) -> None:
    clear_env(monkeypatch)
    path = write_config(
        tmp_path,
        f"""
api_key: test-key
api_host: test-host
limit_message: {limit_value}
""",
    )

    with pytest.raises(ConfigError):
        load_config(path)


def test_limit_messages_env_alias(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    clear_env(monkeypatch)
    monkeypatch.setenv('API_KEY', 'test-key')
    monkeypatch.setenv('API_HOST', 'test-host')
    monkeypatch.setenv('LIMIT_MESSAGES', '15')

    config = load_config(tmp_path / 'missing.yaml')

    assert config.limit_message == 15


def test_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clear_env(monkeypatch)
    path = write_config(
        tmp_path,
        """
api_key: test-key
api_host: test-host
""",
    )

    config = load_config(path)

    assert config.model == 'gemma3:270m'
    assert config.limit_message is None
    assert config.limit_chars is None
    assert config.temperature == 0.7
    assert config.system_prompt is None
    assert config.stream is True