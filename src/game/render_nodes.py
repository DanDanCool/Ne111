from modules.render_module import *
import global_vars
import numpy

# creates an identity matrix multiplied by a scalar
def _scale(scale_factor):
    row0 = [1 * scale_factor, 0, 0, 0]
    row1 = [0, 1 * scale_factor, 0, 0]
    row2 = [0, 0, 1 * scale_factor, 0]
    row3 = [0, 0, 0, 1]
    return numpy.array([row0, row1, row2, row3], numpy.float32)

# creates an orthographic projection matrix
def _ortho(left, right, bot, top):
    row0 = [2.0 / (right - left), 0, 0, - (right + left) / (right - left)]
    row1 = [0, 2.0 / (top - bot), 0, - (top + bot) / (top - bot)]
    row2 = [0, 0, -1, 0]
    row3 = [0, 0, 0, 1]
    return numpy.array([row0, row1, row2, row3], numpy.float32)

# creates an affine translation matrix
def _translate(pos):
    row0 = [1, 0, 0, pos[0]]
    row1 = [0, 1, 0, pos[1]]
    row2 = [0, 0, 1, 0]
    row3 = [0, 0, 0, 1]
    return numpy.array([row0, row1, row2, row3], numpy.float32)

def sprite_pass(graph, pass_data):
        QUAD_VERTICES = numpy.array([ [ -0.5, -0.5, 0.0, 1.0 ],
                                      [ +0.5, -0.5, 0.0, 1.0 ],
                                      [ +0.5, +0.5, 0.0, 1.0 ],
                                      [ -0.5, +0.5, 0.0, 1.0 ] ], numpy.float32)

        ecs = global_vars.get_ecs()
        vertex_buffer = []
        index_buffer = []
        offset = 0
        for _, sprite in ecs.view("sprite_component"):
            scale = _scale(0.1)
            translate = _translate(sprite.position)
            for i in range(4):
                #transform = numpy.matmul(translate, scale)
                transform = numpy.matmul(scale, translate)
                pos = numpy.matmul(transform, QUAD_VERTICES[i])
                vertex_buffer.extend([pos[0], pos[1]])
                vertex_buffer.extend(sprite.color)

            index_buffer.extend([offset + 0, offset + 1, offset + 2, offset + 2, offset + 3, offset + 0])
            offset += 4

        vertex32f = numpy.array(vertex_buffer, numpy.float32)
        index32i = numpy.array(index_buffer, numpy.uint32)

        transform = _ortho(-16 / 9, 16/ 9, -1, 1)

        projection = pass_data["projection"]
        projection.value = transform.flatten(order='F')

        pass_data["vertex_buffer"].write(vertex32f)
        pass_data["index_buffer"].write(index32i)

        # pipeline is also hardcoded to save on time
        graph.submit(graph.get_pipeline("sprite_pipeline"), pass_data["vertex_buffer"], pass_data["index_buffer"],
                     [projection], index32i.size)
