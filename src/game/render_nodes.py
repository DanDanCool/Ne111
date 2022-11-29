from modules.render_module import *
import game
import numpy

class sprite_node(render_node):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, graph, in_params, out_params):
        QUAD_VERTICES = [ [ -0.5, -0.5 ],
                          [ +0.5, -0.5 ],
                          [ +0.5, +0.5 ],
                          [ -0.5, +0.5 ] ]

        TEX_COORDS = [ [ 0.0, 0.0 ], [ 1.0, 0.0 ], [ 1.0, 1.0 ], [ 0.0, 1.0 ] ]

        ecs = game.get_ecs()
        hwinfo = graph.get_hwinfo()
        vertex_buffer = numpy.array()
        index_buffer = []
        offset = 0
        for _, components in ecs.group("sprite_physics"):
            sprite, physics = components
            for i in range(4):
                vertex_buffer.extend(QUAD_VERTICES[i])
                vertex_buffer.extend(sprite.color)

            index_buffer.extend([offset + 0, offset + 1, offset + 2, offset + 2, offset + 3, offset + 0])
            offset += 4

        vertex32f = numpy.array(vertex_buffer, numpy.float)
        index32i = numpy.array(index_buffer, numpy.uint32)

        # synchronous buffer upload, would be interesting to come up with more parallel method
        graph.buffer_data(in_params["vb"], vertex32f, vertex32f.size)
        graph.buffer_data(in_params["ib"], index32i, index32i.size)

        # pipeline is also hardcoded to save on time
        graph.submit(in_params["pipeline"], in_params["vb"], in_params["ib"], index32i.size)

    def inputs(self):
        desc = [ render_data("root", render_data.RENDER_NODE, render_data.READ_WRITE) ]
        return desc

    def transients(self):
        # in the interset of saving time we hardcode these buffers to be pretty massive
        desc = [ render_data("vb", render_data.BUFFER, render_data.WRITE),
                render_data("ib", render_data.BUFFER, render_data.WRITE),
                render_data("pipeline"), render_data.PIPELINE, render_data.READ]
        return desc

