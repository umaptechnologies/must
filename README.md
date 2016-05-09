# Must

Must is a combination dependency-injection, type-checking, and unit-testing library for python. The best way to understand Must is to see it in action.

## The Fickle Warlord

Khans are Fickle Warlords. Why? Because they give orders randomly.

```python
class Khan:
    def __init__(self, random):
        self.random = random.that_must('randint', 'lower_bound_incl, upper_bound_incl')

    def give_orders(self):
        possible_orders = ['attack', 'retreat']
        return possible_orders[self.random.randint(0,1)]
```

As you can see, Khans are built with a source of randomness within them, and they use this random seed to decide what to do. Unlike in standard dependency injection, this seed is checked by Must to ensure it conforms to the needs of Khan. This checking allows Must to automagically understand what our warlords need and provide, and fit them into a broader context.

Instead of creating our warlord from scratch, we allow Must to create objects.

```python
from must import MustHavePatterns
import random

patterns = MustHavePatterns(Khan, random.randint)
khan = patterns.create(Khan)
```

Must, there, knows to use random.randint to satisfy Khan's need for randomness. This is because Khan specifically asks for a thing that must be able to "randint". But what if whoever wrote Khan had asked for `get_random_integer` instead of `randint`? For this we can *alias* the `random.randint` function under the label Khan expects.

```python
patterns = MustHavePatterns(Khan, random.randint)
patterns.alias(get_random_integer="randint")
khan = patterns.create(Khan)
```

Aliasing is a standard part of the Must encapsulation paradigm: modules should focus on *only* their functionality, letting a higher-order system wire the modules together.

## The Simple Warrior

WarriorBody are the Bodies of Simple Warriors. Why? Because they hold weapons, and can attack or retreat.

```python
class WarriorBody:
    def __init__(self, weapon):
        self.weapon = weapon.that_must('strike', 'target')

    def attack(self, target):
        self.weapon.strike(target)

    def retreat(self):
        pass
```

Or at least they can attack. When a WarriorBody retreats nothing happens. Note that a WarriorBody is not able to listen to orders. To make things work together, we'll make a new class, Ashigaru, to handle the entirety of being a Simple Warrior.

```python
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
```

Now what happens if we try and create an Ashigaru?

```python
patterns = MustHavePatterns(Khan, WarriorBody, Ashigaru, random.randint)
patterns.alias(get_random_integer="randint")
ashigaru = patterns.create(Ashigaru)
```

Must will inform us of the missing dependency:

`WarriorBody needs a "weapon" that must be able to strike; couldn't find any matches.`

In other words, to create our Ashigaru, we need a WarriorBody, and to create a WarriorBody we need a Weapon. With Must we can build our modules in a way that their dependencies don't have to be in place when building or unit-testing them (you don't even need interfaces), but then they're easy to determine when it comes time to wire them together.

```python
class SingingSpear:
    def __init__(self, output_stream):
        self.output_stream = output_stream.that_must('output', 'text')

    def strike(self, target):
        self.output_stream.output('Singing Spear says: "I don\'t want to hit %s! I\'m a pacifist!"' % str(target))
```

We can import a wrapper for StdOut from Must and now we're ready to go! (Right?)

```python
patterns = MustHavePatterns(Khan, WarriorBody, Ashigaru, SingingSpear, random.randint, must.MustOutputToStdOut)
patterns.alias(get_random_integer="randint")
ashigaru = patterns.create(Ashigaru)
```

Wrong!

`Ashigaru needs an "enemy" that could be anything; found 6 matches!`

Must is good at figuring out what to plug into where, but sometimes there's too much freedom. In this case, the Ashigaru needs an enemy, but Must can't figure out what that enemy should be. When creating objects with Must we can tell it to use specific parameters like this:

```python
ashigaru = patterns.create(Ashigaru, with_enemy="Cousin Steve")
ashigaru.follow_orders("attack")
```
