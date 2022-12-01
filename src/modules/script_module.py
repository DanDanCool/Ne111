import module
import global_vars

class script_module(module.module):
    def __init__(self):
        super().__init__()
        self.elapsed_time = 0.0

    def update(self, ts):
        ecs = global_vars.get_ecs()
        self.elapsed_time += ts

        if self.elapsed_time < 1000.0:
            return
        else:
            self.elapsed_time = 0

        for entity, script in ecs.view("script_component"):
            script.update(entity, ts)

def create_module():
    mod = script_module()
    return mod
