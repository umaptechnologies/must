import inspect
import re


def new_thing():
    return Requirements()


def must_make_safe(obj):
    if type(obj) in (int, bool):
        return

    def identity(*x, **y):
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


class SafeFactory:
    ''' WRITEME '''
    def __init__(self, obj_constructor):
        self._obj_constructor = obj_constructor

    def make(self, *args):
        return self._obj_constructor(*args)

    def must_make(self, obj_type, parameters):
        return self

    def that_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)

    def and_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)


class Requirements:
    ''' WRITEME '''
    def __init__(self):
        self.is_factory = None  # This becomes True or False as soon as a requirement is specified
        self.properties = []
        self.capabilities = {}
        self.parameters = []
        self.known_parameters = {}

    def must_be_factory(self):
        assert self.is_factory is not False
        self.is_factory = True

    def must_not_be_factory(self):
        assert self.is_factory is not True
        self.is_factory = False

    def must(self, action, taking, returning):
        self.must_not_be_factory()
        self.capabilities[action] = [taking,returning]
        return self

    def must_have(self, *attributes):
        self.must_not_be_factory()
        self.properties.extend(attributes)
        return self

    def must_use(self, **known_parameters):
        self.must_not_be_factory()
        self.known_parameters.update(known_parameters)
        return self

    def must_make(self, obj_type, parameters):
        self.must_be_factory()
        self.parameters = re.split('\s*,\s*',parameters)
        return self

    def that_must(self, action, taking='', returning=''):
        return self.must(action, taking, returning)

    def that_must_have(self, *attributes):
        return self.must_have(*attributes)

    def that_must_use(self, **known_parameters):
        return self.must_use(**known_parameters)

    def that_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)

    def and_must(self, action, taking='', returning=''):
        return self.must(action, taking, returning)

    def and_must_have(self, *attributes):
        return self.must_have(*attributes)

    def and_must_use(self, **known_parameters):
        return self.must_use(**known_parameters)

    def and_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)

    def __str__(self):
        result = 'must'
        if self.is_factory:
            result += " be factory ("+', '.join(self.parameters)+")"
        else:
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


class FactoryPattern:
    ''' WRITEME '''
    def __init__(self, constructor):
        self._constructor = constructor
        self._constructor_args = inspect.getargspec(constructor.__init__).args[1:]  # Ignore 'self'

    def create(self, universe, known_parameters):
        return SafeFactory(self._constructor)

    def matches(self, requirements):
        is_factory = requirements.is_factory
        has_parameters = self.has_parameters(requirements.parameters)
        return is_factory and has_parameters

    def has_parameters(self, parameters):
        return all([x in self._constructor_args for x in parameters])

    def __str__(self):
        result = str(self._constructor)+" factory ("
        result += ', '.join(self._constructor_args)
        result += ")"
        return result


class ClassPattern:
    ''' WRITEME '''
    def __init__(self, constructor):
        self._constructor = constructor
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
                must_make_safe(params[arg_name])
            else:
                params[arg_name] = universe.create_with_namehint(str(self)+': "'+arg_name+'"', self._dependencies[arg_name])
        result = self._constructor(**params)
        must_make_safe(result)
        return result

    def matches(self, requirements):
        isnt_factory = not requirements.is_factory
        has_properties = self.has(requirements.properties)
        c = requirements.capabilities
        has_capabilities = all([self.can(a,c[a][0],c[a][1]) for a in c])
        takes_parameters = all([self.takes(x) for x in requirements.known_parameters.keys()])
        return isnt_factory and has_properties and has_capabilities and takes_parameters

    def has(self, attributes):
        return all([x in self._properties for x in attributes])

    def can(self, action, taking, returning):
        return action in self._capabilities and self._capabilities[action] == taking  # TODO:Include 'returning'

    def takes(self, parameter):
        return parameter in self._dependencies

    def __str__(self):
        result = str(self._constructor)
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
        self._patterns.extend(map(FactoryPattern, constructors))

    def create_with_namehint(self, name_hint, requirements):
        possibilities = filter(lambda x: x.matches(requirements), self._patterns)
        assert len(possibilities) is 1, self._write_error(name_hint, str(requirements), len(possibilities))
        return possibilities[0].create(self, requirements.known_parameters)

    def create(self, requirements):
        return self.create_with_namehint('Object created from specification', requirements)

    def _write_error(self, name_hint, requirements_string, num_possibilities):
        # print "Patterns:"
        # for x in self._patterns:
        #    print '\t'+str(x)
        if num_possibilities is 0:
            return name_hint+' '+requirements_string+"; couldn't find any matches."
        elif num_possibilities is 1:
            return "WTF! Invalid error!"
        else:
            return name_hint+' '+requirements_string+"; found "+str(num_possibilities)+" matches!"
