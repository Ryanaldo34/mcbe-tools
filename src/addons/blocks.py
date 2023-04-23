import typer
import os
from pathlib import Path

import addons.helpers as helpers
from .sounds import define_block_sounds

app = typer.Typer()

class Block:
    def __init__(self, block_data: dict):
        self.__data: dict = block_data
        self.__properties: dict[str, any] = self.__data['minecraft:block']['description'].get('properties')

    @property
    def identifier(self) -> str:
        return self.__data['minecraft:block']['description']['identifier']

    @property
    def name(self):
        return helpers.get_short_name(self.identifier)

    @property
    def real_name(self):
        return helpers.id_to_title(self.identifier)

    def define_properties(self, path: Path):
        pass

    def define_geometry(self, geo_id: str):
        self.__data['minecraft:block']['components']['minecraft:geometry'] = geo_id

    def add_material_instances(self, instances: dict):
        self.__data['minecraft:block']['components']['material_instances'] = instances

    def build(self, file_path: Path):
        helpers.write_to_file(file_path, self.__data)

@app.command()
def sounds(
    rp_path: Path = typer.Argument(None, help='Resource pack where block sounds are being defined'),
    namespace: str = typer.Argument(None, help='The namespace')
):
    """
    Defines the sounds of blocks such as break, place, etc.
    """
    define_block_sounds(rp_path, namespace)

@app.command()
def define(
    behavior_file: Path = typer.Argument(None, help='The behavior file of the block'),
    rp_path: Path = typer.Argument(None, help='The path to the resource pack of this block'),
    rp_name: str = typer.Argument('Resource Pack', help='The name of the resource pack for this block'),
    flipbook: bool = typer.Option(False, help='Whether this block is a flipbook texture'),
    variation: bool = typer.Option(False, help='If the block has multiple textures that variate'),
    sound: str = typer.Option('', 'Specify a specific sound for the block')
):
    """
    Defines the resources of a custom block
    """
    if not behavior_file.exists():
        raise typer.BadParameter('That block behavior file does not exist')

    if not rp_path.exists():
        raise typer.BadParameter('The resource pack does not exist!')

    terrain_textures = rp_path.joinpath('textures', 'terrain_texture.json')
    blocks_rp_file = rp_path.joinpath('blocks.json')
    texts_file = rp_path.joinpath('texts', 'en_US.lang')
    terrain_texture_data: dict
    blocks_data: dict
    if terrain_textures.exists():
        terrain_texture_data = helpers.data_from_file(terrain_textures)
    
    else:
        terrain_texture_data = {
            'num_mip_levels' : 4,
            'texture_name': 'atlas.terrain',
            'resource_pack_name' : rp_name,
            'texture_data': {}
        }
    
    if blocks_rp_file.exists():
        blocks_data = helpers.data_from_file(blocks_rp_file)

    else:
        blocks_data = {
            'format_version': "1.19.30"
        }

    block = Block(helpers.data_from_file(behavior_file))
    terrain_texture_data['texture_data'][block.name] = {}
    block_textr_folder = rp_path.joinpath('textures', 'blocks', block.name)
    block_geo_file = rp_path.joinpath('models', 'block', f'{block.name}.geo.json')
    blocks_data[block.identifier] = {}
    if block_geo_file.exists():
        geo_data = helpers.data_from_file(block_geo_file)
        block.define_geometry(geo_data[0]['description']['identifier'])
    # if the block has more than 1 texture
    if block_textr_folder.exists():
        block_textures = [ str(textr)[textr.find('textures'):].replace(os.sep, '/').replace('.png', '') for textr in block_textr_folder.rglob('*.png') ]
        if variation:
            terrain_texture_data['texture_data'][block.name] = {}
            terrain_texture_data['texture_data'][block.name]['textures'] = {}
            terrain_texture_data['texture_data'][block.name]['textures']['variations']: list[dict] = []
            for textr in block_textures:
                weight = int(input(f'What is the weight for the texture {textr}?: '))
                terrain_texture_data['texture_data'][block.name]['textures']['variations'].append({'path': textr, 'weight': weight})

        else:
            blocks_data[block.identifier]['textures'] = {}
            valid_faces = ['*', 'up', 'down', 'north', 'south', 'east', 'west']
            material_instances = {}
            for textr in block_textures:
                short_name = textr.split('_')[-1]
                face = input(f'What face should the texture {short_name}, render on?: ').lower()
                while face not in valid_faces:
                    print(f'Invalid face, please try again and choose from {valid_faces}')
                    face = input(f'What face should the texture {short_name}, render on?: ')
                material_instances[face] = {
                    'ambient_occlusion': True,
                    'render_method': 'alpha_test',
                    'face_dimming': True,
                    'texture': short_name
                }
                terrain_texture_data['texture_data'][short_name] = {}
                terrain_texture_data['texture_data'][textr]['textures'] = textr
                blocks_data[block.identifier]['textures'][short_name] = textr
            block.add_material_instances(material_instances)

    else:
        terrain_texture_data['texture_data'][block.name] = {}
        terrain_texture_data['texture_data'][block.name]['textures'] = f'textures/custom/blocks/{block.name}'
        blocks_data[block.identifier]['textures'] = block.name

    if flipbook:
        pass

    blocks_data[block.identifier]['sound'] = block.name

    print(blocks_data, terrain_texture_data)
    helpers.write_to_file(blocks_rp_file, blocks_data) # blocks.json
    helpers.write_to_file(terrain_textures, terrain_texture_data) # terrain_texture.json
    block.build(behavior_file)

    with open(texts_file, 'a+') as texts:
        texts.write(f'tile.{block.identifier}.name={block.real_name}\n')