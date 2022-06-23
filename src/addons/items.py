import os, typer, glob
from .helpers.file_handling import *
from .errors import TEXTURE_ERRORS, MissingTextureError
from pathlib import Path
from typing import Union

app = typer.Typer()

class Item:
    def __init__(self, item_data: dict):
        self.__data = item_data

    @property
    def identifier(self):
        return self.__data['minecraft:item']['description']['identifier']

    @property
    def name(self) -> str:
        return self.__data['minecraft:item']['description']['identifier'].split(':')[-1]

    @property
    def is_attachable(self) -> bool:
        return 'minecraft:wearable' in self.__data['minecraft:item']['components']

    @property
    def real_name(self):
        return self.name.replace('_', ' ').title()

def use_anim_callback(value: Union[str, None]):
    if value is not None and value not in ['bow', 'eat', 'drink', 'crossbow', 'camera']:
        raise typer.BadParameter('The animation given is not valid!')

def category_callback(value: str):
    if value not in ['Nature', 'Equipment', 'Construction', 'Items']:
        raise typer.BadParameter('The category given is not valid!')

@app.command('define')
def create_item_defs(item_path: Path = typer.Argument(None, help='The path to the item behavior file'), 
                    rp_path: Path = typer.Argument(None, help='The path to the resource pack'),
                    animation: str = typer.Option(None, callback=use_anim_callback, help='The animation played when the item is being used'),
                    category: str = typer.Option('Items', callback=category_callback, help='The creative category of the item')):
    """Defines an item"""
    try:
        item_data: dict = data_from_file(item_path)
        item = Item(item_data)

        item_rp_folder: Path = rp_path.joinpath('items')
        attachables_folder: Path = rp_path.joinpath('attachables')
        item_textures_folder: Path = rp_path.joinpath('textures', 'items')
        item_textures_file: Path = rp_path.joinpath('textures', 'item_texture.json')
        texts_file: Path = rp_path.joinpath('texts', 'en_US.lang')
        lang_data: list = data_from_file(texts_file) if texts_file.exists() else []
        
        # basic items atlas
        atlas: dict
        if not item_textures_file.exists():
            rp_name = data_from_file(rp_path.joinpath('manifest.json'))['header']['name']
            atlas = {
                'resource_pack_name': rp_name,
                'texture_name': 'atlas.items',
                "texture_data": {}
            }
        else:
            atlas = data_from_file(item_textures_file)

        if not item.is_attachable:
            txtr_atlas = atlas['texture_data']
            item_texture = item_textures_folder.joinpath(f'{item.name}.png')
            txtr_atlas[item.name] = {}
            txtr_atlas[item.name]['textures'] = str(item_texture)[str(item_texture).find('textures'):].replace(os.sep, '/').replace('.png', '')
            lang_def = f'item.{item.identifier}.name={item.real_name}'
            item_rp_data = {
                    'format_version': '1.10.0',
                    'minecraft:item': {
                        'description': {
                            'identifier': item.identifier,
                            'category': category
                        },
                        'components': {
                            'minecraft:icon': item.name,
                            'minecraft:render_offsets': 'apple'
                    }
                }
            }
            if category is not None:
                item_rp_data['minecraft:item']['components']['minecraft:use_animation'] = animation

            write_to_file(item_rp_folder.joinpath(f'{item.name}.item.json'), item_rp_data)
            if lang_def not in lang_data: lang_data.append(lang_def)
            write_to_file(texts_file, lang_data)
            print(atlas)
            write_to_file(item_textures_file, atlas)

        else:
            pass

    except KeyError as err:
        typer.Abort()
