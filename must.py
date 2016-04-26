import inspect
import types
from plastic import Plastic


class SafeObject:
    ''' Never fails a must. '''
    def must_be_factory(self):
        return self

    def must_not_be_factory(self):
        return self

    def must(self, action, taking='', returning=''):
        return self

    def must_have(self, *attributes):
        return self

    def must_use(self, **known_parameters):
        return self

    def must_make(self, obj_type, parameters):
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


def must_be_checkable(obj):
    if type(obj) in (int, bool):
        return

    obj.is_factory = False

    def this_must(self, action, taking='', returning=''):
        # TODO: Assert!
        return obj

    def this_must_have(self, *attributes):
        for a in attributes:
            assert hasattr(obj, a), str(obj)+" doesn't have "+a+"!"
        return obj

    obj.must = types.MethodType(this_must, obj)
    obj.must_have = types.MethodType(this_must_have, obj)
    obj.that_must = types.MethodType(this_must, obj)
    obj.that_must_have = types.MethodType(this_must_have, obj)
    obj.and_must = types.MethodType(this_must, obj)
    obj.and_must_have = types.MethodType(this_must_have, obj)
    return obj


def must_list_objects(possible_list):
    if not isinstance(possible_list, list):
        print "Warning: %s must be a list!" % str(possible_list)
    elif len(possible_list) > 0:
        return must_be_checkable(possible_list[0])
    else:
        return SafeObject()


class SafeFactory:
    ''' WRITEME '''
    def __init__(self, obj_constructor):
        self._obj_constructor = obj_constructor
        self.is_factory = True

    def make(self, *args):
        return self._obj_constructor(*args)

    def must_make(self, obj_type, parameters):
        return self

    def that_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)

    def and_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)


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
        self._dependencies = dict(zip(self._constructor_args,[Plastic() for x in self._constructor_args]))
        obj = constructor(**self._dependencies)  # TODO: THIS BLOWS UP!
        self._properties = []
        self._capabilities = {}
        members = filter(lambda x: not x[0].startswith('_'), inspect.getmembers(obj))
        for m in members:
            m_name, m_val = m
            if callable(m_val):
                args,x,y,defaults = inspect.getargspec(m_val)
                args = args[1:]  # Shave off 'self'
                try:
                    len(defaults)  # Throws an exception if the defaults are None
                    joins = [', '.join(args[:-(cut+1)]) for cut in range(len(defaults))]
                    joins.append(', '.join(args))
                    self._capabilities[m_name] = tuple(joins)  # TODO:Include 'returning'
                except:
                    self._capabilities[m_name] = ', '.join(args)  # TODO:Include 'returning'
            else:
                self._properties.append(m_name)

    def create(self, universe, known_parameters):
        params = {}
        for arg_name in self._dependencies:
            if arg_name in known_parameters:
                params[arg_name] = known_parameters[arg_name]
                must_be_checkable(params[arg_name])
            else:
                params[arg_name] = universe.create_with_namehint(str(self)+': "'+arg_name+'"', self._dependencies[arg_name])
        result = self._constructor(**params)
        must_be_checkable(result)
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
        if action in self._capabilities:
            numberOfArgsTaken = 0 if len(taking) is 0 else taking.count(',')+1  # TODO: This is bad and should feel bad.
            if str(type(self._capabilities[action])) == "<type 'str'>":  # TODO: This check isn't particularly elegant either.
                numberOfArgsProvided = 0 if len(self._capabilities[action]) is 0 else self._capabilities[action].count(',')+1
                return numberOfArgsTaken == numberOfArgsProvided  # TODO:Include 'returning'
            else:
                for x in self._capabilities[action]:
                    numberOfArgsProvided = 0 if len(x) is 0 else x.count(',')+1
                    if numberOfArgsTaken == numberOfArgsProvided:  # TODO: But seriously, we're just discarding the names?
                        return True  # TODO:Include 'returning'

        return False

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
        self._patterns = []
        for c in constructors:
            if hasattr(c, '__call__'):
                class Wrapper:
                    def __init__(self):
                        pass
                setattr(Wrapper, c.__name__, c)
                self._patterns.append(ClassPattern(Wrapper))
            else:
                self._patterns.append(ClassPattern(c))
                self._patterns.append(FactoryPattern(c))

    def create_with_namehint(self, name_hint, requirements):
        possibilities = filter(lambda x: x.matches(requirements), self._patterns)
        assert len(possibilities) is 1, self._write_error(name_hint, str(requirements), len(possibilities))
        return possibilities[0].create(self, requirements.known_parameters)

    def create(self, requirements):
        if isinstance(requirements, Plastic):
            return self.create_with_namehint('Object created from specification', requirements)
        elif isinstance(requirements, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p._constructor == requirements:
                    return p.create(self, {})
        raise Exception("Can't create object from unknown specficiation: "+str(requirements)+(" (%s)" % type(requirements)))

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
