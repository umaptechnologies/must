class Vector2D(object):
    ''' Yet another vector class. '''
    def __init__(self, vector_factory, x, y):
        self.vector_factory = vector_factory.that_must_make('Vector2D', 'vector_factory, x, y')
        self.x = x
        self.y = y

    def translate(self, other_vector):
        self.must_return(None)
        self.x += other_vector.x
        self.y += other_vector.y

    def get_direction_of(self, other_obj):
        self.must_return('Vector2D')
        other_vector = other_obj.location
        return self.vector_factory.make(self.vector_factory, other_vector.x-self.x, other_vector.y-self.y)

    def invert(self):
        self.must_return('Vector2D')
        return self.vector_factory.make(self.vector_factory, self.x*-1, self.y*-1)

    def __str__(self):
        return "%d,%d" % (self.x,self.y)
