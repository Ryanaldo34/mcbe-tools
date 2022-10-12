import typer
import addons.entity.client_entity as client_entity
from addons.sounds import implement_sounds
from addons.helpers.file_handling import write_to_file, data_from_file
from addons.entity.client_entity.factory import ClientEntityFactory
from addons.entity.client_entity.versions import ClientEntityV1_8_0, ClientEntityV1_10_0
from addons.entity.behaviors import EntityBehaviors
from pathlib import Path
from addons.errors import *
from colorama import Fore, Back, Style

Entity = client_entity.entity.Entity
RenderController = client_entity.render_controller.RenderController
app = typer.Typer()

@app.command()
def define( rp_folder: Path = typer.Argument(None, help='ABS path to the resource pack'),
            entity_file: Path = typer.Argument(None, help='ABS path to the entity behavior file'),
            fv: str = typer.Option('1.8.0', help='The format version of the client entity'),
            anim: str = typer.Option('', help='Specify name of the animation file for the entity'),
            ac: str = typer.Option('', help='Specify name of animation controller file for the entity'),
            geo: str = typer.Option('', help='Specify a geometry for the entity'),
            texture: str = typer.Option('', help='Specify the texture name of an entity'),
            default: bool = typer.Option(True, help='Whether the entity has a default rc'),
            dummy: bool = typer.Option(False, help='If the entity is a dummy'),
            ac_req: bool = typer.Option(False, help='If an ac is required'),
            anim_req: bool = typer.Option(False, help='If an animation is required'),
            sounds: bool = typer.Option(False, help='If the entity need sounds'),
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
        if not fv in valid_formats():
            print(f'{fv}, is not a valid client entity format version!')
            raise typer.Abort()

        name = entity_file.stem
        entity_data = data_from_file(entity_file)
        behaviors = EntityBehaviors(entity_data)
        behaviors.build(entity_file)
        geo_path = rp_folder.joinpath('models', 'entity', f'{name}.geo.json') if not geo else rp_folder.joinpath('models', 'entity', f'{geo}.geo.json')
        
        if dummy:
            geo_object = client_entity.geo.Geometry(data_from_file(geo_path), dummy=True)
            materials = { 'default': 'entity_alphatest' }
            entity = Entity(materials, geo_object, behaviors)
            name = entity.name.replace('_', ' ').title()
            # client entityy
            ce = ce_builder.create(fv, entity)
            ce.write_file(rp_folder, dummy=True)

        else:
            materials = Entity.define_materials(default)
            geo_data = data_from_file(geo_path)
            
            if geo_data is None and GEO_ERRORS:
                raise MissingGeometryError('The entity is missing a required geometry definition!')

            geo_object = ce.geo.Geometry(geo_data, dummy=False)
            entity = Entity(materials, geo_object, behaviors, rp_path=rp_folder, anim_req=anim_req, ac_req=ac_req, texture_req=texture_req)
            # client entity
            ce = ce_builder.create(fv, entity)
            name = entity.name.replace('_', ' ').title()
            # particles & sounds defined
            entity.sounds = implement_sounds(entity.name, rp_folder)
            # create render controller, no need for one if it is a dummy
            render_controller = RenderController(entity, f'controller.render.{entity.name}')
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

    except MissingAnimationControllerFile:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing animation controller requirement!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.animation_controllers.json?\n', '+Is the the file saved in RP/animation_controllers', Style.RESET_ALL)
        raise typer.Abort()

    except MissingAnimationError:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing animation requirement!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.animation.json?\n', '+Is the the file saved in RP/animations?', Style.RESET_ALL)
        raise typer.Abort()

    except MissingGeometryError:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing a geometry definition (model)!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.geo.json?\n', '+Is the the file saved in RP/models/entity', Style.RESET_ALL)
        raise typer.Abort()

    except MissingSoundError:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing sound effects requirement!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the entity sound folder in RP/sounds?\n', Style.RESET_ALL)
        raise typer.Abort()
        
    except MissingTextureError:
        print(f'{Back.BLACK}{Style.BRIGHT}{Fore.RED}FATAL ERROR:\n', f'{Back.RESET}', f'The entity in {entity_file} could not be defined due to a missing texture file!', Style.RESET_ALL)
        print(f'{Style.DIM}{Fore.YELLOW}Troubleshooting:\n', '+Is the file named entity_name.png?\n', '+Is the the file saved in RP/textures/entity or RP/textures/entity/entity_name?', Style.RESET_ALL)
        raise typer.Abort()

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