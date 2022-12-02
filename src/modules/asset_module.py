import module

# note: I was going to implement this but the functionality kind of got shoved into the scene module
# also there performance was not a bad enough to warrant such a solution
class texture_resource:
    def __init__(self):
        pass

class mesh_resource:
    def __init__(self):
        pass

class pipeline_resource:
    def __init__(self):
        pass

class sound_resource:
    def __init__(self):
        pass

class atlas_resource:
    def __init__(self):
        pass

class asset_module(module.module):
    def __init__(self):
        pass

    def load_mesh(self, name):
        pass

    def load_texture(self, name):
        pass

    def texture_atlas(self, ids):
        pass

    def load_pipeline(self, name):
        pass

    def load_sound(self, name):
        pass

    def get_texture(self, name):
        pass

    def get_atlas(self, name):
        pass

    def get_pipeline(self, name):
        pass

    def get_sound(self, name):
        pass

def create_module():
    mod = asset_module()
    return mod
