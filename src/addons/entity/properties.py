from abc import ABC, abstractmethod
from typing import Any

class EntityProperties(ABC):
    """Base class for dynamically creating the new entity properties"""
    @abstractmethod
    def get_name(self) -> str:
        ...
    @abstractmethod
    def build_self(self) -> dict[str, Any]:
        ...

class RangedProperty(EntityProperties):
    def __init__(self, name: str, items: list[Any], namespace: str = 'custom'):
        self.__name = f'{namespace}:{name}'
        self.__items = items

    def get_name(self) -> str:
        return self.__name

    def build_self(self) -> dict[str, Any]:
        return {
            "client_sync": True,
            "type": "int",
            "range": [0, len(self.__items) - 1],
            "default": 0
        }

class StringProperty(EntityProperties):
    def __init__(self, name: str, items: list[str], namespace: str = 'custom'):
        self.__name = f'{namespace}:{name}'
        self.__items = items

    def get_name(self) -> str:
        return self.__name

    def build_self(self) -> dict[str, Any]:
        return {
            "client_sync": True,
            "type": "enum",
            "values": self.__items,
            "default": self.__items[0]
        }

class PropertyFactory:
    items: dict[str, EntityProperties] = {}

    @staticmethod
    def register(key: str, cls: EntityProperties):
        PropertyFactory.items[key] = cls

    @staticmethod
    def build(key: str, *args, **kwargs) -> EntityProperties:
        builder = PropertyFactory.items.get(key)
        if builder is not None:
            return builder(*args, **kwargs)
        raise ValueError(f'{key} is not a valid entity property type!')

PropertyFactory.register("int", RangedProperty)
PropertyFactory.register("enum", StringProperty)