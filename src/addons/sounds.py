import os
from pathlib import Path
from .helpers.file_handling import data_from_file, write_to_file
import pprint

def createDefs(RP_PATH: Path, category_path: Path, definition_data: dict, category: str = 'neutral') -> dict:
    """
    Creates the sound definitions for a given category path
    """
    if not category_path.exists():
        print('There are not sounds available')
        return None

    def_file = RP_PATH.joinpath('sounds', 'sound_definitions.json')
    sounds: list[str] = [str(sound) for sound in category_path.glob('*') if sound.is_file()] # free floating sounds in the sounds folder
    subcategories: list[Path] = [subcat for subcat in category_path.glob('*') if subcat.is_dir()] # sub-folders in the sounds folder (entity folders)
    definitions = definition_data['sound_definitions']

    for sound in sounds: # if there are sounds just floating in the sounds folder without a sub folder
        sound_path = sound[sound.find('sounds'):].replace(os.sep, '/').replace('.ogg', '')
        sound_name = sound_path.split('/')[1:].join('.')
        definitions[sound_name] = {}
        definitions[sound_name]['category'] = category
        definitions[sound_name]['sounds'] = []
        definitions[sound_name]['sounds'].append(sound_path)

    for subcategory in subcategories:
        sound_paths: list[str] = [
            str(sound)[str(sound).find('sounds'):].replace(os.sep, '/').replace('.ogg', '') for sound in subcategory.glob('*') if sound.is_file()
        ] # sounds that only have 1 sound path and are not randomized when played
        for sound_path in sound_paths:
            sound_category = sound_path.split('/')[-3]
            subcategory = sound_path.split('/')[-2]
            name = sound_path.split('/')[-1]
            sound_name = '{0}.{1}.{2}'.format(sound_category,subcategory,name)
            definitions[sound_name] = {}
            definitions[sound_name]['category'] = category
            definitions[sound_name]['sounds'] = []
            definitions[sound_name]['sounds'].append(sound_path)

        sub_subcategories: list[Path] = [subcat for subcat in category_path.joinpath(subcategory).glob('*') if subcat.is_dir()]
        for sub_subcat in sub_subcategories:
            sound_paths = [str(sound)[str(sound).find('sounds'):].replace(os.sep, '/').replace('.ogg', '') for sound in sub_subcat.rglob('*.ogg')]
            sub_subcat = str(sub_subcat).split(os.sep)[-1]
            sound_name = '{0}.{1}.{2}'.format(sound_category, subcategory, sub_subcat)
            definitions[sound_name] = {}
            definitions[sound_name]['category'] = category
            definitions[sound_name]['sounds'] = sound_paths
    # create the sound_definitions.json
    write_to_file(def_file, definition_data)
    return definition_data

def define_block_sounds(rp_path: Path, namespace: str):
    """
    Defines all block sounds
    """
    sounds_file = rp_path.joinpath('sounds.json')
    sound_definitions = rp_path.joinpath('sounds', 'sound_definitions.json')
    block_sounds = rp_path.joinpath('sounds', 'block')
    if not block_sounds.exists(): rp_path.joinpath('sounds').mkdir('block')
    definitions: dict
    sound_data: dict = data_from_file(sounds_file) if sounds_file.exists() else {'block_sounds': {}}
    if sound_definitions.exists():
        definitions = data_from_file(sound_definitions)
    
    else:
        definitions = {
            'format_version': '1.14.0',
            'sound_definitions': {}
        }
    
    definitions = createDefs(rp_path, block_sounds, definitions, category='block')
    block_sound_defs = [sound for sound in list(definitions) if sound.startswith('block')]
    for sound in block_sound_defs:
        block_id = '{0}:{1}'.format(namespace, sound.split('.')[1])
        # check if the block has already been added as a key
        if block_id not in sound_data['block_sounds']: sound_data['block_sounds'][block_id] = {}
        sound_data['block_sounds'][block_id]['volume'] = 1.0
        sound_data['block_sounds'][block_id]['pitch'] = 1.0
        # add the sound event to the sounds
        sound_event = sound.split('.')[-1] if sound_event.split('.')[-1] != 'use' else 'item.use.on'
        assert (sound_event in ['break', 'hit', 'item.use.on', 'power.off', 'power.on']), 'The sound event for the block is not valid!'
        # add the properties to the sound
        sound_data['block_sounds'][block_id][sound_event] = {}
        sound_data['block_sounds'][block_id][sound_event]['sound'] = sound
        sound_data['block_sounds'][block_id][sound_event]['pitch'] = 1.0
        sound_data['block_sounds'][block_id][sound_event]['volume'] = 1.0

    write_to_file(sounds_file, sound_data)

def implement_sounds(entity: str, rp_path: Path) -> dict:
    """
    Implements entity sounds for an entity
    """
    sounds_path = rp_path.joinpath('sounds', 'sound_definitions.json')
    sounds_file = rp_path.joinpath('sounds.json')
    sound_events: dict = {}
    sound_defs: dict = {}

    if sounds_file.exists():
        sound_events = data_from_file(sounds_file)

    else:
        sound_events['entity_sounds'] = {}
        sound_events['entity_sounds']['entities'] = {}

    if sounds_path.exists():
        sound_defs = data_from_file(sounds_path)
        sound_defs = createDefs(rp_path, rp_path.joinpath('sounds', 'entity'), sound_defs)

    else:
        sound_defs = {
            'format_version': '1.14.0',
            'sound_definitions': {}
        }
        sound_defs = createDefs(rp_path, rp_path.joinpath('sounds', 'entity'), sound_defs)

    ce_sound_map = {}
    for sound in sound_defs['sound_definitions'].keys():
        sound_split = sound.split('.')
        # see if the sound is in the entity category
        if sound_split[0] == 'entity' and sound_split[1] == entity:
            # check if the sound should be an automatic event for the entity, requires the sound file to be named correctly
            if sound_split[-1] in ['ambient', 'hurt', 'death', 'step', 'fall', 'splash', 'attack', 'shoot']:
                # the name of the entity will be second in the sound split
                entity_name = sound_split[1]
                if entity_name not in sound_events['entity_sounds']['entities']:
                    sound_events['entity_sounds']['entities'][entity_name] = {}
                    sound_events['entity_sounds']['entities'][entity_name]['volume'] = 1.0
                    sound_events['entity_sounds']['entities'][entity_name]['pitch'] = 1.0
                    sound_events['entity_sounds']['entities'][entity_name]['events'] = {}

                sound_events['entity_sounds']['entities'][entity_name]['events'][sound_split[-1]] = {}
                sound_events['entity_sounds']['entities'][entity_name]['events'][sound_split[-1]]['sound'] = sound
                sound_events['entity_sounds']['entities'][entity_name]['events'][sound_split[-1]]['volume'] = 0.25
                sound_events['entity_sounds']['entities'][entity_name]['events'][sound_split[-1]]['pitch'] = 1.0

            else:
                ce_sound_map[sound_split[-1]] = sound
        # for sounds that do not to be added into the sounds.json file
        else:
           continue

    write_to_file(sounds_file, sound_events)
    return ce_sound_map if len(ce_sound_map) > 0 else None

def implement_sound_effects(rp_path: Path):
    """
    Implements generic sound effects that are not block or entity related
    """
    pass

def implement_player_sounds(rp_path: Path):
    """
    Implements all sounds relating to the player
    """