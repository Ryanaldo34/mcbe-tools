from addons.errors import BadDataInputExcep
from addons.helpers.file_handling import write_to_file


class EntityBehaviors:

    def __init__(self, bp_data: dict):
        self.__data: dict = bp_data
        self.__id: str = self.__data.get('minecraft:entity').get('description').get('identifier')
        self.__real_name: str = self.__id.split(':')[-1]

    @property
    def data(self):
        return self.__data

    @property
    def identifier(self):
        if self.__id is not None:
            return self.__id
        else:
            raise BadDataInputExcep('The Entity is missing an identifier and cannot be defined!')

    @property
    def real_name(self):
        return self.__real_name

    @property
    def is_spawnable(self) -> bool:
        return self.__data.get('minecraft:entity').get('description').get('is_spawnable')

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

