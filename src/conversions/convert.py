import shutil, os
import addons.paths as paths
from typing import Any
from pathlib import Path
from addons.helpers.file_handling import data_from_file, write_to_file
from uuid import uuid4

"""doors, buckets, and boats need work"""

versions = {
    4: '1.13.0',
    5: '1.15.0',
    6: '1.16.0',
    7: '1.17.0',
    8: '1.18.0',
    9: '1.18.2',
    10: '1.19.0'
}
java_versions = {
    '1.13.0': 4,
    '1.15.0': 5,
    '1.16.0': 6,
    '1.17.0': 7,
    '1.18.0': 8,
    '1.18.2': 9,
    '1.19.0': 10
}

def copy_files(sources: list[Path], dst: Path):
    for path in sources:
        shutil.copy(path, dst)

def create_paths(base: Path, *paths: list[str]) -> tuple[Path]:
    new_paths = []
    for path in paths:
        folder = base.joinpath(path)
        folder.mkdir()
        new_paths.append(folder)

    return tuple(new_paths)

def convert_mcbe_texture(texture: str) -> str:
    """Converts a vanilla texture that may be named differently on bedrock than java to the java format"""
    keywords = ['bucket', 'planks', 'log', 'concrete']
    if texture.startswith('wool'):
        return ''.join(texture.replace('_colored', '').split('_').reverse())

def convert_mcbe_lang(texts_folder: Path) -> dict[str, str]:
    """Converts the mcbe lang file and languages.json to the proper java format"""
    pass

def convert_java_lang(lang_file: Path) -> list[str]:
    """Converts the java lang file to the proper languages.json and .lang file format on mcbe"""
    pass

def convert_mcmeta(mcmeta_file: Path, pack_name: str, *, rp_uuid: str = None) -> dict[str, Any]:
    """Converts An mcmeta file to a manifest.json file dictionary"""
    if not mcmeta_file.exists():
        raise FileNotFoundError

    mcmeta = data_from_file(mcmeta_file)
    min_version = [int(x) for x in versions[mcmeta['pack']['pack_format']].split('.')]
    manifest = {
        'format_version': 2,
        'header': {
            'name': pack_name,
            'description': mcmeta['pack']['description'],
            'uuid': str(uuid4()),
            'version': [1, 0, 0],
            'min_engine_version': min_version if not rp_uuid else [1, 19, 0]
        },
        'modules': {
            'description': mcmeta['pack']['description'],
            'type': 'data',
            'uuid': str(uuid4()),
            'version': [1, 0, 0]
        }
    }
    if rp_uuid is not None:
        manifest['dependencies'] = [
            {
                'uuid': rp_uuid,
                'version': [1, 0, 0]
            }
        ]

    return manifest

def convert_manifest(manifest_file: Path, rp: bool = False) -> dict[str, Any]:
    """Converts a manifest.json to a pack.mcmeta file for Java Edition"""
    if not manifest_file.exists():
        raise FileNotFoundError

    manifest_data = data_from_file(manifest_file)
    version, major, minor = manifest_data['header']['min_engine_version']
    version_str = f'{version}.{major}.{minor}'
    if not version_str in java_versions:
        version_str = [x for x in list(java_versions) if x.split('.')[1] in version_str and minor >= x.split('.')[-1]][0]

    pack_format: int = java_versions[version_str]
    return {
        'pack': {
            'pack_format': pack_format if not rp else 9,
            'description': manifest_data['header'].get('description')
        }
    }

def convert_mcbe_rp(projects_folder: Path, 
                    mcbe_rp: Path, 
                    *, 
                    namespace='custom',
                    pack_name='Converted RP'
):
    """Converts MCBE resource pack structure to a valid Java resource pack strucuture"""
    parent = projects_folder.joinpath(pack_name)
    parent.mkdir()
    # add the pack icon and the converted manifest
    shutil.copy(mcbe_rp.joinpath('pack_icon.png'), parent.joinpath('pack.png'))
    # assets folder here
    assets = parent.joinpath('assets')
    assets.mkdir()
    # convert manifest to mcmeta
    write_to_file(parent.joinpath('pack.mcmeta'), convert_manifest(mcbe_rp.joinpath('manifest.json'), rp=True))
    minecraft, custom = create_paths(assets, 'minecraft', namespace.lower().replace(' ', ''))
    # add base directories
    create_paths(minecraft, 'blockstates', 'font', 'lang', 'models', 'particles', 'shaders', 'texts', 'textures')
    create_paths(custom, 'animations', 'blockstates', 'font', 'geo', 'lang', 'models', 'particles', 'sounds', 'textures')
    create_paths(
        minecraft.joinpath('textures'), 'block', 'item', 'entity', 'models', 'map', 'painting', 'colormap', 'gui','environment'
    )
    create_paths(
        custom.joinpath('textures'), 'block', 'item', 'entity', 'models', 'map', 'painting', 'colormap', 'gui', 'environment'
    )
    # parse blocks.json and itemtextures json to determine which texture aren't custom
    block_textures: list[Path] = [ x for x in mcbe_rp.joinpath('textures', 'blocks').rglob('*.png') ]
    item_textures: list[Path] = [ x for x in mcbe_rp.joinpath('textures', 'items').rglob('*.png') ]
    custom_block_textures: list[Path] = []
    custom_item_textures: list[Path] = []
    blocks_data = data_from_file(mcbe_rp.joinpath('blocks.json'))
    terrain_data = data_from_file(mcbe_rp.joinpath('textures', 'terrain_texture.json'))
    item_texture_data = data_from_file(mcbe_rp.joinpath('textures', 'item_texture.json'))
    item_folder = mcbe_rp.joinpath('items')
    entity_folder = mcbe_rp.joinpath('entity')

    for block in list(blocks_data):
        if block.startswith(namespace) or ':' in block:
            textures = blocks_data[block]['textures']
            if isinstance(textures, dict):
                for x in textures.values():
                    block_path = mcbe_rp.joinpath(*terrain_data['texture_data'][x].get('textures').replace('blocks', 'block').split('/'))
                    custom_block_textures.append(block_path)
                    block_textures.remove(block_path)
            else:
                custom_block_textures.append(terrain_data[textures].get('textures'))
        else:
            continue
    for item in os.listdir(item_folder):
        data = data_from_file(item)
        texture = data['minecraft:item']['components'].get('minecraft:icon')
        texture_path = mcbe_rp.joinpath(*item_texture_data['texture_data'].get(texture)['textures'].replace('items', 'item').split('/'))
        custom_item_textures.append(texture_path)
        item_textures.remove(texture_path)
    # copy over the block and item textures
    copy_files(block_textures, minecraft.joinpath('textures', 'block'))
    copy_files(custom_block_textures, custom.joinpath('textures', 'block'))
    copy_files(custom_item_textures, custom.joinpath('textures', 'item'))
    copy_files(item_textures, minecraft.joinpath('textures', 'item'))
    # parse client entities and determine which entity textures are custom

def convert_java_rp_structure(projects_folder: Path, java_rp: Path, *, namespace: str = 'custom'):
    """Converts Java resource pack structure to a valid bedrock resource pack structure"""
    pack_name = java_rp.name
    root_dir = projects_folder.joinpath(pack_name)
    root_dir.mkdir()
    # create folders for bedrock rp
    rp_folders = ['animation_controllers', 'animations', 'items', 'entity', 'models', 'particles', 'render_controllers', *paths.MODELS.values(), *paths.SOUNDS.values(), *paths.TEXTURES.values()]
    for folder in rp_folders:
        root_dir.joinpath(pack_name, folder).mkdir(parents=True, exist_ok=True)
    # create manifest
    manifest_data = convert_mcmeta(java_rp.joinpath('pack.mcmeta'), pack_name)
    write_to_file(root_dir.joinpath('manifest.json'), manifest_data, writing=True)
    # add block data
    terrain_textures = {
        'num_mip_levels' : 4,
        'padding' : 8,
        'resource_pack_name' : pack_name,
        'texture_data': {}
    }
    blocks = {}
    # minecraft textures
    minecraft_blocks = [x for x in java_rp.joinpath('assets', 'minecraft', 'textures', 'block').rglob('*.png')]
    minecraft_items = [x for x in java_rp.joinpath('assets', 'minecraft', 'textures', 'item').rglob('*.png')]
    # custom textures
    custom_animations = [x for x in java_rp.joinpath('assets', namespace, 'animations').rglob('*.animation.json')]
    copy_files(custom_animations, root_dir.joinpath('animations'))
    custom_models = [x for x in java_rp.joinpath('assets', namespace, 'geo').rglob('*.geo.json')]
    copy_files(custom_models, root_dir.joinpath('models', 'entity'))
    custom_blocks = [x for x in java_rp.joinpath('assets', namespace, 'textures', 'block').rglob('*.png')]
    custom_items = [x for x in java_rp.joinpath('assets', namespace, 'textures', 'item').rglob('*.png')]
    # write block data from block models


def convert_bp(projects_folder: Path, bp: Path, mcmeta_data: dict[str, Any], *, namespace='custom'):
    """Convert a behavior pack to a valid datapack"""
    ...

def convert_datapack(projects_folder: Path, datapack: Path, manifest_data: dict[str, Any]):
    """Convert a datapack to a valid behavior pack"""
    ...