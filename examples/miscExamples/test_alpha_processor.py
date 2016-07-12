from must import MustHavePatterns
# from must import must_be_something
import alpha_processor as ap


class TestAlphaProcessor(object):
    def setup(self):
        test_patterns = MustHavePatterns(ap.AlphaToBetaProcessor, ap.AlphaToOmegaProcessor, ap.AlphaToGammaProcessor, ap.Alpha, ap.Beta, ap.Gamma, ap.Omega)
        # self.atbp = test_patterns.create(must_be_something().that_must('process', 'alpha'))
        self.atgp = test_patterns.create(ap.AlphaToGammaProcessor)

    def test_yay(self):
        self.atgp.process(ap.Alpha)
