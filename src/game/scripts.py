# script super class, all scripts inherit from this
import level_generation
import global_vars
import random
import pygame

class script:
    def __init__(self):
        pass

    def update(self, entity, ts):
        pass

# generate a level
class level_script(script):
    def __init__(self):
        super().__init__()

    def update(self, entity, ts):
        scene_module = global_vars.get_module("scene_module")
        generator = level_generation.level_layout_generator()
        room = generator.generate_layout()

        xpos = - generator.x_max / 2
        for col in room:
            ypos = 1 - generator.y_max / 2
            for tile in col:
                ypos += 1
                if tile == generator.EMPTY_TILE:
                    continue

                if tile in [generator.CORNER_WALL_TILE, generator.H_WALL_TILE, generator.V_WALL_TILE]:
                    bp = scene_module.load_file("wall")
                    e = scene_module.create_entity(bp)
                    body = e.get("static_body")
                    body.position = (xpos, ypos)
                    sprite = e.get("sprite_component")
                    sprite.position = body.position

                if tile == generator.SPAWN:
                    bp = scene_module.load_file("player")
                    e = scene_module.create_entity(bp)
                    body = e.get("dynamic_body")
                    body.position = (xpos, ypos)

                if tile == generator.ENEMY:
                    bp = scene_module.load_file("basic_enemy")
                    e = scene_module.create_entity(bp)
                    body = e.get("dynamic_body")
                    body.position = (xpos, ypos)

                if tile == generator.EXIT:
                    bp = scene_module.load_file("portal")
                    e = scene_module.create_entity(bp)
                    body = e.get("static_body")
                    body.position = (xpos, ypos)
                    sprite = e.get("sprite_component")
                    sprite.position = body.position

                if tile == generator.TREASURE:
                    bp = scene_module.load_file("treasure")
                    e = scene_module.create_entity(bp)
                    body = e.get("static_body")
                    body.position = (xpos, ypos)
                    sprite = e.get("sprite_component")
                    sprite.position = body.position


            xpos += 1

# delete an entity from the ecs
class delete_script(script):
    def __init__(self):
        super().__init__()

    def update(self, entity, ts):
        ecs = global_vars.get_ecs()
        ecs.entity_destroy(entity.e_id)

# enemy random movement
class random_move_script(script):
    def __init__(self):
        super().__init__()

    def update(self, entity, ts):
        if not entity.has("dynamic_body"):
            return
        x = random.randint(-1,1)
        y = random.randint(-1,1)
        dynamicbody = entity.get("dynamic_body")
        dynamicbody.delta_position = (x,y)

def attack_callback(self, other, ts):
    if not (self.has("stats_component") and other.has("stats_component")):
        return
    self_stat = self.get("stats_component")
    self_stat.elapsed_time += ts
    # delays attack so that player does not instantly die
    if self_stat.elapsed_time < 250.0:
        return
    self_stat.elapsed_time = 0.0

    other_stat = other.get("stats_component")
    other_stat.health -= self_stat.attack

# checks health of the player
def check_health_callback(self, other, ts):
    if not (self.has("stats_component")):
        return
    self_stat = self.get("stats_component")
    if self_stat.health <= 0:
        print("You Lose")
        global_vars.get_engine().should_run(False)

# current system expects there to be a callback for every physics component
# this function is provided so physics components do not require a callback
def empty_callback(self, other, ts):
    pass

# player movement with wasd
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
        dynamicbody.delta_position = (x,y)

# this callback generates a new level
def nextlevel_callback(self, other, ts):
    if not other.has("player_component"):
        return
    # when gerenating a new level we first destroy all entities
    ecs = global_vars.get_ecs()
    # saves player stats so that they carry over to next level
    stats_component = other.get("stats_component")
    ecs.clear()
    generator = level_script()
    generator.update(None,0)
    for e, player in ecs.view("player_component"):
        stats = e.get("stats_component")
        stats.health = stats_component.health

# adds +1 health when treasure is collected
def treasure_callback(self, other, ts):
    if not other.has("player_component"):
        return
    stats_component = other.get("stats_component")
    stats_component.health += 1
    print("health", stats_component.health)
    # destroy the entity to prevent infinite health
    ecs = global_vars.get_ecs()
    ecs.entity_destroy(self.e_id)