# Must

Must is a combination dependency-injection, type-checking, and testing-assistance library for python. The best way to understand Must is to see it in action.

## The Fickle Warlord

Khans are Fickle Warlords. Why? Because they give orders randomly.

```python
class Khan:
    def __init__(self, random):
        self.random = random.that_must('randint', 'lower_bound_incl, upper_bound_incl', int)

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

Must, there, knows to use random.randint to satisfy Khan's need for randomness. This is because Khan specifically asks for a thing that must be able to `randint`. But what if whoever wrote Khan had asked for `get_random_integer` instead of `randint`? For this we can *alias* the `random.randint` function under the label Khan expects.

```python
patterns = MustHavePatterns(Khan, random.randint)
patterns.alias(get_random_integer="randint")
khan = patterns.create(Khan)
```

Aliasing is a standard part of the Must encapsulation paradigm: modules should focus on *only* their functionality, letting a higher-order system wire the modules together.

## The Simple Warrior

WarriorBodies are the Bodies of Simple Warriors. Why? Because they hold weapons, and can attack or retreat.

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
        orders = must_be_string(orders)
        if orders == "attack":
            self.body.attack(self.enemy)
        elif orders == "retreat":
            self.body.retreat()
```

Note the call to `and_must` instead of `that_must`. These are both just aliases for the `must` method. `body.that_must('attack', 'target').and_must('retreat')` is equivalent to `body.must('attack', 'target').must('retreat')`.

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

`Singing Spear says: "I don't want to hit Cousin Steve! I'm a pacifist!"`

## The Coordinated Army

Legions are Coordinated Armies. Why? Because they have a Warlord and some Warriors that wage war together.

```python
class Legion:
    def __init__(self, warlord, warrior_factory, warrior_count, enemy, output_stream):
        self.warlord = warlord.that_must('give_orders')
        warrior_factory = warrior_factory.that_must_make('warrior', 'enemy').that_must('follow_orders', 'orders')
        warrior_count = must_be_natural_number(warrior_count)
        self.output_stream = output_stream.that_must('output', 'text')

        self.warriors = [warrior_factory.make(enemy) for i in range(warrior_count)]

    def wage_war(self):
        orders = self.warlord.give_orders()
        self.output_stream.output(str(self.warlord)+' orders: '+str(orders))
        for warrior in self.warriors:
            warrior.follow_orders(orders)
```

Legion has some interesting things about it. First, we notice that the constructor takes a warrior_factory. Unlike earlier examples that constrained dependencies by calling `must` (via aliases `that_must` & `and_must`), we constrain the warrior_factory by calling `must_make` (which also has aliases of `that_must_make` & `and_must_make`). By saying something `must_make`, we're telling Must that the dependency is a factory. We can chain additional calls to constrain the kinds of factories that we'll accept. In this case, the factory must take an enemy when it builds the warrior, and the warrior must follow_orders.

All factories are created by Must, itself. Whenever we add a pattern to MustHavePatterns, Must automagically builds a corresponding factory for that pattern. Thus, without having to write a single line of code, we already have a KhanFactory, a WarriorBodyFactory, an AshigaruFactory, and so on. Calling `make` on an AshigaruFactory returns a new Ashigaru.

Legion also takes a warrior_count. Unlike previous examples of dependencies, warrior_count is not an object; it's a natural number. When dealing with primitive data, we constrain it by calling one of several `must_be_x` functions. In this case we call `must_be_natural_number`. It is important that we assign the results of the must to the original variable before we do work with it.

```python
patterns = MustHavePatterns(Khan, WarriorBody, Ashigaru, SingingSpear, Legion, random.randint, MustOutputToStdOut)
patterns.alias(get_random_integer="randint")
legion = patterns.create(Legion, with_warrior_count=7, with_enemy="Cousin Steve")
legion.wage_war()
```

## The Curious Programmer

All this code is well and good, but what happens if a Curious Programmer wants to understand the system?

```python
patterns = MustHavePatterns(Khan, WarriorBody, Ashigaru, SingingSpear, Legion, random.randint, MustOutputToStdOut)
print patterns.describe(Khan)
```

This will spit out a description of the Khan class:

```
Khan:
        Khan(random that must be able to get_random_integer(lower_bound_incl, upper_bound_incl) -> <type 'int'>) -> Khan
        give_orders() -> <type 'str'>
```
