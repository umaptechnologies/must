class Vector2D:
    ''' Yet another vector class. '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate(self, other_vector):
        self.x += other_vector.x
        self.y += other_vector.y

    def get_direction_of(self, object):
        other_vector = object.location
        return Vector2D(other_vector.x-self.x, other_vector.y-self.y)

    def invert(self):
        return Vector2D(self.x*-1, self.y*-1)
