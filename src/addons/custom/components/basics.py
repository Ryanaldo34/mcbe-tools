from addons.custom.component import CustomComponent, verify_component_properties
from typing import Any

class Component(CustomComponent):
    families: list
    health: int
    height: float
    width: float
    speed: float

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