class CantFindDependency(Exception):
    def __init__(self, name_hint, requirements_string, possibilities):
        self.name_hint = name_hint
        self.requirements_string = requirements_string
        self.possibilities = possibilities
        Exception.__init__(self, str(self))

    def __str__(self):
        # print "Patterns:"
        # for x in self._patterns:
        #    print '\t'+str(x)
        num_possibilities = len(self.possibilities)
        if num_possibilities is 0:
            return self.name_hint+' '+self.requirements_string+"; couldn't find any matches."
        elif num_possibilities is 1:
            return "WTF! Invalid error!"
        elif num_possibilities < 5:
            return self.name_hint+' '+self.requirements_string+"; too many matches: "+str(map(str, self.possibilities))
        else:
            return self.name_hint+' '+self.requirements_string+"; found "+str(num_possibilities)+" matches!"
