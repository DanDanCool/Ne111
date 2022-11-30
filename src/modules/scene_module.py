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

    def load_file(self, name):
        data = None
        with open("../assets/" + name) as f:
            data = tomllib.load(f)

        return data

    # this is unfortunately hard coded
    # perhaps specifying the entire component body should be mandated so it can be directly passed into the constructor?
    def create_entity(self, blueprint):
        ecs = game.get_ecs()
        entity = ecs.entity(ecs.entity_create(), ecs)
        components = blueprint["components"]

        if "script_component" in components:
            script_component = game.components.script_component()
            for script in components["script_component"]:
                script_object = getattr(game.components, script)
                script_component.add_script(script_object)
            entity.add("script_component", script_component)

        if "dynamic_body" in components:
            dynamic_body = game.components.dynamic_body()
            callback = getattr(game.components, components["dynamic_body"]["collision_callback"])
            dynamic_body.collision_callback = callback
            entity.add("dynamic_body", dynamic_body)

        if "static_body" in components:
            static_body = game.components.static_body()
            callback = getattr(game.components, components["static_body"]["collision_callback"])
            static_body.collision_callback = callback
            entity.add("static_body", static_body)

        if "sprite_component" in components:
            sprite_component = game.components.sprite_component()
            color = components["sprite_component"]["color"]
            sprite_component.color = color
            entity.add("sprite_component", sprite_component)

    # we do scene loading here to guarantee that all modules are loaded
    def update(ts):
        if self.scene_loaded:
            return

        scene = load_file("init.toml")

        for e in scene[entities]:
            blueprint = load_file(e + ".toml")
            create_entity(blueprint)

        self.scene_loaded = True
