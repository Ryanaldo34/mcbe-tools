from pathlib import Path
from addons.entity.behaviors import EntityBehaviors
from addons.helpers.file_handling import data_from_file, write_to_file
from .geo import Geometry

class Entity:
    """ 
    Used to encapsulate and handle data relating to an entity definition
    """
    def __init__(self,
                materials: dict[str, str],
                geometry: Geometry,
                bp_data: EntityBehaviors,
                *,
                textures: dict[str, str] = None,
                acs: dict[str, str] = None,
                anims: dict[str, str] = None,
                sounds: dict[str, str] = None,
                particles: dict[str, str] = None,
                spawn_egg = {
                    'texture': 'spawn_egg',
                    'texture_index': 0
                }
        ):
        self.identifier = bp_data.identifier
        self.name = bp_data.real_name
        self.__materials: dict[str, str] = materials
        self.__bp_data: EntityBehaviors = bp_data
        self.__material_names: list[str] = [f'Material.{x}' for x in list(self.__materials)]
        self.__geo_name_val_map: dict[str, str] = geometry.get_geos()
        self.__geo_names: list[str] = geometry.get_names()
        self.__bones = geometry.get_bones()
        self.__spawn_egg: dict = spawn_egg
        self.__textr_name_val_map: dict[str, str] = textures
        self.__anims: dict[str, str] = anims
        self.__acs: list[dict[str, str]] = acs
        self.__particles: dict[str, str] = particles
        self.__sounds: dict[str, str] = sounds
        self.__locators: dict = geometry.get_locators()

    @property
    def acs(self) -> list[dict[str, str]]:
        return self.__acs

    @property
    def anims(self) -> dict[str, str]:
        return self.__anims

    @property
    def behaviors(self) -> EntityBehaviors:
        return self.__bp_data

    @property
    def has_default_rc(self) -> bool:
        return all(x < 2 for x in [len(self.__material_names), len(self.__textr_name_val_map, len(self.geo_names))])

    @property
    def textr_paths(self) -> list[str]:
        if self.__textr_name_val_map is None:
            return None
        return list(self.__textr_name_val_map.values())

    @property
    def bones(self) -> list[str]:
        return self.__bones

    @property
    def geo_names(self) -> list[str]:
        return self.__geo_names

    @property
    def geometries(self) -> dict[str, str]:
        return self.__geo_name_val_map

    @property
    def locators(self) -> dict:
        return self.__locators

    @property
    def materials(self) -> dict:
        return self.__materials

    @property
    def material_names(self) -> list[str]:
        return self.__material_names

    @property
    def particles(self) -> dict[str, str]:
        return self.__particles

    @property
    def textures(self) -> dict[str, str]:
        return self.__textr_name_val_map

    @property
    def textr_names(self) -> list[str]:
        if self.__textr_name_val_map is None:
            return None
        return [f'Texture.{short_name}' for short_name in list(self.__textr_name_val_map)]

    @property
    def sounds(self) -> dict[str, str]:
        return self.__sounds

    @sounds.setter
    def sounds(self, sounds_dict: dict):
        if type(sounds_dict) != dict and sounds_dict is not None:
            raise ValueError('The Sounds Short-name: Value map needs to be a dictionary!')
        self.__sounds = sounds_dict

    @property
    def spawn_egg(self) -> dict:
        return self.__spawn_egg

    def write_lang(self, RP_PATH: Path) -> None:
        """
        Adds the required entity translation key definitions to the rp .lang file

        :param RP_PATH: The path to the resource pack the entity belongs to
        """
        lang_path = RP_PATH.joinpath('texts', 'en_US.lang')
        title = self.name.replace('_', ' ').title()
        translation = f'entity.{self.identifier}.name={title}\n'
        spawn_translation = f'item.spawn_egg.entity.{self.identifier}.name=Spawn {title}\n'
        with open(lang_path, 'a+') as lang_file:
            written_data = lang_file.readlines()

            if translation not in written_data:
                lang_file.write(translation)
                lang_file.write(spawn_translation)

        self.__bp_data.write_lang_defs(lang_path)

    def _define_spawn_egg(self, rp_path: Path, base_color: str = None, overlay_color: str = None) -> dict:
        """
        Creates the spawn egg dictionary to be added to the client entity file of an entity

        :param base_color: A hex code of the color to be used for the base color of the egg
        :param overlay_color: A hex code of the color to be used as an overlay for the egg
        :param texture: The texture short name to be used as the spawn egg texture
        """
        spawn_egg_texture = rp_path.joinpath('textures', 'items', f'{self.name}.png')
        spawn_egg = {}

        if spawn_egg_texture.exists():
            spawn_egg['texture'] = self.name
            spawn_egg['texture_index'] = 0
            item_atlas_path = rp_path.joinpath('textures', 'item_texture.json')

            item_atlas = data_from_file(item_atlas_path)
            if item_atlas is not None:
                item_atlas['texture_data'][self.name] = {}
                item_atlas['texture_data'][self.name]['textures'] = f'textures/items/{self.name}'
                write_to_file(item_atlas_path, item_atlas)

            return spawn_egg

        if base_color and overlay_color:
            spawn_egg['base_color'] = base_color
            spawn_egg['overlay_color'] = overlay_color

        else:
            spawn_egg['texture'] = 'spawn_egg'
            spawn_egg['texture_index'] = 2

        return spawn_egg
