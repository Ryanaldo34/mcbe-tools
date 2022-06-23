import typer, os
from pathlib import Path
from addons.helpers.file_handling import data_from_file, write_to_file
from .sounds import define_block_sounds

app = typer.Typer()

class Block:
    def __init__(self, block_data: dict):
        self.__data: dict = block_data
        try:
            self.__properties: dict = self.__data['minecraft:block']['description']['properties']
        except KeyError:
            self.__properties = None

    @property
    def identifier(self) -> str:
        return self.__data['minecraft:block']['description']['identifier']

    @property
    def name(self):
        return self.identifier.split(':')[-1]

    @property
    def real_name(self):
        return self.identifier.replace('_', ' ').title()

@app.command()
def sounds(rp_path: Path = typer.Argument(None, help='Resource pack where block sounds are being defined')):
    """
    Defines the sounds of blocks such as break, place, etc.
    """
    define_block_sounds(rp_path)

@app.command()
def define(behavior_file: Path = typer.Argument(None, help='The behavior file of the block'),
            rp_path: Path = typer.Argument(None, help='The path to the resource pack of this block'),
            rp_name: str = typer.Argument(None, help='The name of the resource pack for this block'),
            flipbook: bool = typer.Option(False, help='Whether this block is a flipbook texture')):
    """
    Defines the resources of a custom block
    """
    terrain_textures = rp_path.joinpath('textures', 'terrain_texture.json')
    blocks_rp_file = rp_path.joinpath('blocks.json')
    terrain_texture_data: dict
    blocks_data: dict
    if terrain_textures.exists():
        terrain_texture_data = data_from_file(terrain_textures)
    
    else:
        terrain_texture_data = {
            'num_mip_levels' : 4,
            'padding ': 8,
            'resource_pack_name' : rp_name,
            'texture_data': {}
        }
    
    if blocks_rp_file.exists():
        blocks_data = data_from_file(blocks_rp_file)

    else:
        blocks_data = {
            'format_version': [1, 1, 0]
        }

    block = Block(data_from_file(behavior_file))
    terrain_texture_data['texture_data'][block.name] = {}
    block_textr_folder = rp_path.joinpath('textures', 'blocks', block.name)
    block_texture = rp_path.joinpath('textures', 'blocks', f'{block.name}.png')
    blocks_data[block.identifier] = {}
    # if the block has more than 1 texture
    if block_textr_folder.exists():
        blocks_data[block.identifier]['textures'] = {}
        block_textures = [ str(textr)[textr.find('textures'):].replace(os.sep, '/').replace('.png', '') for textr in block_textr_folder.rglob('*.png') ]
        for textr in block_textures:
            short_name = textr.split('_')[-1]
            terrain_texture_data['texture_data'][short_name] = {}
            terrain_texture_data['texture_data'][textr]['textures'] = textr
            blocks_data[block.identifier]['textures'][short_name] = textr

    else:
        terrain_texture_data['texture_data'][block.name] = {}
        terrain_texture_data['texture_data'][block.name]['textures'] = str(block_texture)
        blocks_data[block.identifier]['textures'] = block.name

    blocks_data[block.identifier]['sound'] = block.name

    print(blocks_data, terrain_texture_data)
    write_to_file(blocks_data, blocks_rp_file) # blocks.json
    write_to_file(terrain_texture_data, terrain_textures) # terrain_texture.json