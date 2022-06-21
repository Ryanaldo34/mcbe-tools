import uuid, os, shutil, typer
from zipfile import ZipFile
from PIL import Image
from .helpers.file_handling import write_to_file, data_from_file

config_data = data_from_file(r'C:\Users\ryan\OneDrive\Documents\projects\bedrockscript\data\config.json')
projects_path: str = config_data['project_storage']
languages = ['en_US']
app = typer.Typer()

@app.command()
def create(project_name: str) -> None:
    """ Creates a new blank project template in the user's dedicated project folder
    
    """
    bp_folders: list = ['animation_controllers', 'animations', 'blocks', 'features', 'functions', 'items', 'entity', 'structures', 'biomes', 'loot_tables', 'trades']
    rp_folders: list = ['animation_controllers', 'animations', 'item', 'entity', 'models', 'models{0}entity'.format(os.sep), 'particles', 'sounds', 'render_controllers', 
    'textures', 'textures{0}entity'.format(os.sep), 'textures{0}items'.format(os.sep)]
    rp_manifest: dict = config_data['rp_manifest']
    bp_manifest: dict = config_data['bp_manifest']
    rp_header = str(uuid.uuid4())
    rp_name: str = project_name.lower().replace(' ', '_') + '_RP'
    bp_name: str = project_name.lower().replace(' ', '_') + '_BP'

    os.chdir(projects_path)
    os.mkdir(project_name)
    os.mkdir(os.path.join(project_name, rp_name))
    os.mkdir(os.path.join(project_name, bp_name))

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

        os.mkdir(os.path.join(project_name, rp_name, folder))

    for folder in bp_folders:

        os.mkdir(os.path.join(project_name, bp_name, folder))

    write_to_file(os.path.join(project_name, rp_name, 'manifest.json'), data=rp_manifest, writing=True)
    write_to_file(os.path.join(project_name, bp_name, 'manifest.json'), data=bp_manifest, writing=True)

@app.command()
def build(project_name: str) -> None:
    """ Executes the script to "build" the project by running tests and moving the changes to the MC folders
    
    :param project_name: the name of the project that is being built, the world names and packs names folders must match for the script to work
    """
    project_path: str = os.path.join(projects_path, project_name)
    project_bp: str = os.path.join(project_path, '{0}_BP'.format(project_name.replace(' ', '_').lower()))
    project_rp: str = os.path.join(project_path, '{0}_RP'.format(project_name.replace(' ', '_').lower()))
    if not os.path.exists(project_path):
        raise FileNotFoundError('The project has not yet been created!')

    dev_bps: str = r'%LocalAppData%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\development_behavior_packs'
    dev_rps: str = r'%LocalAppData%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\development_resoource_packs'

    shutil.copy(project_bp, dev_bps)
    shutil.copy(project_rp, dev_rps)

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
        world_template = os.path.join(package_path, 'world_template')
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

        manifest: dict = config_data['world_template_manifest']
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