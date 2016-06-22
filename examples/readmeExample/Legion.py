from must import must_be_natural_number


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
