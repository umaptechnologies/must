from must import MustHavePatterns

from Khan import Khan
from WarriorBody import WarriorBody
from Ashigaru import Ashigaru
from SingingSpear import SingingSpear
from Legion import Legion
import random
from must import MustOutputToStdOut

patterns = MustHavePatterns(Khan, WarriorBody, Ashigaru, SingingSpear, Legion, random.randint, MustOutputToStdOut)
patterns.alias(get_random_integer="randint")


def test_legion():
    legion = patterns.create(Legion, with_warrior_count=7, with_enemy="Cousin Steve")
    legion.wage_war()

if __name__ == '__main__':
    test_legion()
    print patterns.describe(Khan)
