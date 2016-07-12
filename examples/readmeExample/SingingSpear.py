class SingingSpear(object):
    def __init__(self, output_stream):
        self.output_stream = output_stream.that_must('output', 'text')

    def strike(self, target):
        self.output_stream.output('Singing Spear says: "I don\'t want to hit %s! I\'m a pacifist!"' % str(target))
