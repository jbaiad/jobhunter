import abc

from jobhunter.utils import mixins


class AbstractJobWatchReader(metaclass=mixins.NotInstantiableMeta):
    @abc.abstractclassmethod
    def job_is_watched_by_user(cls, user: str, job: str):
        pass


class AbstractJobWatchWriter(metaclass=mixins.NotInstantiableMeta):
    @abc.abstractclassmethod
    def remove_from_watchlist(cls, user: str, job: str):
        pass

    @abc.abstractclassmethod
    def add_to_watchlist(cls, user: str, job: str):
        pass


__all__ = ['AbstractJobWatchReader', 'AbstractJobWatchWriter']
