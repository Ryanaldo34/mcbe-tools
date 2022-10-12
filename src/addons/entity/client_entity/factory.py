from addons.entity.client_entity.versions import ClientEntityBase


class ClientEntityFactory:
    def __init__(self):
        self.__builders = {}

    def register_builder(self, fv: str, ce):
        self.__builders[fv] = ce

    def create(self, fv: str, *args, **kwargs) -> ClientEntityBase:
        builder = self.__builders.get(fv)
        if not builder:
            raise ValueError(fv)

        return builder(*args, **kwargs)