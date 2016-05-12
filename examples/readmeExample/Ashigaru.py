from must import must_be_string


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
