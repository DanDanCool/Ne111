import engine

g_engine = None

def get_engine():
    global g_engine
    if g_engine == None:
        g_engine = engine.engine()
    return g_engine

def get_ecs():
    return get_engine().get_ecs()

def get_module(name):
    return get_engine().get_module(name)
