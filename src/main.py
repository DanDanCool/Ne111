import global_vars

def main():
    g = global_vars.get_engine()
    g.load_modules()
    g.run()

if __name__ == "__main__":
    main()
