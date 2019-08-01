import pkgutil
import sys
from typing import Iterable

def import_all_from_submodules(excluded_modules: Iterable[str] = []) -> None:
    frame = sys._getframe(1)
    frame.f_globals['__all__'] = getattr(frame.f_globals, '__all__', [])
    package_name = frame.f_globals['__name__']
    package_path = frame.f_globals['__path__']

    for loader, submodule_name, _ in pkgutil.walk_packages(package_path):
        if submodule_name in excluded_modules:
            continue

        submodule = loader.find_module(submodule_name)\
                          .load_module(submodule_name)
        for attr_name in getattr(submodule, '__all__', []):
            attr = getattr(submodule, attr_name)
            attr.__module__ = f'{package_name}.{attr.__module__}'
            frame.f_globals[attr_name] = attr

