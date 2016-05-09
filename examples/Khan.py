from must import MustHavePatterns
from must import must_be_string
from must import MustOutputToStdOut
import random


class Khan:
    def __init__(self, random):
        self.random = random.that_must('get_random_integer', 'lower_bound_incl, upper_bound_incl')

    def give_orders(self):
        possible_orders = ['attack', 'retreat']
        return possible_orders[self.random.get_random_integer(0,1)]


class WarriorBody:
    def __init__(self, weapon):
        self.weapon = weapon.that_must('strike', 'target')

    def attack(self, target):
        self.weapon.strike(target)

    def retreat(self):
        pass


class Ashigaru:
    def __init__(self, body, enemy):
        self.body = body.that_must('attack', 'target').and_must('retreat')
        self.enemy = enemy

    def follow_orders(self, orders):
        must_be_string(orders)
        if orders == "attack":
            self.body.attack(self.enemy)
        elif orders == "retreat":
            self.body.retreat()


class SingingSpear:
    def __init__(self, output_stream):
        self.output_stream = output_stream.that_must('output', 'text')

    def strike(self, target):
        self.output_stream.output('Singing Spear says: "I don\'t want to hit %s! I\'m a pacifist!"' % str(target))


patterns = MustHavePatterns(Khan, WarriorBody, Ashigaru, SingingSpear, random.randint, MustOutputToStdOut)
patterns.alias(get_random_integer="randint")
ashigaru = patterns.create(Ashigaru, with_enemy="Cousin Steve")
ashigaru.follow_orders("attack")
