class render_node:
    def __init__(self, name):
        self.name = name

    def execute(self, graph, in_params, out_params):
        pass

    def in_desc(self):
        in_desc = {}
        return in_desc

    def out_desc(self):
        out_desc = {}
        return out_desc


class render_graph:
    def __init__(self):
        self.nodes = {}
        self.renderer = None

    def add_node(self, node):
        self.nodes[node.name] = node

    def build(self):
        pass

    def execute(self, renderer):
        self.renderer = renderer

    def get_texture(self, name):
        pass

    def get_buffer(self):
        pass

    def get_pipeline(self, name):
        pass
