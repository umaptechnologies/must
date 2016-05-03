from must import MustHavePatterns
from hearthstone_deck import HearthstoneDeck
from mock import call


class TestHearthsoneDeck:
    @classmethod
    def setup_class(cls):
        cls.test_patterns = MustHavePatterns(HearthstoneDeck)

    def test_deck_is_shuffled(self):
        mock_decklist, mock_shuffler, mock_fatigue_factory = self.test_patterns.mock_dependencies(HearthstoneDeck, '__init__')
        decklist = ["Acidmaw","Hunter's Mark","Lepper Gnome"]
        mock_decklist.get_list.return_value = list(decklist)

        HearthstoneDeck(mock_decklist, mock_shuffler, mock_fatigue_factory)

        mock_shuffler.shuffle.assert_called_once_with(decklist)

    def test_get_increasing_fatigue(self):
        mock_decklist, mock_shuffler, mock_fatigue_factory = self.test_patterns.mock_dependencies(HearthstoneDeck, '__init__')
        decklist = ["Acidmaw","Hunter's Mark","Lepper Gnome"]
        mock_decklist.get_list.return_value = list(decklist)
        deck = HearthstoneDeck(mock_decklist, mock_shuffler, mock_fatigue_factory)

        for i in range(len(decklist)+2):
            deck.draw_card()

        assert mock_fatigue_factory.make.call_count is 2
        mock_fatigue_factory.make.assert_has_calls([call(1), call(2)])
