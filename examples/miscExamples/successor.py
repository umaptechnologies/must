class Successor(object):
    def __init__(self, prev):
        self.prev = prev.that_must('get_prev')

    def get_prev(self):
        return self.prev
