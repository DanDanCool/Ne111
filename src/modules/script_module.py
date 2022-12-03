import module
import global_vars

# responsible for the behavioural components in the ecs
class script_module(module.module):
    def __init__(self):
        super().__init__()
        self.elapsed_time = 0.0

    def update(self, ts):
        ecs = global_vars.get_ecs()
        self.elapsed_time += ts

        # only update scripts every second to simulate a turn-based environment because I am too lazy to actually
        # program this into the game
        # the engine was designed to be real-time, a game object would make turn-based updates elegant as it would not
        # have to be coded into the engine as some special case, as some things need to be updated frequently, like
        # input
        if self.elapsed_time < 250.0:
            return
        else:
            self.elapsed_time = 0

        for entity, script in ecs.view("script_component"):
            script.update(entity, ts)

def create_module():
    mod = script_module()
    return mod
