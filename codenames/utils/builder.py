from __future__ import annotations

import random
from typing import Collection, NamedTuple


class ExtractResult[T](NamedTuple):
    remaining: tuple[T, ...]
    sample: tuple[T, ...]


def extract_random_subset[T](elements: Collection[T], subset_size: int) -> ExtractResult[T]:
    elements = tuple(elements)
    sample = tuple(random.sample(elements, k=subset_size))
    remaining = tuple(e for e in elements if e not in sample)
    return ExtractResult(remaining=remaining, sample=sample)
