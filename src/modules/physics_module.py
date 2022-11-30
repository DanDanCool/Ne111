import module
import game

# this physics system is really limited but also very simple, each object can only occupy integer positions
# mkovement is discrete and when collisions occur the energy is lost
class physics_module(module):
    def __init__(self):
        super().__init__()

    def update(self, ts):
        ecs = game.get_ecs()

        bodies = {}
        for e, body in ecs.view("static_body"):
            bodies[body.position] = (e, body)

        # energy is not conserved in this simplistic model
        for e, group in ecs.group("sprite_dynamic"):
            sprite, body = group
            new_pos = (body.position[0] + body.delta_position[0], body.position[1] + body.delta_position[1])
            body.delta_position = (0, 0)
            if new_pos in bodies:
                other = bodies[new_pos]
                body.collision_callback(e, other[0])
                other[1].collision_callback(other[0], e)
            else:
                body.position = new_pos
                sprite.position = new_pos
                bodies[new_pos] = (e, body)
