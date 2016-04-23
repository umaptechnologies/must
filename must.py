import inspect


def must_make_safe(obj):
    def identity(*x):
        return obj
    obj.must = identity
    obj.must_have = identity
    obj.must_use = identity
    obj.that_must = identity
    obj.that_must_have = identity
    obj.that_must_use = identity
    obj.and_must = identity
    obj.and_must_have = identity
    obj.and_must_use = identity


class Requirements:
    ''' WRITEME '''
    def __init__(self):
        self.properties = []
        self.capabilities = {}
        self.known_parameters = {}

    def must(self, action, taking, returning):
        self.capabilities[action] = [taking,returning]
        return self

    def must_have(self, *attributes):
        self.properties.extend(attributes)
        return self

    def must_use(self, **known_parameters):
        self.known_parameters.update(known_parameters)
        return self

    def that_must(self, action, taking='', returning=''):
        return self.must(action, taking, returning)

    def that_must_have(self, *attributes):
        return self.must_have(*attributes)

    def that_must_use(self, **known_parameters):
        return self.must_use(**known_parameters)

    def and_must(self, action, taking='', returning=''):
        return self.must(action, taking, returning)

    def and_must_have(self, *attributes):
        return self.must_have(*attributes)

    def and_must_use(self, **known_parameters):
        return self.must_use(**known_parameters)

    def __str__(self):
        result = 'must'
        if len(self.properties) > 0:
            result += " have "+', '.join(self.properties)
        if len(self.capabilities) > 0:
            result += ("," if len(self.known_parameters) > 0 else " and") if result != 'must' else ""
            result += " be able to "+', '.join(self.capabilities.keys())
        if len(self.known_parameters) > 0:
            result += " and" if result != 'must' else ""
            result += " be created with "+', '.join(self.known_parameters.keys())
        if result == 'must':  # If the requirement has no properties, capabilities, or known parameters
            return 'could be anything'
        return result


class ClassPattern:
    ''' WRITEME '''
    def __init__(self, constructor):
        self._constructor = constructor
        self._str = str(constructor)
        self._constructor_args = inspect.getargspec(constructor.__init__).args[1:]  # Ignore 'self'
        self._dependencies = dict(zip(self._constructor_args,[Requirements() for x in self._constructor_args]))
        obj = constructor(**self._dependencies)
        self._properties = []
        self._capabilities = {}
        members = filter(lambda x: not x[0].startswith('_'), inspect.getmembers(obj))
        for m in members:
            if callable(m[1]):
                args = inspect.getargspec(m[1]).args[1:]
                self._capabilities[m[0]] = ', '.join(args)  # TODO:Include 'returning'
            else:
                self._properties.append(m[0])

    def create(self, universe, known_parameters):
        params = {}
        for arg_name in self._dependencies:
            if arg_name in known_parameters:
                params[arg_name] = known_parameters[arg_name]
            else:
                params[arg_name] = universe.create_from_requirements(str(self)+': "'+arg_name+'"', self._dependencies[arg_name])
            must_make_safe(params[arg_name])
        return self._constructor(**params)

    def matches(self, requirements):
        has_properties = self.has(requirements.properties)
        c = requirements.capabilities
        has_capabilities = all([self.can(a,c[a][0],c[a][1]) for a in c])
        return has_properties and has_capabilities

    def has(self, attributes):
        return all([x in self._properties for x in attributes])

    def can(self, action, taking, returning):
        return action in self._capabilities and self._capabilities[action] == taking  # TODO:Include 'returning'

    def __str__(self):
        result = self._str
        if len(self._properties) > 0:
            result += " has "+', '.join(self._properties)
        if len(self._capabilities) > 0:
            result += " and can " if len(self._properties) > 0 else " can "
            result += ', '.join(self._capabilities.keys())
        return result


class MustHavePatterns:
    ''' Nothing to see here... '''
    def __init__(self, *constructors):
        self._patterns = map(ClassPattern, constructors)

    def create_from_requirements(self, name_hint, requirements):
        possibilities = filter(lambda x: x.matches(requirements), self._patterns)
        assert len(possibilities) is 1, self._write_error(name_hint, str(requirements), len(possibilities))
        return possibilities[0].create(self, requirements.known_parameters)

    def create(self, specification):
        requirements = specification(Requirements())
        return self.create_from_requirements('Object created from specification', requirements)

    def _write_error(self, name_hint, requirements_string, num_possibilities):
        # print "Patterns:"
        # for x in self._patterns:
        #     print '\t'+str(x)
        if num_possibilities is 0:
            return name_hint+' '+requirements_string+"; couldn't find any matches."
        elif num_possibilities is 1:
            return "WTF! Invalid error!"
        else:
            return name_hint+' '+requirements_string+"; found "+str(num_possibilities)+" matches!"
