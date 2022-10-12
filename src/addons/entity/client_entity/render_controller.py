from addons.errors import *
from addons.helpers.file_handling import *
from .entity import Entity
import re

class RenderController:

    def __init__(self, linked_entity: Entity, name: str):

        self.__linked_entity = linked_entity
        self.__name = name
        self.__bones = linked_entity.bones
        self.__texture_names = linked_entity.textr_names
        self.__textr_paths = linked_entity.textr_paths
        self.__geo_names = linked_entity.geo_names
        self.__material_names = linked_entity.material_names
        self.__mat_to_bone_map = []
        self.__arrays = self.__make_arrays()
        self.__textr_arr_indexes = linked_entity.get_textr_indexes(self.__arrays)

    @property
    def name(self) -> str:
        return self.__name

    def __make_arrays(self) -> dict:
        arrays = {}
        num_geos = len(self.__geo_names)
        num_textures = len(self.__textr_paths)
        num_materials = len(self.__material_names)

        if num_geos > 1:
            arrays['geometries'] = {}
            arrays['geometries']['array.models'] = [x for x in self.__geo_names]

        if num_textures > 1:
            arrays['textures'] = {}
            for i, path in enumerate(self.__textr_paths):
                path_parts = path.split('/')
                # means that there are sub folders in the parent entity texture folder, the arrays will be named based on these folders
                if len(path_parts) > 4:
                    array_name = path_parts[3]
                    if array_name in arrays['textures']:
                        arrays['textures'][array_name].append(self.__texture_names[i])

                    else:
                        arrays['textures'][array_name] = []
                        arrays['textures'][array_name].append(self.__texture_names[i])

                elif len(path_parts) == 4:
                    if 'array.skins' not in arrays['textures']:
                        arrays['textures']['array.skins'] = []
                        arrays['textures']['array.skins'].append(self.__texture_names[i])

                    else:
                        arrays['textures']['array.skins'].append(self.__texture_names[i])

                else:
                    pass

        if num_materials > 1:
            pass

        return arrays

    def map_mats_to_bones(self) -> list[dict[str, str]]:
        mat_names = self.__material_names
        # if there are multiple materials defined
        if len(mat_names) > 1:
            for name in mat_names:
                mapped_bones = input('What bone(s) are the material {0} used on? (use spaces to separate): '.format(name)).split(' ')
                for mapped_bone in mapped_bones:
                    self.__mat_to_bone_map.append({ mapped_bone: name })
        # if there is only one material
        else:
            self.__mat_to_bone_map.append({ '*': self.__material_names[0] })

        return self.__mat_to_bone_map
        

    def convert_to_file(self, rc_path: Path) -> dict:
        output = {
            "format_version": "1.8.0",
            "render_controllers": {}
        }
        output['render_controllers'][self.__name] = {}
        controller = output['render_controllers'][self.__name]

        if self.__arrays:
            controller['arrays'] = self.__arrays

        controller['materials'] = self.__mat_to_bone_map
        controller['textures'] = self.__textr_arr_indexes

        if len(self.__geo_names) > 1:
            index = input('What is the indexing function for the geometry array: ')
            controller['geometry'] = f'array.models[{index}]'

        else:
            controller['geometry'] = 'Geometry.default'

        file_name = '{0}.render_controllers.json'.format(self.__linked_entity.name)
        file_path = rc_path.joinpath(file_name)

        write_to_file(file_path, output, writing=True)

        return output