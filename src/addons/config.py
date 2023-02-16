"""Holds all the configuration commands"""
import os
import json
from pathlib import Path
from addons.helpers.file_handling import data_from_file

class MCBEConfig():
    """Encapsulates the configuration data for the project
    """
    def __init__(self, config_path: Path):
        self.__data = data_from_file(config_path)
        
    @property
    def projects_path(self) -> Path:
        return Path(self.__data.get('projects_path')).absolute()
    
    @property
    def entity_models_path(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('entity_models').replace('/', os.sep)
    
    @property
    def block_models_path(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('block_models').replace('/', os.sep)
    
    @property
    def entity_textures_path(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('entity_textures').replace('/', os.sep)
    
    @property
    def block_textures_path(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('block_textures').replace('/', os.sep)
    
    @property
    def item_textures_path(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('item_textures').replace('/', os.sep)
    
    @property
    def entity_sounds_path(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('entity_sounds').replace('/', os.sep)
    
    @property
    def block_sounds_path(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('block_sounds').replace('/', os.sep)
    
    @property
    def player_sounds(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('player_sounds').replace('/', os.sep)
    
    @property
    def misc_sounds(self) -> str:
        return self.__data.get('resourcepack_file_paths').get('misc_sounds').replace('/', os.sep)
    
    @property
    def all_sound_paths(self) -> list[str]:
        return [self.misc_sounds, self.player_sounds, self.block_sounds_path, self.entity_sounds_path]
    
    @property
    def all_model_paths(self) -> list[str]:
        return [self.block_models_path, self.entity_models_path]
    
    @property
    def all_texture_paths(self) -> list[str]:
        return [self.block_textures_path, self.entity_textures_path, self.item_textures_path]

config = MCBEConfig(Path(__file__).parent.parent.joinpath('config.json'))