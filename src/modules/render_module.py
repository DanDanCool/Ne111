import module
import pygame
import numpy
from OpenGL.GL import *
from OpenGL.GLU import *

class render_data:
    def __init__(self, name, res, access):
        RENDER_NODE = 0
        NAMED_RESOURCE = 1
        BUFFER = 3
        PIPELINE = 4

        READ = 0
        WRITE = 1
        READ_WRITE = 2

        self.name = name
        self.resource_type = res
        self.access = access

# note to self: in future implementations, inputs, outputs, and transients should be defined in one function through
# function calls to some builder like Unity's implementation. Allows for much faster graph builds as well as nicer API?
# probably also a good idea to separate the render function and the registration functions for better modularity
class render_node:
    def __init__(self, name):
        self.name = name

    def execute(self, graph, in_params, out_params):
        pass

    def inputs(self):
        desc = []
        return desc

    def outputs(self):
        desc = []
        return desc

    def transients(self):
        desc = []
        return desc

class _root_node(render_node):
    def __init__(self):
        super().__init__("root")

    def execute(self, graph, in_params, out_params):
        graph.clear_backbuffer()

    def outputs(self):
        desc = [ render_data("GLOBAL_BACKBUFFER", render_data.NAMED_RESOURCE, render_data.WRITE) ]
        return desc

class _graph_node:
    def __init__(self, node):
        self.node = node
        self.parents = []
        self.children = []

    def add_parent(self, node):
        self.parents.append(node)

    def add_child(self, node):
        self.children.append(node)

class _graph:
    def __init__(self):
        self.root = _graph_node(None, _root_node())

        self.unlinked_nodes = {}

    def add_node(self, render_node):
        self.unlinked_nodes[render_node.name] = _graph_node(render_node)

    # for now we only use render_nodes to build the graph because I am running out of time
    def build(self):
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
            order.append(n.node)
            nodes.extend(n.children)

        return passes

class render_graph:
    def __init__(self):
        self.renderer = None
        self.graph = _graph()
        add_node(_leaf_node())

    def clear(self):
        self.renderer.clear()

    def add_node(self, node):
        self.graph.add_node(node)

    def execute(self, renderer):
        self.renderer = renderer
        self.graph.build()
        passes = self.graph.traverse()
        for p in passes:
            in_params = {}
            out_params = {}

            # SUPER BAD, but whatever....
            resources = p.transients()
            for r in resources:
                if r.resource_type == render_data.BUFFER:
                    in_params[r.name] = self.renderer.get_buffer(r.name)
                if r.resource_type == render_data.PIPELINE:
                    in_params[r.name] = self.renderer.get_pipeline()
            p.execute(self, in_params, out_params)

    def buffer_data(self, buf, data, size):
        self.renderer.buffer_data(buf, data, size)

    def submit(self, pipeline, vb, ib, count):
        self.renderer.submit(pipeline, vb, ib, count)

    def get_hwinfo(self):
        return renderer.get_hwinfo()

class _pipeline:
    def __init__(self):
        self.program = 0
        self.va = 0

class render_module(module.module):
    def __init__(self):
        super.__init__()
        g_module = self
        pygame.init()
        pygame.display.set_mode((640, 480), pygame.OPENGL | pygame.DOUBLEBUF, vsync = 1)
        self.render_graph = render_graph()

        # PLEASE DON'T HARD CODE... reminder #564
        self.vertex_buffer = 0
        self.index_buffer = 0
        self.pipeline = _pipeline()

        glCreateBuffers(1, [self.vertex_buffer])
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, 6 * 4 * 100000, None, GL_DYNAMIC_DRAW)

        glCreateBuffers(1, [self.index_buffer])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 6 * 6 * 100000, None, GL_DYNAMIC_DRAW)

        glCreateVertexArrays(1, [self.pipeline.va])
        glBindVertexArray(self.pipeline.va)
        self.pipeline.program = glCreateProgram()

        vs = create_shader("../assets/sprite_vert.glsl", GL_VERTEX_SHADER)
        fs = create_shader("../assets/sprite_frag.glsl", GL_FRAGMENT_SHADER)

        glAttachShader(self.pipeline.program, vs)
        glAttachShader(self.pipeline.program, fs)
        glLinkProgram(self.pipeline.program)

        glDetachShader(self.pipeline.program, vs)
        glDetachShader(self.pipeline.program, fs)

        glDeleteShader(vs)
        glDeleteShader(fs)

    # pygame cleanup here
    def __del__(self):
        # on second thought: I am too lazy to do this
        pass

    def create_shader(self, name, usage):
        shader = glCreateShader(usage)
        fbytes = None

        with open(name) as f:
            fbytes = f.read()

        glShaderSource(shader, 1, fbytes, None)
        glCompileShader(shader)
        return shader

    def viewport(self, x, y):
        pass

    def clear(self):
        glClearColor(0.1, 0.4, 0.8, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def vsync(self, sync):
        pass

    def render(self, graph):
        graph.execute(self)
        pygame.display.flip()

    def update(self, ts):
        pygame.event.pump()
        self.render_graph.execute(self)

    def get_render_graph(self):
        return self.render_graph

    def get_pipeline(self):
        return self.pipeline

    def get_buffer(self, name):
        if name == "vb":
            return self.vb
        if name == "ib":
            return self.ib

    def buffer_data(self, buf, data, size):
        # extremely bad
        if data.dtype == float:
            glBindBuffer(GL_ARRAY_BUFFER, buf)
            glBufferSubData(GL_ARRAY_BUFFER, 0, size, data)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        if data.dtype == numpy.uint32:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buf)
            glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, size, data)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    # time running out, hard coding, etc, etc....
    def submit(self, pipeline, vb, ib, count):
        proj = glOrtho(-16, 16, -8, 8, -1, 1)

        glBindVertexArray(pipeline.va)
        glBindBuffer(GL_ARRAY_BUFFER, vb)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, 0, 6 * 4, 0)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(0, 4, GL_FLOAT, 0, 6 * 4, 2 * 4)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)
        glUseProgram(pipeline.program)

        location = glGetUniformLocation(pipeline.program, "u_proj")
        glUniformMatrix4fv(location, 1, 0, proj)

        glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, 0)

    def get_hwinfo(self):
        pass

def get_module():
    return render_module.g_module

def create_module():
    m = render_module()
    return m
