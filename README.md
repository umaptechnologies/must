# Must

Must is a combination dependency-injection, type-checking, and unit-testing library for python. The best way to understand Must is to see it in action.

## The Fickle Warlord

Genghis Khan is a Fickle Warlord. Why? Because he gives orders randomly.

```python
class GenghisKhan:
    def __init__(self, random):
        self.random = random.that_must('randint', 'lower_bound_incl, upper_bound_incl')

    def give_orders(self):
        possible_orders = ['attack', 'retreat']
        return possible_orders[self.random.randint(0,1)]
```

As you can see, Genghis is built with a source of randomness within him, and he uses this random seed to decide what to do. Unlike in standard dependency injection, this seed is checked by Must to ensure it conforms to the needs of GenghisKhan. This checking allows Must to automagically understand what our warlord needs and provides, and fit him into a broader context.

Instead of creating Genghis from scratch, we allow Must to create objects.

```python
from must import MustHavePatterns
import random

patterns = MustHavePatterns(GenghisKhan, random.randint)
khan = patterns.create(GenghisKhan)
```

Must, there, knows to use random.randint to satisfy GenghisKhan's need for randomness. This is because GenghisKhan specifically asks for a thing that must be able to "randint". But what if whoever wrote GenghisKhan had asked for `get_random_integer` instead of `randint`? For this we can *alias* the `random.randint` function under the label GenghisKhan expects.

```python
patterns = MustHavePatterns(GenghisKhan, random.randint)
patterns.alias(get_random_integer="randint")
khan = patterns.create(GenghisKhan)
```

Aliasing is a standard part of the Must encapsulation paradigm: modules should focus on *only* their functionality, letting a higher-order system wire the modules together. 
