import module
import global_vars

# this physics system is really limited but also very simple, each object can only occupy integer positions
# mkovement is discrete and when collisions occur the energy is lost
class physics_module(module.module):
    def __init__(self):
        super().__init__()
        self.elapsed_time = 0

    def update(self, ts):
        ecs = global_vars.get_ecs()
        self.elapsed_time += ts

        # we use positions as keys so we can easily check whether or not there will be a collision
        # note that this does mean order matters, and order is not necessarily stable, so some funky behaviour can occur
        bodies = {}
        for e, body in ecs.view("static_body"):
            bodies[body.position] = (e, body)

        # energy is not conserved in this simplistic model
        for e, group in ecs.group("sprite_dynamic"):
            sprite, body = group
            new_pos = (body.position[0] + body.delta_position[0], body.position[1] + body.delta_position[1])
            body.delta_position = (0, 0)
            # run callbacks every second, implemented because you would insteantly die when hitting an enemy otherwise
            if new_pos in bodies and self.elapsed_time >= 1000:
                self.elapsed_time = 0
                other = bodies[new_pos]
                body.collision_callback(e, other[0])
                other[1].collision_callback(other[0], e)
            else:
                body.position = new_pos
                sprite.position = new_pos
                bodies[new_pos] = (e, body)

def create_module():
    mod = physics_module()
    return mod
