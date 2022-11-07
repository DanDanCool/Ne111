import time

def main():
    lasttime = time.perf_counter_ns()
    while game.run():
        time = time.perf_counter_ns()
        dt = time - lasttime
        lasttime = time
        game.update(dt)

if __name__ == "__main__":
    main()
