from must import MustHavePatterns
from hearthstone_deck import HearthstoneDeck
from mock import call


class TestHearthsoneDeck:
    def setup(self):
        test_patterns = MustHavePatterns(HearthstoneDeck)
        self.mock_decklist, self.mock_shuffler, self.mock_fatigue_factory = test_patterns.mock_dependencies(HearthstoneDeck, '__init__')
        self.decklist = ["Acidmaw","Hunter's Mark","Lepper Gnome"]
        self.mock_decklist.get_list.return_value = list(self.decklist)
        self.deck = HearthstoneDeck(self.mock_decklist, self.mock_shuffler, self.mock_fatigue_factory)

    def test_deck_is_shuffled(self):
        self.mock_shuffler.shuffle.assert_called_once_with(self.decklist)

    def test_get_increasing_fatigue(self):
        for i in range(len(self.decklist)+2):
            self.deck.draw_card()

        assert self.mock_fatigue_factory.make.call_count is 2
        self.mock_fatigue_factory.make.assert_has_calls([call(1), call(2)])
