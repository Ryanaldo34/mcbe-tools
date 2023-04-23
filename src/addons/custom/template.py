from dataclasses import dataclass
from pathlib import Path
from typing import Any
from addons.helpers import write_to_file
from importlib import import_module
import os

@dataclass(frozen=True, kw_only=True)
class CustomEntityTemplate:
    """A template that can be generated that contains a combination of commonly used events, components, etc."""
    name: str
    components: dict[str, Any]
    component_groups: dict[str, Any] = None
    events: dict[str, Any] = None
    experimental: bool = False
    format_version: str = '1.19.0'
    aliases: dict[str, dict[str, Any]] = None
    properties: dict[str, dict[str, Any]] = None
    permutations: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.permutations is not None:
            self.experimental = True

    def build_self(self, f: Path, identifier: str) -> None:
        output = {
            'format_version': self.format_version,
            'minecraft:entity': {
                'description': {
                    'identifier': identifier,
                    'is_spawnable': True,
                    'is_summonable': True,
                    'is_experimental': self.experimental
                },
                'components': self.components
            }
        }
        if self.component_groups:
            assert self.events, 'There must events for a template with components groups'
            output['minecraft:entity']['component_groups'] = self.component_groups
            output['minecraft:entity']['events'] = self.events

        if self.properties:
            assert self.events, 'You need events with properties'
            output['minecraft:entity']['description']['properties'] = self.properties
            if self.aliases is not None:
                output['minecraft:entity']['description']['aliases'] = self.aliases
            output['minecraft:entity']['permutations'] = self.permutations
            output['minecraft:entity']['events'] = self.events

        write_to_file(f, output)

@dataclass(frozen=True, kw_only=True)
class CustomItemTemplate:
    name: str
    components: dict[str, dict[str, Any]]
    events: dict[str, dict[str, Any]] = None
    format_version: str = '1.19.0'

    def build_self(self, f: Path, identifier: str) -> None:
        output = {
            'format_version': self.format_version,
            'minecraft:item': {
                'description': {
                    'identifier': identifier
                },
                'components': self.components
            }
        }
        if self.events:
            output['minecraft:item']['events'] = self.events

@dataclass(frozen=True, kw_only=True)
class CustomBlockTemplate:
    name: str
    components: dict[str, dict[str, Any]]
    format_version: str = '1.19.0'
    properties: dict[str, dict[str, Any]] = None
    permutations: list[dict[str, Any]] = None
    events: dict[str, dict[str, Any]] = None

    def build_self(self, f: Path, identifier: str) -> None:
        output = {
            'format_version': self.format_version,
            'minecraft:block': {
                'description': {
                    'identifer': identifier
                },
                'components': self.components
            }
        }
        if self.events:
            output['minecraft:block']['events'] = self.events
        if self.properties:
            output['minecraft:block']['description']['properties'] = self.properties
            output['minecraft:block']['permutations'] = self.permutations

Template = CustomBlockTemplate | CustomItemTemplate | CustomEntityTemplate

class CustomTemplateRegistry:
    def __init__(self):
        self._data: dict[str, Template] = {}

    def register_templates(self) -> None:
        """
        Adds all custom template to registry so that they can be used in building entity templates
        """
        templates = [os.path.split(template)[-1].replace('.py', '') for template in os.listdir(str(Path(__file__).parent.joinpath('templates'))) if '__init__' not in template]
        for template in templates:
            if template == '__pycache__': continue
            try:
                module = import_module(f'addons.custom.templates.{template}')
                if hasattr(module, 'template'):
                    data: Template = getattr(module, 'template')
                    self._data[data.name] = data
                else:
                    raise AttributeError('A template must be defined correctly')
            except AttributeError:
                print(f'Template not found: {template}')

    def get_template_builder(self, name: str) -> CustomEntityTemplate:
        return self._data.get(name)

template_registry = CustomTemplateRegistry()
template_registry.register_templates()