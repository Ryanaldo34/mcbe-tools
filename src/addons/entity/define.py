import os, typer, json
import addons.entity.client_entity as ce
from addons.sounds import implement_sounds
from addons.helpers.file_handling import *
from pathlib import Path

Entity = ce.entity.Entity
RenderController = ce.render_controller.RenderController
app = typer.Typer()

def define_materials(default: bool) -> dict[str, str]:
    """Defines the shortname: value pairs for materials in the client entity file
    
    :param materials: the string gathered from user input
    """
    if not default:
        materials = input('Enter the names of materials to be used in the entity (use space to separate): ').split(' ')
        material_names = []
        for material in materials:
            name = input(f'what is the short-name of the material-> {material}: ')
            material_names.append(name)

        return { name: value for name, value in zip(material_names, materials) }
    else:
        return {'default': 'entity_alphatest'}


def define_animations(entity: Entity, rp_folder: Path) -> None:
    """
    Gets the animation file path and interprets the data from the file to encapsulate it in the entity object
    
    :param rp_folder: the resource pack folder location
    :param entity: the entity being defined
    """
    name = entity.name
    anim_file = rp_folder.joinpath('animations', f'{name}.animation.json')
    anim_data = data_from_file(anim_file)

    if anim_file.is_file():
        entity.anims = { animation.split('.')[-1]: animation for animation in list(anim_data['animations']) }

    else:
        pass

def define_animation_controllers(entity: Entity, rp_folder: Path) -> None:
    """ 
    Gets the animation controller file path and interprets data from the file to encapsulate it in the entity object

    :param rp_folder: the resource pack folder location
    :param entity: the entity being defined
    """
    name = entity.name
    ac_file = rp_folder.joinpath('animation_controllers', f'{name}.animation_controllers.json')

    if ac_file.is_file():
        ac_data = data_from_file(ac_file)
        entity.acs = [ {controller.split('.')[-1]: controller} for controller in list(ac_data['animation_controllers']) ]

    else:
        pass

def define_textures(entity: Entity, rp_folder: Path):
    """ 
    Gets the texture folder or texture file path and formats the paths into aceptable data for MC and encapsulates it in the entity object
    
    :param rp_folder: the resource pack folder location
    :param working_file: the dir where the script is running
    :param entity: the entity being defined
    """
    name = entity.name
    entity_textr_folder = rp_folder.joinpath('textures', 'entity', name)
    entity_textr_file = rp_folder.joinpath('textures', 'entity', f'{name}.png')

    if entity_textr_folder.exists():
        textures = [str(textr) for textr in entity_textr_folder.rglob('*.png')]
        for i, textr in enumerate(textures):
            pos = textr.find('textures')
            textr = textr[pos:].replace('.png', '').replace(os.sep, '/')
            textures[i] = textr

        short_name_val_map = { textr.split('/')[-1].split('_')[-1]: textr for textr in textures }
        entity.textr_name_val_map = short_name_val_map
        entity.textr_names = [f'Texture.{short_name}' for short_name in list(short_name_val_map)]
        entity.textr_paths = list(short_name_val_map.values())
        
    else:
        if entity_textr_file.exists():
            entity.textr_name_val_map = {'default': f'textures/entity/{name}'}
            entity.textr_names = ['Texture.default']
            entity.textr_paths = [f'textures/entity/{name}']

        else:
            entity.textr_name_val_map = None

@app.command()
def define( rp_folder: Path = typer.Argument(None),
            entity_file: Path = typer.Argument(None),
            default: bool = typer.Option(True, help='Whether the entity has a default rc'),
            dummy: bool = typer.Option(False, help='If the entity is a dummy')) -> None:
    """
    Writes the client entity and render controller files of an entity
    """
    materials: dict = define_materials(default)
        
    geo_data = {}
    geo_path = rp_folder.joinpath('models', 'entity', f'{entity_file.stem}.geo.json')
    entity_data = data_from_file(entity_file)
    behaviors = ce.behaviors.EntityBehaviors(entity_data)
    geo_data = data_from_file(geo_path)
    geo_object = ce.geo.Geometry(geo_data, dummy=False) if not dummy else ce.geo.Geometry(geo_data, dummy=True)
    entity = Entity(materials, geo_object, behaviors)
    # animations and textures defined (update with path obj)
    define_animations(entity, rp_folder)
    define_animation_controllers(entity, rp_folder)
    define_textures(entity, rp_folder)
    # particles & sounds defined
    entity.sounds = implement_sounds(entity.name, rp_folder)
    # create render controller, no need for one if it is a dummy
    if dummy:
        print('writing ce file...')
        print(entity.write_client_entity(os.path.join(rp_folder, 'entity')))

    else:
        bones = geo_object.get_bones()
        rc_name = 'controller.render.{0}'.format(entity.name)
        render_controller = RenderController(entity, 'controller.render.{0}'.format(entity.name, rc_name), bones)

        render_controller.map_mats_to_bones()
        print(json.dumps(render_controller.convert_to_file(rp_folder.joinpath('render_controllers')), indent=4, sort_keys=True))

    # write the client_entity file
    print(json.dumps(entity.write_client_entity(rp_folder), indent=4, sort_keys=True))
    entity.write_lang(rp_folder)

@app.command()
def generate(template: str, bp_path: str):
    """
    Generate an entity's behavior file from a select template
    """
    pass