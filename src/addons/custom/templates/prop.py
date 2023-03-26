from addons.custom.template import CustomEntityTemplate

template = CustomEntityTemplate(
    name='prop',
    components={
            "minecraft:type_family": {
                "family": [
                    "furniture"
                ]
            },
            "minecraft:pushable": {
                "is_pushable": False,
                "is_pushable_by_piston": False
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
                "value": 0
            },
            "minecraft:health": {
                "value": 10
            },
            "minecraft:collision_box": {
                "height": 1,
                "width": 1
            },
            "minecraft:is_stackable": {},
            "minecraft:physics": {}
    }
)