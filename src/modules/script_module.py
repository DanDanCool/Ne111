import module
import game

class script_module(module.module):
    def __init__(self):
        super().__init__()

    def update(self, ts):
        ecs = game.get_ecs()

        for entity, script in ecs.view("script_component"):
            script.update(entity, ts)
