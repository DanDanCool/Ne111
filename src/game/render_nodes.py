from modules.render_module import *
from OpenGL.GLU import *
import game
import numpy

def sprite_pass(graph, pass_data):
        QUAD_VERTICES = [ [ -0.5, -0.5 ],
                          [ +0.5, -0.5 ],
                          [ +0.5, +0.5 ],
                          [ -0.5, +0.5 ] ]

        TEX_COORDS = [ [ 0.0, 0.0 ], [ 1.0, 0.0 ], [ 1.0, 1.0 ], [ 0.0, 1.0 ] ]

        ecs = game.get_ecs()
        vertex_buffer = []
        index_buffer = []
        offset = 0
        for _, sprite in ecs.view("sprite_component"):
            for i in range(4):
                vertex_buffer.extend(QUAD_VERTICES[i])
                vertex_buffer.extend(sprite.color)

            index_buffer.extend([offset + 0, offset + 1, offset + 2, offset + 2, offset + 3, offset + 0])
            offset += 4

        vertex32f = numpy.array(vertex_buffer, numpy.float)
        index32i = numpy.array(index_buffer, numpy.uint32)

        # synchronous buffer upload, would be interesting to come up with more parallel method
        graph.buffer_data(pass_data["vertex_buffer"], "vertex", vertex32f, vertex32f.size)
        graph.buffer_data(pass_data["index_buffer"], "index", index32i, index32i.size)

        projection = pass_data["projection"]
        projection.value = glOrtho(-16, 16, -8, 8, -1, 1)

        # pipeline is also hardcoded to save on time
        graph.submit(graph.get_pipeline("sprite_pipeline"), pass_data["vertex_buffer"], pass_data["index_buffer"],
                     [projection], index32i.size)
