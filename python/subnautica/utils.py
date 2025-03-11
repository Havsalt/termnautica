import random
from collections.abc import Iterable, Generator
from collections import deque


def groupwise[T](iterable: Iterable[T], /, n: int) -> Generator[tuple[T, ...]]:
    accum = deque((), n)
    for element in iterable:
        accum.append(element)  # type: ignore
        if len(accum) == n:
            yield tuple(accum)


def randf(a: float, b: float, /) -> float:
    return random.random() * (b - a) + a


def move_toward(start: float, target: float, change: float) -> float:
    if abs(target - start) <= change:
        return target
    return start + change if start < target else start - change
