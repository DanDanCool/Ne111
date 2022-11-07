import render_graph
class sprite_render(render_graph.render_node):
    def __init__(self, name):
        pass

    def

class game:
    def __init__(self):
        self.should_run = True;
        self.input
        self.renderer
        self.render_graph
        self.component_system
        self.timestep = 0

        # TODO: iterate through src/modules and add each module
        self.modules = []

    def run(self):
        return self.should_run

    def update(self, ts):
        self.timesetp = 0
        self.input.update()

        # update various game subsystems here....
        for m in self.modules:
            m.update(ts)

        self.renderer.render()
