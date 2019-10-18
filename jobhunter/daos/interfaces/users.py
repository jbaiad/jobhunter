import abc

class AbstractUser:
    @property
    @abc.abstractmethod
    def is_authenticated(self):
        pass

    @property
    @abc.abstractmethod
    def is_active(self):
        pass

    @property
    @abc.abstractmethod
    def is_anonymous(self):
        pass

    @abc.abstractmethod
    def get_id(self):
        pass

__all__ = ['AbstractUser']
