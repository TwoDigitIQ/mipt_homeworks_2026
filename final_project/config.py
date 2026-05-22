from dataclasses import dataclass
import os
from pathlib import Path
from typing import TypeAlias

import yaml

from errors import ConfigError


ConfigData: TypeAlias = dict[str, object]

_DEFAULT_MODEL = 'gemma3:270m'
_DEFAULT_TEMPERATURE = 0.7
_DEFAULT_STREAM = True

_ENV_KEYS = {
    'API_KEY': 'api_key',
    'API_HOST': 'api_host',
    'MODEL': 'model',
    'LIMIT_MESSAGE': 'limit_message',
    'LIMIT_MESSAGES': 'limit_message',
    'LIMIT_CHARS': 'limit_chars',
    'TEMPERATURE': 'temperature',
    'STREAM': 'stream',
}

_TRUE_VALUES = {'1', 'true', 'yes', 'y', 'on'}
_FALSE_VALUES = {'0', 'false', 'no', 'n', 'off'}


@dataclass(frozen=True, slots=True)
class AppConfig:
    api_key: str
    api_host: str
    model: str
    limit_message: int | None
    limit_chars: int | None
    temperature: float
    system_prompt: str | None
    stream: bool


def load_config(config_path: str | Path = 'config.yaml') -> AppConfig:
    config = _read_yaml(Path(config_path))
    config.update(_read_env())

    if not config:
        raise ConfigError('config.yaml or environment variables are required')

    return AppConfig(
        api_key=_required_str(config, 'api_key'),
        api_host=_required_str(config, 'api_host'),
        model=_str(config, 'model') or _DEFAULT_MODEL,
        limit_message=_positive_int(config, 'limit_message'),
        limit_chars=_positive_int(config, 'limit_chars'),
        temperature=_temperature(config),
        system_prompt=_str(config, 'system_prompt'),
        stream=_bool(config, 'stream', default=_DEFAULT_STREAM),
    )


def _read_yaml(path: Path) -> ConfigData:
    if not path.exists():
        return {}

    try:
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f'cannot read config file: {path}') from exc

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ConfigError('config.yaml must contain a mapping')

    result: ConfigData = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ConfigError('config keys must be strings')
        result[key] = value

    return result


def _read_env() -> ConfigData:
    result: ConfigData = {}

    for env_name, config_name in _ENV_KEYS.items():
        value = os.environ.get(env_name)
        if value is not None:
            result[config_name] = value

    return result


def _required_str(config: ConfigData, key: str) -> str:
    value = _str(config, key)
    if value is None:
        raise ConfigError(f'{key} is required')
    return value


def _str(config: ConfigData, key: str) -> str | None:
    value = config.get(key)

    if value is None:
        return None

    if isinstance(value, str) and value.strip():
        return value.strip()

    raise ConfigError(f'{key} must be a non-empty string')


def _positive_int(config: ConfigData, key: str) -> int | None:
    value = config.get(key)

    if value is None or value == '':
        return None

    if isinstance(value, bool):
        raise ConfigError(f'{key} must be a positive integer')

    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        try:
            result = int(value)
        except ValueError as exc:
            raise ConfigError(f'{key} must be a positive integer') from exc
    else:
        raise ConfigError(f'{key} must be a positive integer')

    if result <= 0:
        raise ConfigError(f'{key} must be a positive integer')

    return result


def _temperature(config: ConfigData) -> float:
    value = config.get('temperature')

    if value is None or value == '':
        return _DEFAULT_TEMPERATURE

    if isinstance(value, bool):
        raise ConfigError('temperature must be a number')

    if isinstance(value, int | float):
        result = float(value)
    elif isinstance(value, str):
        try:
            result = float(value)
        except ValueError as exc:
            raise ConfigError('temperature must be a number') from exc
    else:
        raise ConfigError('temperature must be a number')

    if not 0 <= result <= 1:
        raise ConfigError('temperature must be between 0 and 1')

    return result


def _bool(config: ConfigData, key: str, *, default: bool) -> bool:
    value = config.get(key)

    if value is None or value == '':
        return default

    if isinstance(value, bool):
        return value

    if not isinstance(value, str):
        raise ConfigError(f'{key} must be a boolean')

    normalized = value.strip().lower()

    if normalized in _TRUE_VALUES:
        return True

    if normalized in _FALSE_VALUES:
        return False

    raise ConfigError(f'{key} must be a boolean')