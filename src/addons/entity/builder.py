from addons.entity.client_entity.entity import Entity
from addons.entity.behaviors import EntityBehaviors
from addons.entity.client_entity.render_controller import RenderController
from .properties import EntityProperties, PropertyFactory

from pathlib import Path
import os

class EntityBuilder:
    """Responsible for building out the entity's custom components and defining properties dynamically"""
    def __init__(self, behaviors: EntityBehaviors):
        self.__behaviors = behaviors

    def build_entity(self, build_path: Path, properties: list[EntityProperties]) -> None:
        for prop in properties:
            self.__behaviors.add_property(prop)
        self.__behaviors.build(build_path)

def build_arrays(entity: Entity, rp_path: Path) -> dict[str, dict[str, list[str]]] | None:
    """Builds out the arrays dictionary for the render controller"""
    entity_folder = rp_path.joinpath('textures').joinpath('entity').joinpath(entity.name)
    print(str(entity_folder))
    if not entity_folder.exists() and len(entity.geometries) == 0:
        print('not')
        return None
    arrays = {}
    if entity_folder.exists():
        arrays['textures'] = {}
        for root, subdirs, files in os.walk(str(entity_folder)):
            if not files: continue
            root = root.split(os.sep)[-1]
            array_name = f'Array.{root}' if len(subdirs) > 0 and root == entity.name else 'skins'
            arrays['textures'][array_name] = ['Texture.' + f.replace('.png', '').lower().split('_')[-1] for f in files if f.endswith('.png')]
    if len(entity.geometries) > 1:
        arrays['geometries'] = {}
        arrays['geometries']['Array.models'] = entity.geo_names
    return arrays

def build_properties(arrays: dict[str, dict[str, list[str]]], namespace: str = 'custom') -> list[EntityProperties] | None:
    """Dyanmically builds entity properties from the entity render controller array dictionary"""
    if arrays is None:
        return None
    properties = []
    if arrays.get('textures') is not None:
        for array, data in arrays.get('textures').items():
            name = array.split('.')[-1]
            prop = PropertyFactory.build('int', name, data, namespace=namespace)
            properties.append(prop)
    if arrays.get('geometries') is not None:
        data = arrays.get('geometries').get('Array.models')
        prop = PropertyFactory.build('int', 'models', data, namespace=namespace)
        properties.append(prop)
    
    return properties

def build_entity(build_path: Path, rc: RenderController, behaviors: EntityBehaviors, *, namespace = 'custom') -> None:
    """Helper function that runs all code required to build an entity's behavior file completely"""
    behavior_builder = EntityBuilder(behaviors)
    if rc is not None:
        properties = build_properties(rc.arrays, namespace=namespace)
        behavior_builder.build_entity(build_path, properties)
    else:
        behavior_builder.build_entity(build_path, [])
        