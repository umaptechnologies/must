from Vector2D import Vector2D


class NormalEyes:
    ''' I'm a pair of eyes! '''
    def __init__(self):
        pass

    def look(self, target):
        return str(target)


class NormalFeet:
    ''' I'm a pair of feet! '''
    def __init__(self):
        pass

    def walk(self, speed, direction):
        return speed, Vector2D(direction.x*speed,direction.y*speed)
