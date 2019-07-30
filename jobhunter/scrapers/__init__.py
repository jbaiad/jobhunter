import pkgutil


__all__ = []

for loader, module_name, _ in  pkgutil.walk_packages(__path__):
    if module_name != 'interfaces':
        _module = loader.find_module(module_name).load_module(module_name)
        __all__.extend(_module.__all__)
        for attr_name in _module.__all__:
            attr = _module.__getattribute__(attr_name)
            attr.__module__ = f'{__name__}.{attr.__module__}'
            globals()[attr_name] = attr

