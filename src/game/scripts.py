# script super class, all scripts inherit from this
#import level_generation
import global_vars

class script:
    def __init__(self):
        pass

    def update(self, entity, ts):
        pass

class level_script(script):
    def __init__(self):
        super().__init__()

    def update(self, entity, ts):
        pass
        #generator = level_generation.level_layout_generator()
        #room = generator.generate_layout()

        ## WALL_TILE
        ## EMPTY_TILE
        ## SPECIAL_TILE
        #for x in room:
        #    for y in x:
        #        if y == level_layout_generator.EMPTY_TILE:
        #            pass

class delete_script(script):
    def __init__(self):
        super().__init__()

    def update(self, entity, ts):
        ecs = global_vars.get_ecs()
        ecs.entity_destroy(entity.e_id)

class random_move_script(script):
    def __init__(self):
        super().__init__()

    def update(self, entity, ts):
        pass

def attack_callback(self, other):
    # TODO: attack the other enemy here
    pass
