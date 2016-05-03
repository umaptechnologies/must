# Must

Must is a combination dependency-injection, type-checking, and unit-testing library for python. The best way to understand Must is to see it in action.

## The Fickle Warlord

Genghis Khan is a Fickle Warlord. Why? Because he gives orders randomly.

    class GenghisKhan:
        def __init__(self, random):
            self.random = random.that_must('generate_random_int', 'lower_bound_incl, upper_bound_excl')
            
        def give_orders(self):
            possible_orders = ['attack', 'retreat']
            return possible_orders[self.random.generate_random_int(0,2)]
            
As you can see, Genghis is built with a source of randomness within him, and he uses this random seed to decide what to do. Unlike in standard dependency injection, this seed is checked by Must to ensure it conforms to the needs of GenghisKhan. This checking allows Must to automagically understand what our warlord needs and provides, and fit him into a broader context.
