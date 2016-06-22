from must import must_be_something


class Alpha:
    def __init__(self):
        pass


class Beta:
    def __init__(self, root):
        self.root = root
        self.special_sauce = True


class Omega:
    def __init__(self, root):
        self.root = root
        self.dance_paste = True


class Gamma:
    def __init__(self, root, quickshot):
        self.root = root
        self.quickshot = quickshot


class AlphaToBetaProcessor:
    def __init__(self, beta_factory):
        self.beta_factory = beta_factory.that_must_make('beta', 'root').that_must_have('special_sauce')

    def process(self, alpha):
        self.must_return('beta').that_must_have('special_sauce')
        return self.beta_factory.make(alpha)


class AlphaToOmegaProcessor:
    def __init__(self, omega_factory):
        self.omega_factory = omega_factory.that_must_make('omega', 'root').that_must_have('dance_paste')

    def process(self, alpha):
        self.must_return('omega')
        return self.omega_factory.make(alpha)


class AlphaToGammaProcessor:
    def __init__(self, alpha_to_beta_processor, gamma_factory):
        self.alpha_to_beta_processor = alpha_to_beta_processor.that_must('process', 'alpha', must_be_something().that_must_have('special_sauce'))
        self.gamma_factory = gamma_factory.that_must_make('gamma', 'root, quickshot')

    def process(self,alpha):
        self.must_return('gamma')
        beta = self.alpha_to_beta_processor.process(alpha)
        return self.gamma_factory.make(beta, beta.special_sauce)
