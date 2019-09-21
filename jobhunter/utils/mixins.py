import abc


class NotInstantiableMeta(abc.ABCMeta):
    def __call__(cls, *arg, **kwargs):
        raise TypeError(f'{cls.__module__}.{cls.__name__} is not instantiable!')
