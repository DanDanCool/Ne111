import time
import importlib
import pathlib

class game:
    def __init__(self):
        g_game = self
        self.b_run = True;
        self.component_system

        self.lib = []
        self.modules = []

        path = pathlib.Path('modules')
        for p in path.iterdir():
            m = importlib.import_module(p.name)
            self.lib.append(m)
            self.modules.append(m.create_module())

    def reload(self):
        for m in self.lib :
            importlib.reload(m)

    def run(self):
        last_time = time.perf_counter_ns()
        while (self.b_run):
            time = time.perf_counter_ns()
            dt = time - last_time

            for m in self.modules:
                m.update(ts)

    def should_run(self, run):
        self.b_run = run

    def get_ecs(self):
        return self.component_system

def get_game():
    return game.g_game

def get_ecs():
    return game.g_game.get_ecs()
