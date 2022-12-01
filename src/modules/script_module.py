import module
import engine

class script_module(module.module):
    def __init__(self):
        super().__init__()

    def update(self, ts):
        ecs = engine.get_ecs()

        for entity, script in ecs.view("script_component"):
            script.update(entity, ts)

def create_module():
    mod = script_module()
    return mod
