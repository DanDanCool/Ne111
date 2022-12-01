# script super class, all scripts inherit from this
#import level_generation
import global_vars
import random
import pygame

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
        x = random.randint(-1,1)
        y = random.randint(-1,1)
        dynamicbody = entity.get('dynamic_body')
        dynamicbody.delta_position = [x,y]

def attack_callback(self, other):
    # TODO: attack the other enemy here
    if not other.has("stats_component"):
        return
    self_stat = self.get("stats_component")
    other_stat = other.get("stats_component")
    other_stat.health -= self_stat.attack

def check_health_callback(self,other):
    self_stat = self.get("stats_component")
    if self_stat.health <= 0:
        print("You Lose")
        global_vars.get_engine().should_run(False)

def empty_callback(self,other):
    pass

class player_move_script(script):
    def __init__(self):
        super().__init__()

    def update(self, entity, ts):
        pressed_keys = pygame.key.get_pressed()
        x = 0
        y = 0
        if pressed_keys [pygame.K_w]:
            y = 1
        if pressed_keys [pygame.K_s]:
            y = -1
        if pressed_keys [pygame.K_d]:
            x = 1
        if pressed_keys [pygame.K_a]:
            x = -1
        dynamicbody = entity.get('dynamic_body')
        dynamicbody.delta_position = [x,y]

