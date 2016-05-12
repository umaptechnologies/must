class WarriorBody:
    def __init__(self, weapon):
        self.weapon = weapon.that_must('strike', 'target')

    def attack(self, target):
        self.weapon.strike(target)

    def retreat(self):
        pass
