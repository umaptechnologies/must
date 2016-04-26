from must import MustHavePatterns
from hearthstone_deck import HearthstoneDeck
from random import shuffle


class MockDecklist:
    def __init__(self):
        pass

    def get_list(self):
        return ["Hunter's Mark", "Unleash The Hounds", "Acidmaw"]


class TestHearthsoneDeck:
    @classmethod
    def setup_class(cls):
        cls.test_patterns = MustHavePatterns(HearthstoneDeck, MockDecklist, shuffle)

    def test_create_deck(self):
        deck = self.test_patterns.create(HearthstoneDeck)

        assert deck is not None
