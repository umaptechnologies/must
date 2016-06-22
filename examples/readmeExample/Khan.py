class Khan:
    def __init__(self, random):
        self.random = random.that_must('get_random_integer', 'lower_bound_incl, upper_bound_incl')

    def give_orders(self):
        self.must_return(str)
        possible_orders = ['attack', 'retreat']
        return possible_orders[self.random.get_random_integer(0,1)]
