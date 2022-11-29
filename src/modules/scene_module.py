import module
import tomllib
import game
import game.components
import ecs

class scene_module(module):
    def __init__(self):
        self.scene_loaded = False

        # register ECS components here because I have no better place to put it
        ecs = game.get_ecs()
        ecs.register("sprite_component", game.components.sprite_component)
        ecs.register("physics_component", game.components.physics_component)
        ecs.register("script_component", game.components.script_component)
        ecs.register("dynamic_body", game.components.dynamic_body)
        ecs.register("static_body", game.components.static_body)

        ecs.group_create("sprite_dynamic", game.components.sprite_dynamic)
        ecs.group_create("sprite_static", game.components.sprite_static)

    # we do scene loading here to guarantee that all modules are loaded
    def update(ts):
        if self.scene_loaded:
            return

        scene = None
        with open("../assets/init.toml") as f:
            scene = tomllib.load(f)

        ecs = game.get_ecs()
        for e in scene[entities]:
            for c in e:
                if c["component"] == "script_component":
                    entity = ecs.entity(ecs.entity_create(), ecs)
                    script_component = game.components.script_component()
                    script_component.add_script(level_script())
                    script_component.add_script(delete_script())
                    entity.add("script_component", script_component)

        self.scene_loaded = True
