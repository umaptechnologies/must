from must import must_be_string


class WordSpitter(object):
    def __init__(self, favorite_word='Pastry'):
        self.favorite_word = must_be_string(favorite_word)

    def say(self, suffix=None):
        self.must_return(str)
        return self.favorite_word+('' if suffix is None else suffix)
