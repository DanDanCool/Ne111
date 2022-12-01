import module
import pygame
import global_vars

# use pygame for mouse and keyboard events
class input_module(module.module):
    def __init__(self):
        super().__init__()

    def update(self, ts):
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                global_vars.get_engine().should_run(False)
            if e.type == pygame.VIDEORESIZE:
                # TODO: resize renderer viewport
                pass


def create_module():
    mod = input_module()
    return mod
