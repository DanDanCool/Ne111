import render_graph
class sprite_render(render_graph.render_node):
    def __init__(self, name):
        pass

class game:
    def __init__(self):
        self.brun = True;
        self.component_system

        # TODO: iterate through src/modules and add each module
        self.modules = []

    def run(self):
        return self.brun

    def update(self, ts):
        self.input.update()

        # update various game subsystems here....
        for m in self.modules:
            m.update(ts)
