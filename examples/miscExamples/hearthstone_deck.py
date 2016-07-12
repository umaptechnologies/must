class HearthstoneDeck(object):
    ''' Replicates the functionality of a deck in Hearthstone. '''
    def __init__(self, decklist, shuffler, fatigue_factory):
        decklist.must('get_list', returning='[card]')
        shuffler.must('shuffle', '[card]')
        self.fatigue_factory = fatigue_factory.that_must_make('fatigue', 'fatigue_counter')
        self.fatigue = 0

        self._cards = list(decklist.get_list())
        shuffler.shuffle(self._cards)

    def draw_card(self):
        try:
            return self._cards.pop()
        except IndexError:
            self.fatigue += 1
            return self.fatigue_factory.make(self.fatigue)
