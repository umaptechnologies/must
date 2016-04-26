class HearthstoneDeck:
    ''' Replicates the functionality of a deck in Hearthstone. '''
    def __init__(self, decklist, shuffler):
        decklist.must('get_list', '', '[card]')
        shuffler.must('shuffle', '[card]')

        self._cards = list(decklist.get_list())
        shuffler.shuffle(self._cards)
