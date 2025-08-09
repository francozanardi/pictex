from functools import wraps
from collections import defaultdict
from typing import Optional

class _CachedPropertyDescriptor:

    def __init__(self, func, group):
        self._func = func
        self._group = group
        self._cache_attr_name = f"_cache_{func.__name__}"
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if hasattr(instance, self._cache_attr_name):
            return getattr(instance, self._cache_attr_name)

        value = self._func(instance)
        setattr(instance, self._cache_attr_name, value)
        instance._cache_registry[self._group].add(self._cache_attr_name)

        return value

def cached_property(group: str = 'ungrouped'):
    def decorator(func):
        return _CachedPropertyDescriptor(func, group)
    return decorator

def cached_method(group: str = 'ungrouped'):
    
    def decorator(func):
        cache_attr_name = f"_cache_{func.__name__}"

        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            if not hasattr(instance, cache_attr_name):
                setattr(instance, cache_attr_name, {})

                if not hasattr(instance, '_cache_registry'):
                    instance._cache_registry = defaultdict(set)
                instance._cache_registry[group].add(cache_attr_name)

            cache = getattr(instance, cache_attr_name)
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                return cache[key]

            result = func(instance, *args, **kwargs)
            cache[key] = result
            return result

        return wrapper
    
    return decorator

class Cacheable:
    def __init__(self) -> None:
        self._cache_registry = defaultdict(set)
    
    def clear_cache(self, filter_by_group: Optional[str] = None) -> None:
        items_to_remove = []
        if filter_by_group is None:
            items_to_remove = [key for cache_keys in self._cache_registry.values() for key in cache_keys]
            self._cache_registry.clear()
        elif filter_by_group in self._cache_registry:
            items_to_remove = self._cache_registry[filter_by_group]
            del self._cache_registry[filter_by_group]

        for item in items_to_remove:
            delattr(self, item)
