from must import MustHavePatterns
import random


class GenghisKhan:
    def __init__(self, random):
        self.random = random.that_must('get_random_integer', 'lower_bound_incl, upper_bound_incl')

    def give_orders(self):
        possible_orders = ['attack', 'retreat']
        return possible_orders[self.random.get_random_integer(0,1)]


patterns = MustHavePatterns(GenghisKhan, random.randint)
patterns.alias(get_random_integer="randint")
khan = patterns.create(GenghisKhan)
print khan.give_orders()
