import module
import tomllib
import pygame
import numpy
from OpenGL.GL import *

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
        self.nodes[render_node.name] = node

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
            order.append(n)
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

class render_graph:
    def __init__(self, renderer):
        self.renderer = renderer
        self.graph = _graph()

        _, builder = add_pass("root", _root_pass)
        self.graph.root = builder.node

    def clear_global_buffers(self):
        self.renderer.clear_global_buffers()

    def add_pass(self, name, render_fn):
        node = _graph_node(name, render_fn)
        self.graph.add_node(node)
        return node.pass_data, builder(self.graph, node)

    def add_node(self, node):
        self.graph.add_node(node)

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
        self.va = 0
        self.layout = []

class _uniform:
    def __init__(self, name, utype, value):
        self.name = name
        self.utype = utype
        self.value = value

class render_module(module.module):
    def __init__(self):
        super.__init__()
        g_module = self
        pygame.init()
        pygame.display.set_mode((640, 480), pygame.OPENGL | pygame.DOUBLEBUF, vsync = 1)
        self.render_graph = render_graph()

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
        graph.execute()
        pygame.display.flip()

    def update(self, ts):
        pygame.event.pump()
        self.render_graph.execute(self)

    def get_render_graph(self):
        return self.render_graph

    def create_buffer(self, buf_type, size):
        if buf_type == "vertex":
            buffer = 0
            glCreateBuffers(1, [buffer])
            glBindBuffer(GL_ARRAY_BUFFER, buffer)
            glBufferData(GL_ARRAY_BUFFER, size, None, GL_DYNAMIC_DRAW)
            return buffer

        if buf_type == "index":
            buffer = 0
            glCreateBuffers(1, [buffer])
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, size, None, GL_DYNAMIC_DRAW)
            return buffer

    def get_pipeline(self, name):
        if name in self.pipelines:
            return self.pipelines[name]
        else:
            return create_pipeline(name)

    def load_pipeline(self, name):
        data = None
        with open("../assets/" + name + ".toml") as f:
            data = tomllib.load(f)
        return data

    def create_pipeline(self, name):
        pipeline_info = load_pipeline(name)
        pipeline = _pipeline()

        glCreateVertexArrays(1, [pipeline.va])
        glBindVertexArray(pipeline.va)
        pipeline.layout = pipeline_info["layout"]

        self.pipeline.program = glCreateProgram()

        vs = create_shader("../assets/" + pipeline_info["vertex_shader"] + ".glsl", GL_VERTEX_SHADER)
        fs = create_shader("../assets/" + pipeline_info["fragment_shader"] + ".glsl", GL_FRAGMENT_SHADER)

        glAttachShader(pipeline.program, vs)
        glAttachShader(pipeline.program, fs)
        glLinkProgram(pipeline.program)

        glDetachShader(pipeline.program, vs)
        glDetachShader(pipeline.program, fs)

        glDeleteShader(vs)
        glDeleteShader(fs)

        self.pipelines[name] = pipeline

    def bind_pipeline(self, pipeline):
        stride = 0
        for attribute in pipeline.layout:
            stride += 4 * attribute["count"] # this is hardcoded to assume 4 bytes

        offset = 0
        for i in range(len(pipeline.layout)):
            attribute = pipeline.layout[i]
            gltype = 0
            if attribute["type"] == "float":
                gltype = GL_FLOAT

            glEnableVertexAttribArray(i)
            glVertexAttribPointer(0, 2, gltype, 0, stride, offset)
            offset += 4 * attribute["count"]

    def bind_uniforms(self, pipeline, uniforms):
        for u in uniforms:
            location = glGetUniformLocation(pipeline.program, u.name)
            if u.type == "mat4fv":
                glUniformMatrix4fv(location, 1, 0, u.value)

    def buffer_data(self, buf, buf_type, data, size):
        # extremely bad
        if buf_type == "vertex":
            glBindBuffer(GL_ARRAY_BUFFER, buf)
            glBufferSubData(GL_ARRAY_BUFFER, 0, size, data)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        if buf_type == "index":
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buf)
            glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, size, data)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    # time running out, hard coding, etc, etc....
    def submit(self, pipeline, vb, ib, uniforms, count):
        glBindVertexArray(pipeline.va)
        glBindBuffer(GL_ARRAY_BUFFER, vb)
        bind_pipeline(pipeline)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)
        glUseProgram(pipeline.program)

        bind_uniforms(pipeline, uniforms)

        glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, 0)

    def get_hwinfo(self):
        pass

def get_module():
    return render_module.g_module

def create_module():
    m = render_module()
    return m
