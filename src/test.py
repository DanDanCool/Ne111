import moderngl
import pygame
import numpy

pygame.init()
pygame.display.set_mode((1280, 720), pygame.OPENGL | pygame.DOUBLEBUF, vsync = 1)
glcontext = moderngl.create_context()
glcontext.enable(moderngl.BLEND)
glcontext.blend_func = glcontext.SRC_ALPHA, glcontext.ONE_MINUS_SRC_ALPHA
glcontext.viewport = (0, 0, 1280, 720)

col0 = [1, 0, 0, 0]
col1 = [0, 1, 0, 0]
col2 = [0, 0, 1, 0]
col3 = [0, 0, 0, 1]
mat = []
mat.extend(col0)
mat.extend(col1)
mat.extend(col2)
mat.extend(col3)
mat = numpy.array(mat, numpy.float32)

vsbytes = None
with open("../assets/sprite_vert.glsl") as f:
    vsbytes = f.read()

fsbytes = None
with open("../assets/sprite_frag.glsl") as f:
    fsbytes = f.read()


vb = glcontext.buffer(None, reserve=24 * 4, dynamic=True)
ib = glcontext.buffer(None, reserve=6 * 4, dynamic=True)

QUAD_VERTICES = [ [ -0.5, -0.5 ],
                  [ +0.5, -0.5 ],
                  [ +0.5, +0.5 ],
                  [ -0.5, +0.5 ] ]

vertex_buffer = []
index_buffer = []
offset = 0
for i in range(4):
    vertex_buffer.extend(QUAD_VERTICES[i])
    vertex_buffer.extend([1, 0, 0, 1])

index_buffer.extend([offset + 0, offset + 1, offset + 2, offset + 2, offset + 3, offset + 0])
offset += 4

vertex32f = numpy.array(vertex_buffer, numpy.float32)
index32i = numpy.array(index_buffer, numpy.uint32)

vb.write(vertex32f)
ib.write(index32i)

program = glcontext.program(vertex_shader = vsbytes, fragment_shader = fsbytes)
program["u_proj"] = mat
va = glcontext.vertex_array(program, [ (vb, "2f 4f", "a_pos", "a_color") ], index_buffer = ib)

while True:
    pygame.event.pump()
    glcontext.clear(0.8, 0.2, 0.4, 1.0)
    glcontext.screen.use()
    va.render(moderngl.TRIANGLES, index32i.size)
    pygame.display.flip()
