from pathlib import Path
from addons.entity.behaviors import EntityBehaviors
from addons.helpers.file_handling import data_from_file, write_to_file
from .geo import Geometry
from addons.errors import *

class EntityProperties:
    ...

class Entity:
    """ 
    Used to encapsulate and handle data relating to an entity definition
    """
    def __init__(self, materials: dict[str, str],
                geometry: Geometry, 
                bp_data: EntityBehaviors, 
                rp_path: Path, *,
                anim_req: bool = False,
                ac_req: bool = False,
                texture_req: bool = False):
        """
        :param materials: the short-name: value map of materials for the entity gathered from user input
        :param bp_data: the encapsulated data from the entity's behavior fiile
        """
        self.identifier = bp_data.identifier
        self.name = bp_data.real_name
        self.__materials: dict[str, str] = materials
        self.__bp_data: EntityBehaviors = bp_data
        self.__material_names: list[str] = [f'Material.{x}' for x in list(self.__materials)]
        self.__geo_name_val_map: dict = geometry.get_geos()
        self.__geo_names: list[str] = geometry.get_names()
        self.__bones = geometry.get_bones()
        self.__spawn_egg: dict = self._define_spawn_egg(rp_path)
        self.__textr_name_val_map: dict[str, str] = self._define_textures(rp_path, texture_req)
        self.__textr_names: list[str] = [f'Texture.{short_name}' for short_name in list(self.__textr_name_val_map)] if self.__textr_name_val_map is not None else None
        self.__textr_paths: list[str] = list(self.__textr_name_val_map.values()) if self.__textr_name_val_map is not None else None
        self.__anims: dict[str, str] = self._define_animations(rp_path, anim_req)
        self.__acs: list[dict] = self._define_animation_controllers(rp_path, ac_req)
        self.__particles: dict = None
        self.__sounds: dict = None
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
        return len(self.__material_names) < 2 and len(self.__textr_names) < 2 and len(self.__geo_names) < 2

    @property
    def textr_paths(self) -> list[str]:
        return self.__textr_paths

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
        return self.__textr_names

    @textr_names.setter
    def textr_names(self, names: list[str]):
        if type(names) != list and names is not None:
            raise ValueError('The Texture Names List needs to be a list!')
        self.__textr_names = names

    @property
    def sounds(self) -> dict:
        return self.__sounds

    @sounds.setter
    def sounds(self, sounds_dict: dict):
        if type(sounds_dict) != dict and sounds_dict is not None:
            raise ValueError('The Sounds Short-name: Value map needs to be a dictionary!')
        self.__sounds = sounds_dict

    @property
    def spawn_egg(self) -> dict:
        return self.__spawn_egg

    @staticmethod
    def define_materials(default: bool) -> dict[str, str]:
        """Defines the shortname: value pairs for materials in the client entity file
        
        :param materials: the string gathered from user input
        """
        if not default:
            materials = input('Enter the names of materials to be used in the entity (use space to separate): ').split(' ')
            material_names = []
            for material in materials:
                name = input(f'what is the short-name of the material -> {material}: ')
                material_names.append(name)

            return { name: value for name, value in zip(material_names, materials) }
        else:
            return {'default': 'entity_alphatest'}

    def _define_animations(self, rp_folder: Path, anim_errors: bool = False) -> dict[str, str] | None:
        """
        Gets the animation file path and interprets the data from the file to encapsulate it in the entity object
        
        :param rp_folder: the resource pack folder location
        :param entity: the entity being defined
        """
        anim_file = rp_folder.joinpath('animations', f'{self.name}.animation.json')
        anim_data = data_from_file(anim_file)

        if anim_file.is_file():
            self.__anims = { animation.split('.')[-1]: animation for animation in list(anim_data['animations']) }

        else:
            if anim_errors: raise MissingAnimationError('The entity is missing a required animation file!')

    def _define_animation_controllers(self, rp_folder: Path, ac_errors: bool = False) -> list[dict[str, str]] | None:
        """ 
        Gets the animation controller file path and interprets data from the file to encapsulate it in the entity object

        :param rp_folder: the resource pack folder location
        :param entity: the entity being defined
        """
        ac_file = rp_folder.joinpath('animation_controllers', f'{self.name}.animation_controllers.json')

        if ac_file.is_file():
            ac_data = data_from_file(ac_file)
            return [ {controller.split('.')[-1]: controller} for controller in list(ac_data['animation_controllers']) ]

        else:
            if ac_errors: raise MissingAnimationControllerFile('The entity has a required animation controller that is missing!')

    def _define_textures(self, rp_folder: Path, texture_errors: bool = True) -> dict[str, str] | None:
        """ 
        Gets the texture folder or texture file path and formats the paths into aceptable data for MC and encapsulates it in the entity object
        
        :param rp_folder: the resource pack folder location
        :param working_file: the dir where the script is running
        :param entity: the entity being defined
        """
        entity_textr_folder = rp_folder.joinpath('textures', 'entity', self.name)
        entity_textr_file = rp_folder.joinpath('textures', 'entity', f'{self.name}.png')

        if entity_textr_folder.exists():
            textures = [str(textr) for textr in entity_textr_folder.rglob('*.png')]
            for i, textr in enumerate(textures):
                pos = textr.find('textures')
                textr = textr[pos:].replace('.png', '').replace(os.sep, '/')
                textures[i] = textr
            short_name_val_map = { textr.split('/')[-1].split('_')[-1]: textr for textr in textures }

            return short_name_val_map
            
        else:
            if entity_textr_file.exists():
                return {'default': f'textures/entity/{self.name}'}

            else:
                if texture_errors: raise MissingTextureError('The entity is missing a required texture file')
                    
                return None

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
