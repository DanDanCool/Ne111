import global_vars

# engine has to be globally accessible, in addition there must be only one at all times
# unfortunately a singleton has to be used to facilitate this, which makes dependencies unclear
# this weakness is due to the underlying design of the engine, because from the onset of development a distinction between
# engine and game code were not clearly defined
def main():
    g = global_vars.get_engine()
    # one of the main themes of this engine is treating code as data, allowing for highly modulr design
    # however modularizing all aspects of the engine was a mistake in my opinion, as most important features were
    # implmeented in modules, which necessidated exposing them globally
    # an interesting consequences of this however is the ability to hot-reload code at runtime
    g.load_modules()
    # most of the main loop was moved onto the engine as in my opinion it provides greater flexibility
    g.run()

if __name__ == "__main__":
    main()
