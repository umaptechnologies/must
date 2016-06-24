class CantFindDependency(Exception):
    def __init__(self, name_hint, requirements, possibilities):
        self.name_hint = name_hint
        self.requirements = requirements
        self.possibilities = possibilities
        Exception.__init__(self, str(self))

    def __str__(self):
        num_possibilities = len(self.possibilities)
        if num_possibilities is 0:
            return self.name_hint+' '+str(self.requirements)+"; couldn't find any matches."
        elif num_possibilities is 1:
            return "WTF! Invalid error!"
        elif num_possibilities < 5:
            return self.name_hint+' '+str(self.requirements)+"; too many matches: "+str(map(str, self.possibilities))
        else:
            return self.name_hint+' '+str(self.requirements)+"; found "+str(num_possibilities)+" matches!"
