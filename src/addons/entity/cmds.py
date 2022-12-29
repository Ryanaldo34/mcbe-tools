import typer
import addons.entity.client_entity as client_entity
from addons.sounds import implement_sounds
from addons.helpers.file_handling import write_to_file, data_from_file
from addons.entity.client_entity.factory import ClientEntityFactory
from addons.entity.client_entity.versions import ClientEntityV1_8_0, ClientEntityV1_10_0
from addons.entity.behaviors import EntityBehaviors
from addons.entity.builder import build_entity, build_arrays
from addons.entity.client_entity.render_controller import RenderController
from addons.entity.client_entity.entity import Entity
from .define import *

from pathlib import Path
from addons.errors import *
from colorama import Fore, Back, Style
from typing import Optional

app = typer.Typer()

@app.command()
def define( rp_folder: Path = typer.Argument(None, help='ABS path to the resource pack'),
            entity_file: Path = typer.Argument(None, help='ABS path to the entity behavior file'),
            fv: str = typer.Option('1.8.0', help='The format version of the client entity'),
            anim: Path = typer.Option('', help='Specify name of the animation file for the entity'),
            ac: Path = typer.Option('', help='Specify name of animation controller file for the entity'),
            geo: Path = typer.Option('', help='Specify a geometry for the entity'),
            material: Optional[list[str]] = typer.Option(None, help='Add a material to the entity'),
            texture: Path = typer.Option(None, help='Specify the texture name of an entity'),
            dummy: bool = typer.Option(False, help='If the entity is a dummy'),
            ac_req: bool = typer.Option(False, help='If an ac is required'),
            anim_req: bool = typer.Option(False, help='If an animation is required'),
            sounds_req: bool = typer.Option(False, help='If the entity need sounds'),
            texture_req: bool = typer.Option(True, help='If the entity requires a texture')
    ) -> None:
    """
    Writes the client entity and render controller files of an entity
    """
    # remake paths that are added to the entity class methods for defining information and make abc for animations and animation controller parsing
    try:
        valid_formats = ['1.8.0', '1.10.0']
        ce_builder = ClientEntityFactory()
        ce_builder.register_builder('1.8.0', ClientEntityV1_8_0)
        ce_builder.register_builder('1.10.0', ClientEntityV1_10_0)

        if not entity_file.exists():
            raise typer.BadParameter('The entity file provided DNE', param=entity_file)
        if not rp_folder.exists():
            raise typer.BadParameter('The resource pack provided DNE', param=rp_folder)
        if fv not in valid_formats:
            print(f'{fv}, is not a valid client entity format version!')
            raise typer.Abort()

        entity_data = data_from_file(entity_file)
        behaviors = EntityBehaviors(entity_data)
        name = behaviors.real_name
        geo_path = rp_folder.joinpath('models', 'entity', f'{name}.geo.json') if not geo else rp_folder.joinpath('models', 'entity', f'{geo}.geo.json')
        anim_file = anim if anim else rp_folder.joinpath('animations', f'{name}.animation.json')
        ac_file = ac if ac else rp_folder.joinpath('animation_controllers', f'{name}.animation_controllers.json')
        texture_path = texture
        if not texture_path:
            file = rp_folder.joinpath('textures', 'entity', f'{name}.png')
            texture_path = file if file.exists() else rp_folder.joinpath('textures', 'entity', name)
        
        if dummy:
            geo_object = client_entity.geo.Geometry(data_from_file(geo_path), dummy=True)
            materials = { 'default': 'entity_alphatest' }
            entity = Entity(materials, geo_object, behaviors)
            name = entity.name.replace('_', ' ').title()
            # client entityy
            ce = ce_builder.create(fv, entity)
            ce.write_file(rp_folder, dummy=True)
            return None

        geo_data = data_from_file(geo_path)
        
        if geo_data is None and GEO_ERRORS:
            raise MissingGeometryError('The entity is missing a required geometry definition!')
        # define all the short_name: value dictionaries for the entity
        materials = define_materials(material)
        textures_dict = define_textures(texture_path, req=texture_req)
        anim_dict = define_animations(anim_file, req=anim_req)
        ac_dict = define_acs(ac_file, req=ac_req)
        geo_object = client_entity.geo.Geometry(geo_data, dummy=False)
        sounds = implement_sounds(name, rp_folder)
        spawn_egg = define_spawn_egg(name, rp_folder)
        # create the entity object
        entity = Entity(
            materials,
            geo_object,
            behaviors,
            textures=textures_dict,
            anims=anim_dict,
            acs=ac_dict,
            spawn_egg=spawn_egg,
            sounds=sounds
        )
        # client entity
        ce = ce_builder.create(fv, entity)
        name = entity.name.replace('_', ' ').title()
        # create render controller
        if entity.has_default_rc:
            ce.add_rc('controller.render.default')
            build_entity(entity_file, None, behaviors)
        else:
            arrays = build_arrays(entity, rp_folder)
            render_controller = RenderController(f'controller.render.{entity.name}', arrays, materials)
            build_entity(entity_file, render_controller, behaviors)
            render_controller.map_mats_to_bones()
            # write render controller
            render_controller.convert_to_file(rp_folder.joinpath('render_controllers'))
            ce.add_rc(render_controller)
        # write the client_entity file
        ce.write_file(rp_folder, dummy=False)
        entity.write_lang(rp_folder)
        # log to console
        print(f'{Fore.GREEN}Successfully Defined {name}!')
        print(Style.RESET_ALL)

    except MissingAnimationControllerFile as exc:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing animation controller requirement!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.animation_controllers.json?\n', '+Is the the file saved in RP/animation_controllers', Style.RESET_ALL)
        raise typer.Abort() from exc

    except MissingAnimationError as exc:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing animation requirement!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.animation.json?\n', '+Is the the file saved in RP/animations?', Style.RESET_ALL)
        raise typer.Abort() from exc

    except MissingGeometryError as exc:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing a geometry definition (model)!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.geo.json?\n', '+Is the the file saved in RP/models/entity', Style.RESET_ALL)
        raise typer.Abort() from exc

    except MissingSoundError as exc:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing sound effects requirement!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the entity sound folder in RP/sounds?\n', Style.RESET_ALL)
        raise typer.Abort() from exc
        
    except MissingTextureError as exc:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing texture file!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.png?\n', '+Is the the file saved in RP/textures/entity or RP/textures/entity/entity_name?', Style.RESET_ALL)
        raise typer.Abort() from exc

@app.command()
def add_sounds(
    rp_path: Path = typer.Argument(default=None), 
    entity_id: str = typer.Argument(default=None)
):
    if not rp_path.exists():
        raise typer.BadParameter('The resource pack provided does not exist')

    sounds_path = rp_path.joinpath('sounds', 'entity')
    ce_path = rp_path.joinpath('entity', f'{entity_id}.entity.json')

    if not ce_path.exists() or not sounds_path.exists():
        raise typer.BadParameter('You are missing one or more requirements in the resource pack!')

    ce_data = data_from_file(ce_path)
    ce_data['minecraft:client_entity']['description']['sound_effects'] = implement_sounds(entity_id, rp_path)
    write_to_file(ce_path, ce_data)