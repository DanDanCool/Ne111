# component base class
class component:
    def __init__(self):
        pass

    def component_callback(self, entity):
        pass

# component base class for registering groups
class group_component:
    def __init__(self, desc):
        pass

    def pools(self):
        pass

    def components(self):
        return ()

class sprite_component(component):
    def __init__(self):
        super().__init__()
        self.mesh_id = "square"
        self.texture_id = 0
        self.pipeline_id = 0
        self.color = [ 1, 1, 1, 1 ]
        self.position = [ 0, 0 ]

class script_component(component):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def add_script(self, script):
        self.scripts.append(script)

    def update(self, entity, ts):
        for script in self.scripts:
            script.update(entity, ts)

class stats_component(component):
    def __init__(self):
        self.health = 3
        self.attack = 1

# there is some data duplication here, but regularly the physics engine would update the data for the matrix transforms
# for simplicity we directly modify the sprite position
# collsion callback: function object that takes in two entity objects: this and other
class dynamic_body(component):
    def __init__(self):
        super().__init__()
        self.position = ( 0, 0 )
        self.delta_position = ( 0, 0 )
        self.collision_callback = None

class static_body(component):
    def __init__(self):
        super().__init__()
        self.position = ( 0, 0 )
        self.collision_callback = None

class sprite_dynamic(group_component):
    def __init__(self, desc):
        super().__init__(desc)
        self.sprite = desc["sprite_component"]
        self.physics = desc["dynamic_body"]

    # seems hardcoded but we would probably want to take the unique hash of the class instead
    def pools():
        return [ "sprite_component", "dynamic_body" ]

    def components(self):
        return (self.sprite, self.physics)

class sprite_static(group_component):
    def __init__(self, desc):
        super().__init__(desc)
        self.sprite = desc["sprite_component"]
        self.physics = desc["static_body"]

    # seems hardcoded but we would probably want to take the unique hash of the class instead
    def pools():
        return [ "sprite_component", "static_body" ]

    def components(self):
        return (self.sprite, self.physics)
