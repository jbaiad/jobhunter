from typing import Iterable, Optional, TypeVar, Union

T = TypeVar('T')
Filterable = Optional[Union[T, Iterable[T]]]
