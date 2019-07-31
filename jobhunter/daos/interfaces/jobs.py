import abc
from datetime import datetime
from typing import Iterable, Optional, Type, Union

import pandas as pd

import jobhunter.utils.mixins as mixins


class AbstractJobReader(metaclass=mixins.NotInstantiableMeta):
    @classmethod
    def get_jobs(cls, 
                 company: Optional[Union[str, Iterable[str]]] = None, 
                 employment_type: Optional[Union[str, Iterable[str]]] = None,
                 latest_post_date: Optional[Union[str, datetime]] = None,
                 ) -> pd.DataFrame:
        pass


class AbstractJobWriter(metaclass=mixins.NotInstantiableMeta):
    @classmethod
    def write_jobs(cls, jobs: pd.DataFrame) -> None:
        pass


__all__ = ['AbstractJobReader', 'AbstractJobWriter']

