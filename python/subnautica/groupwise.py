from collections.abc import Iterable, Generator
from collections import deque


def groupwise[T](iterable: Iterable[T], /, n: int) -> Generator[tuple[T, ...]]:
    accum = deque((), n)
    for element in iterable:
        accum.append(element)  # type: ignore
        if len(accum) == n:
            yield tuple(accum)
