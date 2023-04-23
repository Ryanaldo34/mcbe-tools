from pathlib import Path
from addons.errors import BadDataInputExcep
from addons.helpers import write_to_file
from typing import Any
from addons.custom.component import component_registry, CustomComponent
from addons.entity.properties import EntityProperties

class EntityBehaviors:
    def __init__(self, bp_data: dict):
        self.__data: dict[str, dict[str, Any]] = bp_data
        self.__id: str = self.__data.get('minecraft:entity').get('description').get('identifier')
        self.__real_name: str = self.__id.split(':')[-1]

    @property
    def data(self) -> dict[str, dict[str, Any]]:
        return self.__data

    @property
    def identifier(self) -> str:
        if self.__id is not None:
            return self.__id
        else:
            raise BadDataInputExcep('The Entity is missing an identifier and cannot be defined!')

    @property
    def real_name(self):
        return self.__real_name

    @property
    def is_spawnable(self) -> bool:
        self.__data.get('minecraft:entity').get('description').get('is_spawnable')
        return self.__data.get('minecraft:entity').get('description').get('is_spawnable')

    def add_property(self, property: EntityProperties):
        name = property.get_name()
        data = property.build_self()
        if self.__data['minecraft:entity']['description'].get('properties') is not None:
            self.__data['minecraft:entity']['description']['properties'][name] = data
        else:
            self.__data['minecraft:entity']['description']['properties'] = {}
            self.__data['minecraft:entity']['description']['properties'][name] = data

    def build(self, build_path: Path) -> None:
        """
        Builds out the custom components in the file
        
        :param build_path: The path to the entity's behavior file
        """
        cgs: dict[str, Any] | None = self.__data['minecraft:entity'].get('component_groups')
        if cgs is not None:
            for name, group in cgs.items():
                for k in list(group):
                    if k.startswith(component_registry.namespace):
                        passed_properties = self.__data.pop(k)
                        component = component_registry.get_component(k.split(':')[-1])
                        root = self.__data['minecraft:entity']['component_groups'][name]
                        component.build_self(root=root, properties=passed_properties)
        components: dict[str, Any] = self.__data['minecraft:entity']['components']
        for k in list(components):
            if k.startswith(component_registry.namespace):
                passed_properties = self.__data['minecraft:entity']['components'].pop(k)
                Component = component_registry.get_component(k.split(':')[-1])
                component: CustomComponent = Component() # returns the component class corresponding to the component name
                component.build_self(root=components, properties=passed_properties)

        write_to_file(build_path, self.__data)

    def write_lang_defs(self, lang_file_path: str) -> list[str]:
        """
        Creates a list of the required lang definitions from the behavior components on an entity

        :returns: a list of the lang definitions in "translation.key=Name Required" format
        """
        with open(lang_file_path, 'a+') as lang_file:
            lang_data = lang_file.readlines()
            ride_hint = f'action.hint.exit.{self.identifier}=Tap Sneak To Exit {self.__real_name}\n'
            components = self.__data.get('minecraft:entity').get('components')
            component_groups = self.__data.get('minecraft:entity').get('component_groups')

            if component_groups:
                for cg in component_groups.values():
                    if 'minecraft:rideable' in cg and ride_hint not in lang_data:
                        lang_file.write(ride_hint)
                        return lang_file.readlines()

            if components:
                if components.get('minecraft:rideable') and ride_hint not in lang_data:
                    lang_file.write(ride_hint)
                    return lang_file.readlines()

            return lang_file.readlines()