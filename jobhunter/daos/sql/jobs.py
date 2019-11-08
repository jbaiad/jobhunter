from datetime import datetime

import pandas as pd
from sqlalchemy import func

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
                 url: daos_common.Filterable[str] = None,
                ) -> pd.DataFrame:
        session = common.Session()
        rows = common.apply_filters(session.query(Job), [
            (Job.company.__eq__, company),
            (Job.employment_type.__eq__, employment_type),
            (Job.location.__eq__, location),
            (Job.date_posted.__le__, latest_post_date),
            (Job.is_active.__eq__, is_active),
            (Job.url.__eq__, url)
        ]).all()

        if rows:
            return pd.DataFrame([
                row.__dict__ for row in rows
            ]).drop('_sa_instance_state', axis=1)
        else:
            return pd.DataFrame(columns=Job.__table__.columns.keys())


class JobWriter(interfaces.AbstractJobWriter):
    @classmethod
    def write_jobs(cls, jobs: pd.DataFrame) -> None:
        session = common.Session()
        max_job_id = (session.query(func.max(Job.id)).first()[0] or 0) + 1
        jobs = jobs.filter(Job.__table__.columns.keys(), axis=1).set_index('url')
        current_jobs = JobReader.get_jobs(url=jobs.index, is_active=True).set_index('url')

        inserted_jobs = jobs.loc[jobs.index.difference(current_jobs.index)]
        inserted_jobs['id'] = range(max_job_id, max_job_id + len(inserted_jobs))
        inserted_jobs['date_posted'] = inserted_jobs['date_posted'].fillna(datetime.today())
        session.bulk_insert_mappings(Job, inserted_jobs.reset_index().to_dict('records'))

        updated_jobs = jobs.loc[jobs.index.intersection(current_jobs.index)]
        updated_jobs['id'] = current_jobs.loc[updated_jobs.index, 'id']
        updated_jobs['date_posted'] = current_jobs.loc[updated_jobs.index, 'date_posted'].fillna(datetime.today())
        for idx, current_job in current_jobs.loc[updated_jobs.index].iterrows():
            if current_job.equals(updated_jobs.loc[idx].reindex_like(current_job)):
                updated_jobs.drop(index=idx, inplace=True)
        
        session.bulk_update_mappings(Job, updated_jobs.reset_index().to_dict('records'))

        session.commit()

        return inserted_jobs, updated_jobs

    @classmethod
    def mark_inactive_jobs(cls, jobs: pd.DataFrame) -> pd.DataFrame:
        active_jobs = JobReader.get_jobs(is_active=True, company=jobs['company'], url=jobs['url'])
        inactive_jobs = active_jobs[~active_jobs.url.isin(jobs['url'])]
        inactive_jobs.is_active = False
        cls.write_jobs(inactive_jobs)

        return inactive_jobs


__all__ = ['JobReader', 'JobWriter']
