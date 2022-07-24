from pathlib import Path
import uuid, os, shutil, typer
from zipfile import ZipFile
from PIL import Image
from addons.helpers.file_handling import write_to_file, data_from_file
import addons.paths as paths

data = data_from_file(Path('../data/config.json'))
projects_path = Path(paths.PROJECTS)
languages = ['en_US']
bp_folders = ['animation_controllers', 'animations', 'blocks', 'features', 'functions', 'items', 'entities', 'structures', 'biomes', 'loot_tables', 'trades']
rp_folders = ['animation_controllers', 'animations', 'items', 'entity', 'models', 'particles', 'render_controllers', *paths.MODELS.values(), *paths.SOUNDS.values(), *paths.TEXTURES.values()]
app = typer.Typer()

@app.command()
def create(project_name: str) -> None:
    """ Creates a new blank project template in the user's dedicated project folder
    
    """
    rp_manifest: dict = data['rp_manifest']
    bp_manifest: dict = data['bp_manifest']
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

    blocks = data['blocks.json']
    sounds = data['sounds.json']
    sound_defs = data['sound_definitions.json']
    terrain = data['terrain_texture.json']
    terrain['resource_pack_name'] = project_name
    items = data['item_texture.json']
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
def package(project_name: str, project_description: str, assets_zip_folder: str) -> None:
    """
    Packages a world for marketplace submission

    :param project_name: the name of the project being packaged
    :param project_description: the description to be used in game for the world template
    :param assets_zip_folder: the path to the zip folder 
    """
    search_name = project_name.lower().replace(' ', '_')
    world_folder_path = r'%LocalAppData%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds\{0}'.format(search_name)

    if not os.path.exists(world_folder_path) or not os.path.exists(assets_zip_folder):
        raise FileNotFoundError('A folder for the world being packaged does not exist or the assets folder provided is invalid!')

    else:
        package_path = os.path.join(package_path, search_name)
        world_template = os.path.join(package_path, 'Content', 'world_template')
        template_texts = os.path.join(world_template, 'texts')
        texts = [f'pack.name={project_name}', f'pack.description{project_description}']
        os.mkdirs(template_texts)
        bad_files = ['level.dat_old', 'world_behavior_pack_history.json', 'world_resource_pack_history.json']

        for el in os.listdir(world_folder_path):
            if os.path.isdir(el):
                shutil.copytree(os.path.join(world_folder_path, el), world_template)
            
            else:
                if el not in bad_files:
                    shutil.copy(os.path.join(world_folder_path, el), world_template)

        manifest: dict = data['world_template_manifest']
        for k, v in manifest.items():
            if type(v) == list:
                for el in v:
                    if type(el) == dict:
                        if 'uuid' in el:
                            manifest[k]['uuid'] = str(uuid.uuid4())
                    else:
                        continue
            else:
                if type(v) == dict:
                    if 'uuid' in v:
                        manifest[k]['uuid'] = str(uuid.uuid4())
                else:
                    continue
            if k == 'uuid':
                manifest['uuid'] = str(uuid.uuid4())

            else:
                continue

        write_to_file(os.path.join(world_template, 'manifest.json'), manifest, writing=True)
        write_to_file(os.path.join(template_texts, 'languages.json'), languages, writing=True)
        write_to_file(os.path.join(template_texts, 'en_US.lang'), texts, writing=True) # world template folder completed
        
        marketing_art = os.path.join(package_path, 'Marketing Art')
        store_art = os.path.join(package_path, 'Store Art')
        temp_path = os.path.join(package_path, 'temp')
        os.mkdir(marketing_art)
        os.mkdir(store_art)

        with ZipFile(assets_zip_folder, 'r') as assets:
            os.mkdir(os.path.join(package_path, 'temp'))
            assets.extractall(temp_path)

        for file_name in os.listdir(os.path.join(package_path, 'temp')):
            file_num : int = 0
            if 'panorama' not in file_name and 'keyart' not in file_name and 'partnerart' not in file_name:
                # marketing art
                marketing_name : str = os.path.join(temp_path,'{0}_MarketingScreenshot_{1}.jpg'.format(project_name.replace(' ', '').lower(), file_num))
                curr_file_path: str = os.path.join(temp_path, file_name)
                os.rename(curr_file_path, marketing_name)
                shutil.copy(marketing_name, marketing_art)
                # store art
                store_name: str = os.path.join(store_art, '{0}_screenshot_{1}.jpg'.format(project_name.replace(' ', '').lower() , file_num))
                store_img = Image.open(marketing_name)
                store_img.resize((800, 450))
                store_img.save(store_name) # save the resized image to the store art folder with its correct name
                store_img.close()
                file_num += 1
            else:
                curr_file_path: str = os.path.join(temp_path, file_name)
                if 'panorama' in file_name:
                    panorama_file = os.path.join(temp_path, file_name)
                    new_panorama_name = '{0}_panorama_0.jpg'.format(project_name.replace(' ', '').lower())
                    new_panorama_file = os.path.join(store_art, new_panorama_name)
                    shutil.move(panorama_file, new_panorama_file) # format the file with the projectname_panorama.jpg format
                elif 'keyart' in file_name:
                    thumbnail = Image.open(curr_file_path)
                    thumbnail.resize((800, 450))
                    thumbnail.save(os.path.join(store_art, '{0}_Thumbnail_0.jpg'.format(project_name.replace(' ', '').lower() )))
                    thumbnail.close()
                    marketing_keyart: str = '{0}_MarketingKeyArt.jpg'.format(project_name.replace(' ', '').lower())
                    shutil.move(curr_file_path, os.path.join(marketing_art, marketing_keyart))

                elif 'partnerart' in file_name:
                    shutil.move(curr_file_path, os.path.join(marketing_art, '{0}_PartnerArt.jpg'.format(project_name.replace(' ', '').lower() )))
                else:
                    continue

        shutil.rmtree(temp_path)