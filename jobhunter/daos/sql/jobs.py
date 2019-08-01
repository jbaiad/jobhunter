from datetime import datetime
import operator
from typing import Iterable, Optional, Union

import pandas as pd

import jobhunter.daos.interfaces.jobs as interfaces
import jobhunter.daos.sql.common as common
from jobhunter.daos.sql.schemata import Job


class JobReader(interfaces.AbstractJobReader):
    @classmethod
    def get_jobs(cls,
                company : common.Filterable[str] = None,
                employment_type: common.Filterable[str] = None,
                location: common.Filterable[str] = None,
                latest_post_date: common.Filterable[datetime] = None,
                ) -> pd.DataFrame:
        session = common.Session()
        rows = common.apply_filters(session.query(Job), [
            (Job.company.__eq__, company),
            (Job.employment_type.__eq__, employment_type),
            (Job.location.__eq__, location),
            (Job.date_posted.__le__, latest_post_date),
        ]).all()
        
        
        if rows:
            return pd.DataFrame([
                row.__dict__ for row in rows
            ]).drop('_sa_instance_state', axis=1)
        else:
            return pd.DataFrame()


class JobWriter(interfaces.AbstractJobWriter):
    @classmethod
    def write_jobs(cls, jobs: pd.DataFrame) -> None:
       session = common.Session()
       session.bulk_insert_mappings(Job, jobs.to_dict('records'))
       session.commit()

__all__ = ['JobReader', 'JobWriter']

