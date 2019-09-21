from datetime import datetime
from typing import Iterable, Optional, Union

import pandas as pd

from jobhunter.utils import mixins


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

    @classmethod
    def mark_inactive_jobs(cls, jobs: pd.DataFrame) -> pd.DataFrame:
        pass


__all__ = ['AbstractJobReader', 'AbstractJobWriter']
