import sqlalchemy as sqla

from jobhunter.daos import interfaces
from jobhunter.daos.sql import common
from jobhunter.daos.sql.schemata import JobWatch


class JobWatchReader(interfaces.AbstractJobWatchReader):
    @classmethod
    def job_is_watched_by_user(cls, user: str, job_id: str):
        session = common.Session()
        watch = session.query(JobWatch).filter(sqla.and_(JobWatch.username == user, JobWatch.job_id == job_id)).first()
        return watch is not None

class JobWatchWriter(interfaces.AbstractJobWatchWriter):
    @classmethod
    def remove_from_watchlist(cls, user: str, job_id: str):
        session = common.Session()
        session.query(JobWatch).filter(sqla.and_(JobWatch.username == user, JobWatch.job_id == job_id)).delete()
        session.commit()
    
    @classmethod
    def add_to_watchlist(cls, user: str, job_id: str):
        session = common.Session()
        session.merge(JobWatch(username=user, job_id=job_id))
        session.commit()


__all__ = ['JobWatchReader', 'JobWatchWriter']
