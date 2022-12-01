import module
import toml
import pygame
import numpy
import moderngl

# note to self: in future implementations, inputs, outputs, and transients should be defined in one function through
# function calls to some builder like Unity's implementation. Allows for much faster graph builds as well as nicer API?
# probably also a good idea to separate the render function and the registration functions for better modularity
def _root_pass(graph, pass_data):
    graph.clear_global_buffers()

class _graph_node:
    def __init__(self, name, render_fn):
        self.name = name
        self.render_func = render_fn
        self.pass_data = {}
        self.parents = []
        self.children = []

    def add_parent(self, node):
        self.parents.append(node)

    def add_child(self, node):
        self.children.append(node)

class _graph:
    def __init__(self):
        self.root = None
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.name] = node

    def get_node(self, name):
        return self.nodes[name]

    # for now we only use render_nodes to build the graph because I am running out of time
    def build(self):
        return # graph should already be built
        unlinked_inputs = {}
        unlinked_outputs = {}

        for name, node in self.unlinked_nodes:
            render_node = node.node
            for i in render_node.inputs():
                if i.resource_type == render_data.RENDER_NODE:
                    self.unlinked_nodes[i.name].add_child(node)
                    node.add_parent(self.unlinked_nodes[i.name])
                else:
                    if i.name in unlinked_inputs:
                        unlinked_inputs[i.name].append(node)
                    else:
                        unlinked_inputs[i.name] = [node]

            for o in render_node.outputs():
                for i in unlinked_inputs[o.name]:
                    pass

    def traverse(self):
        passes = []
        nodes = [self.root]
        for n in nodes:
            passes.append(n)
            nodes.extend(n.children)

        return passes

class builder:
    def __init__(self, graph, node):
        self.render_graph = graph
        self.node = node

    def add_dependency(self, name):
        parent = self.render_graph.graph.get_node(name)
        self.node.add_parent(parent)
        parent.add_child(self.node)

    def create_buffer(self, buf_type, size):
        return self.render_graph.create_buffer(buf_type, size)

    def create_uniform(self, name, utype, value):
        return self.render_graph.create_uniform(name, utype, value)

class render_graph:
    def __init__(self, renderer):
        self.renderer = renderer
        self.graph = _graph()

        _, builder = self.add_pass("root", _root_pass)
        self.graph.root = builder.node

    def clear_global_buffers(self):
        self.renderer.clear_global_buffers()

    def add_pass(self, name, render_fn):
        node = _graph_node(name, render_fn)
        self.graph.add_node(node)
        return node.pass_data, builder(self, node)

    def execute(self):
        self.graph.build()
        passes = self.graph.traverse()
        for p in passes:
            p.render_func(self, p.pass_data)

    def create_buffer(self, buf_type, size):
        return self.renderer.create_buffer(buf_type, size)

    def create_uniform(self, name, utype, value):
        return _uniform(name, utype, value)

    def buffer_data(self, buf, buf_type, data, size):
        self.renderer.buffer_data(buf, buf_type, data, size)

    def get_pipeline(self, name):
        return self.renderer.get_pipeline(name)

    def submit(self, pipeline, vb, ib, uniforms, count):
        self.renderer.submit(pipeline, vb, ib, uniforms, count)

    def get_hwinfo(self):
        return renderer.get_hwinfo()

class _pipeline:
    def __init__(self):
        self.program = 0
        self.layout = []

class _uniform:
    def __init__(self, name, utype, value):
        self.name = name
        self.utype = utype
        self.value = value

class render_module(module.module):
    g_module = None
    def __init__(self):
        super().__init__()
        g_module = self
        pygame.init()
        pygame.display.set_mode((1280, 720), pygame.OPENGL | pygame.DOUBLEBUF, vsync = 1)
        self.glcontext = moderngl.create_context()
        self.glcontext.enable(moderngl.BLEND)
        self.glcontext.blend_func = self.glcontext.SRC_ALPHA, self.glcontext.ONE_MINUS_SRC_ALPHA
        self.glcontext.viewport = (0, 0, 1280, 720)

        self.render_graph = render_graph(self)
        self.pipelines = {}

    # pygame cleanup here
    def __del__(self):
        # on second thought: I am too lazy to do this
        pygame.quit()

    def create_shader(self, name):
        fbytes = None
        with open(name) as f:
            fbytes = f.read()
        return fbytes

    def viewport(self, x, y):
        pass

    def clear_global_buffers(self):
        self.glcontext.clear(0.8, 0.2, 0.4, 1.0)

    def vsync(self, sync):
        pass

    def update(self, ts):
        pygame.event.pump()
        self.glcontext.screen.use()
        self.render_graph.execute()
        pygame.display.flip()

    def get_render_graph(self):
        return self.render_graph

    def create_buffer(self, buf_type, size):
        return self.glcontext.buffer(None, reserve=size, dynamic=True)

    def load_pipeline(self, name):
        data = None
        with open("../assets/" + name + ".toml") as f:
            data = toml.load(f)
        return data

    def create_pipeline(self, name):
        pipeline_info = self.load_pipeline(name)
        pipeline = _pipeline()

        vs = self.create_shader("../assets/" + pipeline_info["vertex_shader"] + ".glsl")
        fs = self.create_shader("../assets/" + pipeline_info["fragment_shader"] + ".glsl")

        pipeline.program = self.glcontext.program(vertex_shader = vs, fragment_shader = fs)
        pipeline.layout = pipeline_info["layout"]

        self.pipelines[name] = pipeline
        return pipeline

    def get_pipeline(self, name):
        if name in self.pipelines:
            return self.pipelines[name]
        else:
            return self.create_pipeline(name)

    def bind_pipeline(self, pipeline, buffer):
        #stride = 0
        #for attribute in pipeline.layout:
        #    stride += 4 * attribute["count"] # this is hardcoded to assume 4 bytes

        #offset = 0
        #for i in range(len(pipeline.layout)):
        #    attribute = pipeline.layout[i]
        #    gltype = 0
        #    if attribute["type"] == "float":
        #        gltype = GL_FLOAT

        #    glEnableVertexAttribArray(i)
        #    glVertexAttribPointer(0, 2, gltype, 0, stride, offset)
        #    offset += 4 * attribute["count"]
        attrformat = ""
        for attribute in pipeline.layout.values():
            count = attribute["count"]
            attrformat += str(count)
            if attribute["type"] == "float":
                attrformat += "f"
            attrformat += " "

        attrformat = str.strip(attrformat)

        args = [buffer, attrformat]
        args.extend([k for k in pipeline.layout.keys()])
        return args

    def bind_uniforms(self, pipeline, uniforms):
        for u in uniforms:
            pipeline.program[u.name] = u.value
            #location = glGetUniformLocation(pipeline.program, u.name)
            #if u.type == "mat4fv":
            #    glUniformMatrix4fv(location, 1, 0, u.value)

    def buffer_data(self, buf, buf_type, data, size):
        # extremely bad
        #if buf_type == "vertex":
        #    glBindBuffer(GL_ARRAY_BUFFER, buf)
        #    glBufferSubData(GL_ARRAY_BUFFER, 0, size, data)
        #    glBindBuffer(GL_ARRAY_BUFFER, 0)
        #if buf_type == "index":
        #    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buf)
        #    glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, size, data)
        #    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        pass

    # time running out, hard coding, etc, etc....
    def submit(self, pipeline, vb, ib, uniforms, count):
        #glBindVertexArray(pipeline.va)
        #glBindBuffer(GL_ARRAY_BUFFER, vb)
        #bind_pipeline(pipeline)
        self.bind_uniforms(pipeline, uniforms)
        attrformat = self.bind_pipeline(pipeline, vb)

        # this is probably really inefficient, but this silly library is very inflexible
        # this creates a vertex array object that also does rendering for some reason?
        # in low-level opengl you can bind a vertex array object and then bind the vertex and index buffers to tell the
        # GPU what to render, but the constructor necessitates taking in a fixed vertex buffer and index buffer
        #va = self.glcontext.vertex_array(pipeline.program, [ attrformat ], index_buffer = ib)
        va = self.glcontext.vertex_array(pipeline.program, [ (vb, "2f 4f", "a_pos", "a_color") ], index_buffer = ib)
        va.render(moderngl.TRIANGLES, count)

    def get_hwinfo(self):
        pass

def create_module():
    m = render_module()
    return m
