from primitive_musts import must_be_string


class MustOutputToStdOut(object):
    ''' Wrapper for the "print" statement. '''
    def __init__(self):
        pass

    def output(self, text):
        text = must_be_string(text)
        self.must_return(None)
        print text
