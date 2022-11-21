class sprite_component:
    def __init__(self):
        self.mesh_id = "square"
        self.texture_id = 0
        self.pipeline_id = 0
        self.position = [0, 0]

class script_component:
    def __init__(self):
        self.scipts = None # this is a linked list

class physics_component:
    pass
