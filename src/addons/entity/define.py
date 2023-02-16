"""Contains helper functions for defining an entity

"""
from addons.entity.client_entity.entity import Entity
from addons.errors import *
from addons.helpers.file_handling import data_from_file, write_to_file

import os
from pathlib import Path

def define_materials(materials: list[str]) -> dict[str, str]:
    """Defines the shortname: value pairs for materials in the client entity file

    Parameters
    ----------
    materials : list[str]
        The list of materials entered by the user

    Returns
    -------
    dict[str, str]
        The short_name: material map for the entity
    """
    if not materials:
        return {'default': 'entity_alphatest'}

    material_names = []
    for material in materials:
        name = input(f'what is the short-name of the material -> {material}: ')
        material_names.append(name)
    return { name: value for name, value in zip(material_names, materials) }

def define_textures(texture_path: Path, *, req: bool = False) -> dict[str, str] | None:
    """Creates the short_name: texture dictionary for entity textures

    Parameters
    ----------
    texture_path : Path
        The path to the texture or textures folder
    req : bool, optional
        If the texture is required for the entity, by default False

    Returns
    -------
    dict[str, str] | None
        The short_name: path map for each texture

    Raises
    ------
    MissingTextureError
        If the texture is required, it returns a user error that states the texture is missing
    """
    if not texture_path.exists() and req:
        raise MissingTextureError()
    
    if texture_path.is_file():
        return {'default': f'textures/entity/{texture_path.stem}'}
    
    textures = [str(textr) for textr in texture_path.rglob('*.png')]
    for i, textr in enumerate(textures):
        pos = textr.find('textures')
        textr = textr[pos:].replace('.png', '').replace(os.sep, '/')
        textures[i] = textr
    return { textr.split('/')[-1].split('_')[-1]: textr for textr in textures }

def define_animations(anim_file: Path, *, req: bool = False) -> dict[str, str] | None:
    """Defines the short_name: animation dictionary for an entity's animations

    Parameters
    ----------
    anim_file : Path
       The path to the animations file
    req : bool, optional
        Whether this entity has animations required to be defined, by default False

    Returns
    -------
    dict[str, str] | None
        The short_name: animation dictionary

    Raises
    ------
    MissingAnimationError
        If the entity has a required animation file but none is found, this error raised
    """
    if req and not anim_file.is_file():
        raise MissingAnimationError()
    
    anim_data = data_from_file(anim_file)
    return { animation.split('.')[-1]: animation for animation in list(anim_data['animations']) } if anim_data is not None else None


def define_acs(acs_file: Path, *, req: bool = False) -> dict[str, str] | None:
    """Creates the short_name: controller dictionary for entity animation controllers

    Parameters
    ----------
    acs_file : Path
        The path to animation controller file
    req : bool, optional
        Whether an animation controller is required for the entity definition, by default False

    Returns
    -------
    dict[str, str] | None
        The short_name: controller map

    Raises
    ------
    MissingAnimationControllerFile
        If the entity requires an animation controller for its definition, but none is found
    """
    if req and not acs_file.is_file():
        raise MissingAnimationControllerFile()
    
    ac_data = data_from_file(acs_file)
    return [{controller.split('.')[-1]: controller} for controller in list(ac_data['animation_controllers'])] if ac_data is not None else None

def define_spawn_egg(name: str, rp_path: Path, base_color: str = None, overlay_color: str = None) -> dict:
    """
    Creates the spawn egg dictionary to be added to the client entity file of an entity

    :param base_color: A hex code of the color to be used for the base color of the egg
    :param overlay_color: A hex code of the color to be used as an overlay for the egg
    :param texture: The texture short name to be used as the spawn egg texture
    """
    spawn_egg_texture = rp_path.joinpath('textures', 'items', f'{name}.png')
    spawn_egg = {}

    if spawn_egg_texture.exists():
        spawn_egg['texture'] = name
        spawn_egg['texture_index'] = 0
        item_atlas_path = rp_path.joinpath('textures', 'item_texture.json')

        item_atlas = data_from_file(item_atlas_path)
        if item_atlas is not None:
            item_atlas['texture_data'][name] = {}
            item_atlas['texture_data'][name]['textures'] = f'textures/items/{name}'
            write_to_file(item_atlas_path, item_atlas)

        return spawn_egg

    if base_color and overlay_color:
        spawn_egg['base_color'] = base_color
        spawn_egg['overlay_color'] = overlay_color

    else:
        spawn_egg['texture'] = 'spawn_egg'
        spawn_egg['texture_index'] = 0

    return spawn_egg 