from pathlib import Path
import uuid, os, shutil, typer
from zipfile import ZipFile
from PIL import Image
from addons.helpers.file_handling import write_to_file, data_from_file
from .config import config

projects_path = config.projects_path
languages = ['en_US']
bp_folders = ['animation_controllers', 'animations', 'blocks', 'features', 'functions', 'items', 'entities', 'structures', 'biomes', 'loot_tables', 'scripts', 'trades']
rp_folders = ['animation_controllers', 'animations', 'items', 'entity', 'models', 'particles', 'render_controllers', *config.all_texture_paths, *config.all_model_paths, *config.all_sound_paths]
app = typer.Typer()

def package_skinpack():
    ...

@app.command()
def create(
    project_name: str,
    gt: bool=typer.Option(default=False, help="Whether this is gametest enabled")
) -> None:
    """ Creates a new blank project template in the user's dedicated project folder
    
    """
    rp_manifest: dict = config.rp_manifest
    bp_manifest: dict = config.bp_manifest
    rp_header = str(uuid.uuid4())
    rp_name: str = project_name.lower().replace(' ', '_') + '_RP'
    bp_name: str = project_name.lower().replace(' ', '_') + '_BP'

    project_path = projects_path.joinpath(project_name)
    project_path.mkdir()
    project_path.joinpath(rp_name).mkdir()
    project_path.joinpath(bp_name).mkdir()

    rp_manifest['header']['uuid'] = rp_header
    rp_manifest['header']['name'] = project_name + ' RP'
    rp_manifest['header']['description'] = 'Resource pack for {0}'.format(project_name)
    for module in rp_manifest['modules']:
        module['uuid'] = str(uuid.uuid4())
        module['description'] = 'Resource pack for {0}'.format(project_name)

    bp_manifest['header']['uuid'] = str(uuid.uuid4())
    bp_manifest['header']['name'] = project_name + ' BP'
    bp_manifest['header']['description'] = 'Behavior pack for {0}'.format(project_name)
    for module in bp_manifest['modules']:
        module['uuid'] = str(uuid.uuid4())
        module['description'] = 'Behavior pack for {0}'.format(project_name)
    bp_manifest['dependencies'][0]['uuid'] = rp_header

    for folder in rp_folders:
        project_path.joinpath(rp_name, folder).mkdir(parents=True, exist_ok=True)

    for folder in bp_folders:
        project_path.joinpath(bp_name, folder).mkdir(parents=True, exist_ok=True)

    blocks = config.blocks_json
    sounds = config.sounds_json
    sound_defs = config.sound_defs
    terrain = config.terrain_texture
    terrain['resource_pack_name'] = project_name
    items = config.item_texture
    items['resource_pack_name'] = project_name

    write_to_file(project_path.joinpath(rp_name, 'manifest.json'), data=rp_manifest, writing=True)
    write_to_file(project_path.joinpath(bp_name, 'manifest.json'), data=bp_manifest, writing=True)
    write_to_file(project_path.joinpath(rp_name, 'blocks.json'), data=blocks, writing=True)
    write_to_file(project_path.joinpath(rp_name, 'sounds.json'), data=sounds, writing=True)
    write_to_file(project_path.joinpath(rp_name, 'sounds', 'sound_definitions.json'), data=sound_defs, writing=True)
    write_to_file(project_path.joinpath(rp_name, 'textures', 'item_texture.json'), data=items, writing=True)
    write_to_file(project_path.joinpath(rp_name, 'textures', 'terrain_texture.json'), data=terrain, writing=True)
    write_to_file(project_path.joinpath(rp_name, 'textures', 'flipbook_textures.json'), data=[], writing=True)

@app.command()
def package(
    project_name: str,
    project_description: str,
    assets_zip_folder: Path,
    world_folder_path: Path,
    skinpack: bool=typer.Option(default=False, help='Whether this package has a skinpack')
) -> None:
    """
    Packages a world for marketplace submission

    :param project_name: the name of the project being packaged
    :param project_description: the description to be used in game for the world template
    :param assets_zip_folder: the path to the zip folder 
    """
    if not world_folder_path.exists() or not assets_zip_folder.exists():
        raise FileNotFoundError('A folder for the world being packaged does not exist or the assets folder provided is invalid!')

    else:
        package_parents = ['Content', 'Marketing Art', 'Store Art']
        package_path = assets_zip_folder.parent.joinpath(project_name)
        package_path.mkdir()
        for prnt in package_parents:
            path = package_path.joinpath(prnt)
            path.mkdir()
        world_template = package_path.joinpath('Content', 'world_template')
        template_texts = world_template.joinpath('texts')
        texts = [f'pack.name={project_name}', f'pack.description{project_description}']
        os.makedirs(str(template_texts), exist_ok=True)
        bad_files = ['level.dat_old', 'world_behavior_pack_history.json', 'world_resource_pack_history.json']

        for el in os.listdir(world_folder_path):
            if os.path.isdir(el):
                shutil.copytree(world_folder_path.joinpath(el), world_template)
            
            else:
                if el not in bad_files:
                    shutil.copy(world_folder_path.joinpath(el), world_template)

        manifest: dict = config.world_template_manifest
        for k, v in manifest.items():
            if isinstance(v, list):
                for el in v:
                    if not isinstance(el, dict): continue
                    if 'uuid' in el:
                        manifest[k]['uuid'] = str(uuid.uuid4())
            else:
                if not isinstance(v, dict): continue
                if 'uuid' in v:
                    manifest[k]['uuid'] = str(uuid.uuid4())
            if k == 'uuid':
                manifest['uuid'] = str(uuid.uuid4())
            else:
                continue

        write_to_file(world_template.joinpath('manifest.json'), manifest, writing=True)
        write_to_file(template_texts.joinpath('languages.json'), languages, writing=True)
        write_to_file(template_texts.joinpath('en_US.lang'), texts, writing=True) # world template folder completed
        
        marketing_art = package_path.joinpath('Marketing Art')
        store_art = package_path.joinpath('Store Art')
        temp_path = package_path.joinpath('temp')

        with ZipFile(assets_zip_folder, 'r') as assets:
            temp_path.mkdir()
            assets.extractall(str(temp_path))

        project_file_name = project_name.replace(' ', '').lower()
        for i, file_name in enumerate(os.listdir(str(temp_path))):
            if 'panorama' not in file_name and 'keyart' not in file_name and 'partnerart' not in file_name:
                # marketing art
                marketing_name = temp_path.joinpath(f'{project_file_name}_MarketingScreenshot_{i}.jpg')
                curr_file_path = temp_path.joinpath(file_name)
                curr_file_path.rename(marketing_name)
                shutil.copy(marketing_name, marketing_art)
                # store art
                store_name = store_art.joinpath(f'{project_file_name}_screenshot_{i}.jpg')
                store_img = Image.open(marketing_name)
                store_img.resize((800, 450))
                store_img.save(store_name) # save the resized image to the store art folder with its correct name
                store_img.close()
            else:
                curr_file_path = temp_path.joinpath(file_name)
                if 'panorama' in file_name:
                    panorama_file = os.path.join(temp_path, file_name)
                    new_panorama_name = f'{project_file_name}_panorama_0.jpg'
                    new_panorama_file = store_art.joinpath(new_panorama_name)
                    shutil.move(panorama_file, new_panorama_file) # format the file with the projectname_panorama.jpg format
                if 'keyart' in file_name:
                    thumbnail = Image.open(curr_file_path)
                    thumbnail.resize((800, 450))
                    thumbnail.save(store_art.joinpath(f'{project_file_name}_Thumbnail_0.jpg'))
                    thumbnail.close()
                    marketing_keyart = f'{project_file_name}_MarketingKeyArt.jpg'
                    shutil.move(curr_file_path, marketing_art.joinpath(marketing_keyart))
                if 'partnerart' in file_name:
                    shutil.move(curr_file_path, marketing_art.joinpath(f'{project_file_name}_PartnerArt.jpg'))

        shutil.rmtree(str(temp_path))