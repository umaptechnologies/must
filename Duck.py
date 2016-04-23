class Duck:
    ''' I'm a duck! '''
    def __init__(self, wings, eyes, location, feet):
        self.wings = wings.that_must('flap', 'frequency', 'calories_burnt')
        self.eyes = eyes.that_must('look', 'target', 'appearance')
        self.location = location \
            .that_must_have('x','y') \
            .and_must('translate',taking='other_vector') \
            .and_must('get_direction_of','entity','vector')
        self.feet = feet.that_must('walk', 'speed, direction', 'calories_burnt, translation_vector')
        self.energy = 100

    def respond(self, words, source):
        # words.must_be_a_string()
        source.must_have('location')
        # self.must_return()

        if words == 'Boo!' and self.energy > 0:
            calories_burnt_from_flapping = self.wings.flap(4)
            calories_burnt_from_walking, movement = self.feet.walk(10, self.location.get_direction_of(source).invert())
            self.energy = self.energy - calories_burnt_from_walking - calories_burnt_from_flapping
            self.location.translate(movement)


class UselessDuckWings:
    ''' I can flap, but nothing else. '''
    def __init__(self):
        pass

    def flap(self, frequency):
        return frequency*2  # calories_burnt


class MeanChild:
    ''' I'm a kid that loves saying "Boo!" '''
    def __init__(self, location):
        self.location = location.that_must_have('x','y').and_must('translate','other_vector')

    def start_conversation(self):
        return "Boo!"
