import module
import toml
import global_vars
import game.components
import game.scripts
import game.render_nodes
import ecs
from . import render_module

class scene_module(module.module):
    def __init__(self):
        self.scene_loaded = False

        # register ECS components here because I have no better place to put it
        ecs = global_vars.get_ecs()
        ecs.register("sprite_component", game.components.sprite_component)
        ecs.register("script_component", game.components.script_component)
        ecs.register("dynamic_body", game.components.dynamic_body)
        ecs.register("static_body", game.components.static_body)

        ecs.group_create("sprite_dynamic", game.components.sprite_dynamic)
        ecs.group_create("sprite_static", game.components.sprite_static)

        graph = global_vars.get_module("render_module").get_render_graph()
        pass_data, builder = graph.add_pass("sprite", game.render_nodes.sprite_pass)
        builder.add_dependency("root")

        # 6 floats per vertex * 4 vertices * 4 bytes * 100 thousand quads
        pass_data["vertex_buffer"] = builder.create_buffer("vertex", 6 * 4 * 4 * 100000)

        # 6 vertices per quad (two triangles) * 4 bytes * 100 thousand quads
        pass_data["index_buffer"] = builder.create_buffer("index", 6 * 4 * 100000)

        pass_data["projection"] = builder.create_uniform("u_proj", "mat4fv", 0)

    def load_file(self, name):
        data = None
        with open("../assets/" + name + ".toml") as f:
            data = toml.load(f)
        return data

    # this is unfortunately hard coded
    # perhaps specifying the entire component body should be mandated so it can be directly passed into the constructor?
    def create_entity(self, blueprint):
        cs = global_vars.get_ecs()
        entity = ecs.entity(cs.entity_create(), cs)
        components = blueprint["components"]

        if "script_component" in components:
            script_component = game.components.script_component()
            for script in components["script_component"]:
                script_object = getattr(game.scripts, script)
                script_component.add_script(script_object())
            entity.add("script_component", script_component)

        if "dynamic_body" in components:
            dynamic_body = game.components.dynamic_body()
            callback = getattr(game.scripts, components["dynamic_body"]["collision_callback"])
            dynamic_body.collision_callback = callback
            entity.add("dynamic_body", dynamic_body)

        if "static_body" in components:
            static_body = game.components.static_body()
            callback = getattr(game.scripts, components["static_body"]["collision_callback"])
            static_body.collision_callback = callback
            entity.add("static_body", static_body)

        if "sprite_component" in components:
            sprite_component = game.components.sprite_component()
            color = components["sprite_component"]["color"]
            sprite_component.color = color
            entity.add("sprite_component", sprite_component)

    # we do scene loading here to guarantee that all modules are loaded
    def update(self, ts):
        if self.scene_loaded:
            return

        scene = self.load_file("init")

        for e in scene["entities"]:
            blueprint = self.load_file(e)
            self.create_entity(blueprint)

        cs = global_vars.get_ecs()
        for i in range(10):
            for j in range(10):
                e = ecs.entity(cs.entity_create(), cs)
                sprite = game.components.sprite_component()
                sprite.position = [-i - 1, -j - 1]
                sprite.color = [i / 10, i / 10, 1, 1]
                e.add("sprite_component", sprite)

        self.scene_loaded = True

def create_module():
    mod = scene_module()
    return mod
