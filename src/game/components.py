class group_component:
    def __init__(self, desc):
        pass

    def pools(self):
        pass

    def components(self):
        return ()

class sprite_component:
    def __init__(self):
        self.mesh_id = "square"
        self.texture_id = 0
        self.pipeline_id = 0
        self.color = [ 1, 1, 1, 1 ]

class script_component:
    def __init__(self):
        self.scripts = []

    def add_script(self, script):
        self.scripts.append(script)

    def update(self, entity, ts):
        for script in self.scripts:
            script.update(entity, ts)

class physics_component:
    def __init__(self):
        self.type = None
        self.position = [ 0, 0 ]

class sprite_physics_group(group_component):
    def __init__(self, desc):
        super().__init__(desc)
        self.sprite = desc["sprite_component"]
        self.physics = desc["physics_component"]

    # seems hardcoded but we would probably want to take the unique hash of the class instead
    def pools(self):
        return [ "sprite_component", "physics_component" ]

    def components(self):
        return (self.sprite, self.physics)
