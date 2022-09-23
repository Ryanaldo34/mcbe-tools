from addons.custom.component import CustomComponent, verify_component_properties
from typing import Any

class Component(CustomComponent):
    bubbles: bool
    can_breach: bool
    can_pass_doors: bool
    can_jump: bool
    can_sink: bool
    underwater_movement: float
    stroll_interval: int = 25

    @property
    def name(self) -> str:
        return 'amphibian'
    
    @verify_component_properties
    def build_self(self, *, root: dict[str, Any], properties: dict[str, Any]) -> None:
        root['minecraft:movement.amphibious'] = {}
        root['minecraft:underwater_movement'] = {
            'value': properties['underwater_movement']
        }
        root['minecraft:navigation.generic'] = {
            'avoid_damage_blocks': True,
            'avoid_portals': True,
            'can_breach': properties['can_breach'],
            'can_jump': properties['can_jump'],
            'can_pass_doors': properties['can_pass_doors'],
            'can_sink': properties['can_sink'],
            'can_swim': True,
            'can_walk': True,
            'is_amphibious': True
        }
        root['minecraft:jump.static'] = {}
        root['minecraft:behavior.random_stroll'] = {
            'priority': 8,
            'interval': properties['stroll_interval']
        }
        root['minecraft:behavior.random_swim'] = {
            'priority': 7,
            'interval': properties['stroll_interval']
        }
        root['minecraft:breathable'] = {
            'breathes_air': True,
            'breathes_water': True,
            'generates_bubbles': properties['bubbles'],
            'suffocate_time': 1,
            'inhale_time': 3.0
        }
