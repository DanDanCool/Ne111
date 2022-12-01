import time
import importlib
import pathlib
import ecs

class engine:
    def __init__(self):
        self.b_run = True;
        self.component_system = ecs.component_system()

        self.lib = []
        self.modules = {}

    def __del__(self):
        self.modules.clear()
        self.lib.clear()

    def load_modules(self):
        path = pathlib.Path('modules')
        for p in path.iterdir():
            if p.stem in [ "__init__", "__pycache__" ]:
                continue
            m = importlib.import_module('modules.' + p.stem)
            self.modules[p.stem] = m.create_module()
            self.lib.append(m)

    def get_module(self, name):
        return self.modules[name]

    def reload(self):
        for m in self.lib :
            importlib.reload(m)

    def run(self):
        last_time = time.perf_counter_ns()
        while (self.b_run):
            cur_time = time.perf_counter_ns()
            dt = (cur_time - last_time) / (10**6) # ms

            for _, m in self.modules.items():
                m.update(dt)

            last_time = cur_time

    def should_run(self, run):
        self.b_run = run

    def get_ecs(self):
        return self.component_system
