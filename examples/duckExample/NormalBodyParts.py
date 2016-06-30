class NormalEyes:
    ''' I'm a pair of eyes! '''
    def __init__(self):
        pass

    def look(self, target):
        self.must_return(str)
        return str(target)


class NormalFeet:
    ''' I'm a pair of feet! '''
    def __init__(self, vector_factory):
        self._vector_factory = vector_factory.that_must_make('vector','x, y')

    def walk(self, speed, direction):
        self.must_return(int, 'vector')
        return speed, self._vector_factory.make(direction.x*speed, direction.y*speed)
