from pathlib import Path
from .behaviors import EntityBehaviors
from addons.helpers.file_handling import data_from_file, write_to_file
from .geo import Geometry

class Entity:
    """ 
    Used to encapsulate and handle data relating to an entity definition
    """

    def __init__(self, materials: dict, geometry: Geometry, bp_data: EntityBehaviors):
        """
        :param materials: the short-name: value map of materials for the entity gathered from user input
        :param bp_data: the encapsulated data from the entity's behavior fiile
        """
        self.identifier = bp_data.identifier
        self.name = bp_data.real_name
        self.__materials: dict = materials
        self.__bp_data: EntityBehaviors = bp_data
        self.__material_names: list[str] = [f'Material.{x}' for x in list(self.__materials)]
        self.__geo_name_val_map: dict = geometry.get_geos()
        self.__geo_names: list[str] = geometry.get_names()
        self.__spawn_egg: dict = None
        self.__textr_name_val_map: dict = None
        self.__textr_names: list[str] = None
        self.__textr_paths: list[str] = None
        self.__anims: dict = None
        self.__acs: list[dict] = None
        self.__particles: dict = None
        self.__sounds: dict = None
        self.__locators: dict = geometry.get_locators()
        self.__render_controllers: list[str] = [] # not required for dummy entities so that is why this is here, should otherwise always be filled

    @property
    def geo_names(self) -> list[str]:
        return self.__geo_names

    @property
    def material_names(self) -> list[str]:
        return self.__material_names

    @property
    def textr_name_val_map(self):
        raise AttributeError('Texture Name-Value Map is write-only')

    @textr_name_val_map.setter
    def textr_name_val_map(self, map: dict):
        if type(map) != dict and map is not None:
            raise ValueError('The Texture Short-name: Value map must be a dictionary!')
        self.__textr_name_val_map = map

    @property
    def textr_names(self) -> list[str]:
        return self.__textr_names

    @textr_names.setter
    def textr_names(self, names: list[str]):
        if type(names) != list and names is not None:
            raise ValueError('The Texture Names List needs to be a list!')
        self.__textr_names = names

    @property
    def textr_paths(self) -> list[str]:
        return self.__textr_paths

    @textr_paths.setter
    def textr_paths(self, paths: list[str]):
        if type(paths) != list and paths is not None:
            raise ValueError('The Texture Paths List needs to be a list!')
        self.__textr_paths = paths

    @property
    def sounds(self) -> dict:
        return self.__sounds

    @sounds.setter
    def sounds(self, sounds_dict: dict):
        if type(sounds_dict) != dict and sounds_dict is not None:
            raise ValueError('The Sounds Short-name: Value map needs to be a dictionary!')
        self.__sounds = sounds_dict

    @property
    def particles(self) -> dict:
        return self.__particles

    @particles.setter
    def particles(self, values: dict):
        if type(values) != dict and values is not None:
            raise ValueError('The Particles Short-name: Value map needs to be a dictionary!')
        self.__particles = values

    @property
    def anims(self):
        raise AttributeError('Animations are write-only')

    @anims.setter
    def anims(self, anims_dict: dict):
        if type(anims_dict) != dict and anims_dict is not None:
            raise ValueError('The Animations Short-name: Value map needs to be a dictionary!')
        self.__anims = anims_dict

    @property
    def acs(self):
        raise AttributeError('Animation Controllers are write-only')

    @acs.setter
    def acs(self, acs_dict: dict):
        if type(acs_dict) != list and acs_dict is not None:
            raise ValueError('The Animation Controllers Short-name: Value map needs to be a dictionary!')
        self.__acs = acs_dict

    def get_textr_indexes(self, arrays: dict) -> list:
        """
        Prompts the user for the indexing function of each texture array in the render controller

        :param arrays: the arrays dictionary from the entity's render controller
        :returns: a list of indexes to be used in the entity's render controller
        """
        if len(arrays) == 0 or 'textures' not in arrays:
            return [ 'Texture.default' ]

        else:
            textr_arrs = arrays['textures'].keys()
            indexes = []

            for array in textr_arrs:
                value = input('What is the indexing function for the array {0}?: '.format(array))
                value = f'{array}[{value}]'
                indexes.append(value)

            assert len(indexes) > 0, 'The texture index list needs to be at least 1!'
            return indexes

    def add_rc(self, render_controller: str) -> None:
        """
        Adds a render controller name to the entity's render controller list

        :param render_controller: the render controller name being added
        """
        self.__render_controllers.append(render_controller)

    def write_client_entity(self, rp_path: Path, dummy=False) -> dict:
        """
        Uses encapsulated data to complete the data used for writing the client entity file and returns it

        :param entity_folder: the path to the rp/entity folder in the entity's resource pack
        :returns: the data to be written to the client entity file
        """
        entity_folder = rp_path.joinpath('entity')
        file_name = '{0}.entity.json'.format(self.name)
        file_path = entity_folder.joinpath(file_name)

        if dummy:
            output = {
                'format_version': '1.8.0',
                'minecraft:client_entity': {
                    'description': {
                        'identifier': self.identifier,
                        'materials': { 'default': 'entity_alphatest' },
                        'geometry': { 'default': 'geometry.dummy' }
                    }
                }   
            }
            write_to_file(file_path, output)
            return output
            
        else: 
            output = {
                'format_version': '1.8.0',
                'minecraft:client_entity': {
                    'description': {
                        'identifier': self.identifier,
                        'materials': self.__materials,
                        'geometry': self.__geo_name_val_map
                    }
                }   
            }
            description = output['minecraft:client_entity']['description']

            if self.__bp_data.is_spawnable():
                description['spawn_egg'] = self.define_spawn_egg(rp_path)

            # test to see if properties are filled and necessary to add to client entity
            if self.__textr_name_val_map is not None:
                description['textures'] = self.__textr_name_val_map

            if self.__anims is not None:
                description['animations'] = self.__anims

            if self.__acs is not None:
                description['animation_controllers'] = self.__acs

            if self.__sounds is not None:
                description['sounds'] = self.__sounds

            if self.__particles is not None:
                description['particles'] = self.__particles

            if self.__locators is not None:
                description['locators'] = self.__locators

            if len(self.__render_controllers) > 0:
                description['render_controllers'] = self.__render_controllers

            if self.__spawn_egg is not None:
                description['spawn_egg'] = self.__spawn_egg

            print('Writing to the client entity file right now!')
            write_to_file(file_path, output, writing=True)

            return output

    def write_lang(self, RP_PATH: Path) -> None:
        """
        Adds the required entity translation key definitions to the rp .lang file

        :param RP_PATH: The path to the resource pack the entity belongs to
        """
        lang_path = RP_PATH.joinpath('texts', 'en_US.lang')
        title = self.name.replace('_', ' ').title()
        translation = f'entity.{self.identifier}.name={title}\n'
        spawn_translation = f'item.spawn_egg.entity.{self.identifier}.name=Spawn {title}\n'
        with open(lang_path, 'a') as lang_file:
            written_data = lang_file.readlines()

            if translation not in written_data:
                lang_file.write(translation)
                lang_file.write(spawn_translation)

        self.__bp_data.write_lang_defs(lang_path)

    def define_spawn_egg(self, rp_path: Path, base_color: str = None, overlay_color: str = None) -> dict:
        """
        Creates the spawn egg dictionary to be added to the client entity file of an entity

        :param base_color: A hex code of the color to be used for the base color of the egg
        :param overlay_color: A hex code of the color to be used as an overlay for the egg
        :param texture: The texture short name to be used as the spawn egg texture
        """
        spawn_egg_texture = rp_path.joinpath('textures', 'items', f'{self.name}')
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
