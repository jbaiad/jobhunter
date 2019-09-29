from datetime import datetime

import pandas as pd

import jobhunter.daos.interfaces.jobs as interfaces
import jobhunter.daos.common as daos_common
from jobhunter.daos.sql import common
from jobhunter.daos.sql.schemata import Job


class JobReader(interfaces.AbstractJobReader):
    @classmethod
    def get_jobs(cls,
                 company: daos_common.Filterable[str] = None,
                 employment_type: daos_common.Filterable[str] = None,
                 location: daos_common.Filterable[str] = None,
                 latest_post_date: daos_common.Filterable[datetime] = None,
                 is_active: daos_common.Filterable[bool] = True,
                ) -> pd.DataFrame:
        session = common.Session()
        rows = common.apply_filters(session.query(Job), [
            (Job.company.__eq__, company),
            (Job.employment_type.__eq__, employment_type),
            (Job.location.__eq__, location),
            (Job.date_posted.__le__, latest_post_date),
            (Job.is_active.__eq__, is_active)
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
        current_urls = set(row[0] for row in session.query(Job.url).distinct())
        session.bulk_update_mappings(Job, jobs[jobs.url.isin(current_urls)].to_dict('records'))
        session.bulk_insert_mappings(Job, jobs[~jobs.url.isin(current_urls)].to_dict('records'))
        session.commit()

    @classmethod
    def mark_inactive_jobs(cls, jobs: pd.DataFrame) -> pd.DataFrame:
        active_jobs = JobReader.get_jobs(is_active=True, company=jobs.company)
        inactive_jobs = active_jobs[~active_jobs.url.isin(jobs)]
        inactive_jobs.is_active = False
        cls.write_jobs(inactive_jobs)

        return inactive_jobs


__all__ = ['JobReader', 'JobWriter']
