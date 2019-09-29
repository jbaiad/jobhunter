from datetime import datetime

import pandas as pd

from jobhunter.daos import common
from jobhunter.utils import mixins


class AbstractJobReader(metaclass=mixins.NotInstantiableMeta):
    @classmethod
    def get_jobs(cls,
                 company: common.Filterable[str] = None,
                 employment_type: common.Filterable[str] = None,
                 location: common.Filterable[str] = None,
                 latest_post_date: common.Filterable[datetime] = None,
                 is_active: common.Filterable[bool] = True
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
