from enum import Enum
from typing import Iterable

def enum_values(cls: type[Enum]) -> Iterable[str]:
    return [member.value for member in cls]
