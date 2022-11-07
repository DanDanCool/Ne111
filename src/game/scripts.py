# script super class, all scripts inherit from this
class script:
    def __init__(self):
        self.next = None

    def update(self, entity, ts):
        pass
