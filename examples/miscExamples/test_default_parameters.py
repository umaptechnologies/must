from must import MustHavePatterns
from default_parameters import WordSpitter


class TestWordSpitter(object):
    def setup(self):
        test_patterns = MustHavePatterns(WordSpitter)
        self.spitter = test_patterns.create(WordSpitter)

    def test_can_say_favorite_word(self):
        assert self.spitter.say() == self.spitter.favorite_word
