from addons.custom.component import CustomComponent, verify_component_properties, Range
from typing import Any, Annotated

class Component(CustomComponent):
    families: list[str]
    health: Annotated[int, Range(1, 1000)]
    height: float
    width: float
    speed: float = 0.0

    @staticmethod
    def get_name() -> str:
        return 'basics'
        
    @verify_component_properties
    def build_self(self, *, root: dict[str, Any], properties: dict[str, Any]) -> None:
        root['minecraft:physics'] = {}
        root['minecraft:type_family'] = {
            'family': properties['families']
        }
        root['minecraft:health'] = {
            'value': properties['health']
        }
        root['minecraft:collision_box'] = {
            'height': properties['height'],
            'width': properties['height']
        }
        root['minecraft:movement'] = {
            'value': properties['speed']
        }