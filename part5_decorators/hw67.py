import json
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar, cast
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime) -> None:
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 1,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        errors: list[ValueError] = []

        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.block_time: datetime | None = None
        self.blocked_until: datetime | None = None
        self.fails = 0

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        func_name = f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = datetime.now(UTC)
            self._check_block(func_name, now)

            try:
                result = func(*args, **kwargs)
            except self.triggers_on as error:
                self._handle_trigger_error(func_name, error, now)

            self.fails = 0
            return result

        return cast("CallableWithMeta[P, R_co]", wrapper)

    def _reset(self) -> None:
        self.block_time = None
        self.blocked_until = None
        self.fails = 0

    def _handle_trigger_error(self, func_name: str, error: Exception, now: datetime) -> None:
        self.fails += 1

        if self.fails < self.critical_count:
            raise error

        self.block_time = now
        self.blocked_until = now + timedelta(seconds=self.time_to_recover)
        raise BreakerError(func_name, now) from error

    def _check_block(self, func_name: str, now: datetime) -> None:
        if self.blocked_until is None:
            return

        if now < self.blocked_until:
            block_time = now if self.block_time is None else self.block_time
            raise BreakerError(func_name, block_time)

        self._reset()


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
