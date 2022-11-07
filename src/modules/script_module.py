class script_module(game_module):
    def __init__(self, game):
        super(self, game)
        self.scripts = []

    def update(self, ts):
        # go through all scirpt components here and update
