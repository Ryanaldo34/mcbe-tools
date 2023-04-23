from addons.errors import *
from addons.helpers import *

class RenderController:
    """Respresents a render controller for a particular entity"""
    def __init__(self, name: str, arrays: dict[str, dict[str, list[str]]], materials: dict[str, str]):
        self.__name = name
        self.__arrays = arrays
        self.__materials = materials
        self.__mat_to_bone_map = []

    @property
    def name(self) -> str:
        return self.__name

    @property
    def arrays(self) -> dict[str, dict[str, list[str]]]:
        return self.__arrays

    def map_mats_to_bones(self) -> list[dict[str, str]]:
        """Formats the bone to the material name in a list for the render controller"""
        mat_names = list(self.__materials)
        if len(mat_names) == 1:
            self.__mat_to_bone_map.append({ '*': 'Material.default' })
            return self.__mat_to_bone_map

        for name in mat_names:
            mapped_bones = input('What bone(s) are the material {0} used on? (use spaces to separate): '.format(name)).split(' ')
            for mapped_bone in mapped_bones:
                self.__mat_to_bone_map.append({ mapped_bone: name })

        return self.__mat_to_bone_map
        

    def convert_to_file(self, rc_path: Path, namespace = 'custom') -> dict:
        """Writes the render controller data to the render controller json file"""
        file_name = '{0}.render_controllers.json'.format(self.__name.split('.')[-1])
        file_path = rc_path.joinpath(file_name)
        output = {
            "format_version": "1.8.0",
            "render_controllers": {}
        }
        output['render_controllers'][self.__name] = {}
        controller = output['render_controllers'][self.__name]
        controller['materials'] = self.__mat_to_bone_map
        controller['geometry'] = 'Geometry.default'
        controller['textures'] = ['Texture.default']
        if self.__arrays is None:
            write_to_file(file_path, output, writing=True)
            return output

        controller['arrays'] = self.__arrays
        texture_arrays = self.__arrays.get('textures')
        geometry_arrays = self.__arrays.get('geometries')
        if texture_arrays is not None:
            controller['textures'] = [f"Array.{array}[query.property('{namespace}:{array}')]" for array in list(texture_arrays)]
        if geometry_arrays is not None:
            controller['geometry'] = f"Array.models[query.property('{namespace}:models')]"

        write_to_file(file_path, output, writing=True)
        return output