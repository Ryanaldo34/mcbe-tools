from abc import ABC, abstractmethod
from pathlib import Path
from .entity import Entity
from addons.helpers import *
from .render_controller import RenderController

class ClientEntityBase(ABC):
    @abstractmethod
    def write_file(self, rp_path: Path, dummy=False) -> None:
        ...
        
    @abstractmethod
    def add_rc(self, render_controller: RenderController | str, condition: str = None) -> None:
        ...

class ClientEntityV1_8_0(ClientEntityBase):
    def __init__(self, entity: Entity):
        self.__entity = entity
        self.__render_controllers = []

    def write_file(self, rp_path: Path, dummy=False) -> None:
        file_name = '{0}.entity.json'.format(self.__entity.name)
        file_path = rp_path.joinpath('entity', file_name)

        if dummy:
            output = {
                'format_version': '1.8.0',
                'minecraft:client_entity': {
                    'description': {
                        'identifier': self.__entity.identifier,
                        'materials': { 'default': 'entity_alphatest' },
                        'geometry': { 'default': 'geometry.dummy' }
                    }
                }   
            }
            write_to_file(file_path, output)
            return None
            
        else: 
            output = {
                'format_version': '1.8.0',
                'minecraft:client_entity': {
                    'description': {
                        'identifier': self.__entity.identifier,
                        'materials': self.__entity.materials,
                        'geometry': self.__entity.geometries
                    }
                }   
            }
            description = output['minecraft:client_entity']['description']

            # test to see if properties are filled and necessary to add to client entity
            if self.__entity.textures is not None:
                description['textures'] = self.__entity.textures
            if self.__entity.anims is not None:
                description['animations'] = self.__entity.anims
            if self.__entity.acs is not None:
                description['animation_controllers'] = self.__entity.acs
            if self.__entity.sounds is not None:
                description['sound_effects'] = self.__entity.sounds
            if self.__entity.particles is not None:
                description['particles'] = self.__entity.particles
            if self.__entity.locators is not None:
                description['locators'] = self.__entity.locators
            if len(self.__render_controllers) > 0:
                description['render_controllers'] = self.__render_controllers
            if self.__entity.spawn_egg:
                description['spawn_egg'] = self.__entity.spawn_egg

            write_to_file(file_path, output, writing=True)
            return None

    def add_rc(self, render_controller: RenderController | str, condition: str = None) -> None:
        if condition is None:
            if isinstance(render_controller, RenderController):
                self.__render_controllers.append(render_controller.name)
            else:
                self.__render_controllers.append(render_controller)
            return None

class ClientEntityV1_10_0(ClientEntityBase):
    def __init__(self, entity: Entity):
        self.__entity = entity
        self.__render_controllers = []

    def write_file(self, rp_path: Path, dummy=False) -> None:
        file_name = '{0}.entity.json'.format(self.__entity.name)
        file_path = rp_path.joinpath('entity', file_name)

        if dummy:
            output = {
                'format_version': '1.10.0',
                'minecraft:client_entity': {
                    'description': {
                        'identifier': self.__entity.identifier,
                        'materials': { 'default': 'entity_alphatest' },
                        'geometry': { 'default': 'geometry.dummy' }
                    }
                }   
            }
            write_to_file(file_path, output, writing=True)
            return None

        output = {
            'format_version': '1.10.0',
            'minecraft:client_entity': {
                'description': {
                    'identifier': self.__entity.identifier,
                    'materials': self.__entity.materials,
                    'geometry': self.__entity.geometries
                }
            }   
        }
        description = output['minecraft:client_entity']['description']
        if self.__entity.textures is not None:
            description['textures'] = self.__entity.textures
        if len(self.__render_controllers) > 0:
            description['render_controllers'] = self.__render_controllers
        if self.__entity.spawn_egg:
            description['spawn_egg'] = self.__entity.spawn_egg
        if self.__entity.sounds is not None:
            description['sound_effects'] = self.__entity.sounds
        if self.__entity.particles is not None:
            description['particles'] = self.__entity.particles
        if self.__entity.locators is not None:
            description['locators'] = self.__entity.locators
        if self.__entity.anims is not None:
            description['scripts'] = {}
            description['scripts']['animate'] = []
            description['animations'] = self.__entity.anims
            if not self.__entity.acs:
                description['scripts']['animate'] = self.__entity.anims.keys()
                write_to_file(file_path, output, writing=True)
                return None

            for ac in self.__entity.acs:
                for k, v in ac.items():
                    description['animations'][k] = v
                    description['scripts']['animate'].append(k)
        write_to_file(file_path, output, writing=True)

    def add_rc(self, render_controller: RenderController | str, condition: str = None) -> None:
        if condition is None:
            if isinstance(render_controller, RenderController):
                self.__render_controllers.append(render_controller.name)
            else:
                self.__render_controllers.append(render_controller)
            return None