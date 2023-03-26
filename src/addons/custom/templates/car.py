from addons.custom.template import CustomEntityTemplate

template = CustomEntityTemplate(
    name='car',
    components={
        "minecraft:type_family": {
            "family": [
                "vehicle"
            ]
        },
        "minecraft:collision_box": {
            "height": 1.0,
            "width": 1.0
        },
        "minecraft:breathable": {
            "total_supply": 15,
            "suffocate_time": 0.0,
            "inhale_time": 0.0,
            "breathes_air": True,
            "breathes_water": False,
            "breathes_lava": False,
            "breathes_solids": False,
            "generates_bubbles": True
        },
        "minecraft:scale": {
            "value": 1.0
        },
        "minecraft:health": {
            "value": 10,
            "max": 10
        },
        "minecraft:damage_sensor": {
            "triggers": [
                {
                    "cause": "all",
                    "deals_damage": False
                }
            ]
        },
        "minecraft:movement": {
            "value": 0.25,
            "max": 0.25
        },
        "minecraft:navigation.generic": {},
        "minecraft:movement.basic": {
            "max_turn": 30
        },
        "minecraft:rideable": {
            "seat_count": 1,
            "family_types": [
                "player"
            ],
            "interact_text": "text.interact.ride",
            "pull_in_entities": False,
            "crouching_skip_interact": False,
            "seats": [
                {
                    "position": [-0.0, 1.0, 0.0],
                    "min_rider_count": 0
                }
            ]
        },
        "minecraft:input_ground_controlled": {},
        "minecraft:physics": {
            "has_collision": True,
            "has_gravity": True
        }
    }
)