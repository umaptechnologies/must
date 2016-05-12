from must import MustHavePatterns
from must import must_be_string
from must import must_be_natural_number
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


class Legion:
    def __init__(self, warlord, warrior_factory, warrior_count, enemy, output_stream):
        self.warlord = warlord.that_must('give_orders')
        warrior_factory.that_must_make('warrior', 'enemy').that_must('follow_orders', 'orders')
        warrior_count = must_be_natural_number(warrior_count)
        self.output_stream = output_stream.that_must('output', 'text')

        self.warriors = [warrior_factory.make(enemy) for i in range(warrior_count)]

    def wage_war(self):
        orders = self.warlord.give_orders()
        self.output_stream.output(str(self.warlord)+' orders: '+str(orders))
        for warrior in self.warriors:
            warrior.follow_orders(orders)


patterns = MustHavePatterns(Khan, WarriorBody, Ashigaru, SingingSpear, Legion, random.randint, MustOutputToStdOut)
patterns.alias(get_random_integer="randint")
legion = patterns.create(Legion, with_warrior_count=7, with_enemy="Cousin Steve")
legion.wage_war()
print patterns.describe(Khan)
