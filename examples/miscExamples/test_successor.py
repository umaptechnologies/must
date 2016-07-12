from must import MustHavePatterns
from successor import Successor


class TestSuccessor(object):
    @classmethod
    def setup_class(cls):
        cls.test_patterns = MustHavePatterns(Successor)

    def test_successor(self):
        try:
            self.test_patterns.create(Successor)
            raise Exception("Recursive structure did not explode.")
        except RuntimeError as re:
            assert str(re).startswith("maximum recursion depth")
