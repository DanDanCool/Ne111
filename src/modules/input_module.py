import module
import pygame
import game

# use pygame for mouse and keyboard events
class input_module(module.module):
    def __init__(self):
        super().__init__()
        g_module = self

    def update(ts):
        events = pygame.event.get()
        for e in events:
            if e.type() == pygame.event.QUIT:
                game.get_game().should_run(False)
            if e.type() == pygame.event.VIDEORESIZE:
                # TODO: resize renderer viewport
                pass


def create_module():
    mod = input_module()
    return mod
