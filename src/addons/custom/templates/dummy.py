from addons.custom.template import CustomEntityTemplate

template = CustomEntityTemplate(
    name='dummy',
    components={
        "minecraft:type_family": {
            "family": [
                "dummy"
            ]
        },
        "minecraft:collision_box": {
            "height": 0.001,
            "width": 0.001
        },
        "minecraft:physics": {},
        "minecraft:tick_world": {
            "never_despawn": True,
            "radius": 2
        }
    }
)