from must import MustHavePatterns
from hearthstone_deck import HearthstoneDeck
import random


class MockDecklist:
    def __init__(self):
        pass

    def get_list(self):
        return ["Hunter's Mark", "Unleash The Hounds", "Acidmaw"]


class MockFatigue:
    def __init__(self, fatigue_counter):
        self.fatigue_counter = fatigue_counter


class TestHearthsoneDeck:
    @classmethod
    def setup_class(cls):
        cls.test_patterns = MustHavePatterns(HearthstoneDeck, MockDecklist, MockFatigue, random.shuffle)

    def test_deck_is_shuffled(self):
        mock_decklist, mock_shuffler, mock_fatigue_factory = self.test_patterns.mock_dependencies(HearthstoneDeck, '__init__')

        HearthstoneDeck(mock_decklist, mock_shuffler, mock_fatigue_factory)

        mock_shuffler.shuffle.assert_called_once_with([])

    def test_get_increasing_fatigue(self):
        deck = self.test_patterns.create(HearthstoneDeck)

        for i in range(3):
            deck.draw_card()
        fatigue1 = deck.draw_card()
        fatigue2 = deck.draw_card()

        assert isinstance(fatigue1, MockFatigue)
        assert fatigue1.fatigue_counter == 1
        assert isinstance(fatigue2, MockFatigue)
        assert fatigue2.fatigue_counter == 2
