import inspect
import types
from mock import MagicMock
from plastic import Plastic


def _mock_must_return_itself_for_must_calls(mock):
    mock.must_be_factory.return_value = mock
    mock.must_not_be_factory.return_value = mock
    mock.must.return_value = mock
    mock.must_have.return_value = mock
    mock.must_use.return_value = mock
    mock.must_make.return_value = mock
    mock.that_must.return_value = mock
    mock.that_must_have.return_value = mock
    mock.that_must_use.return_value = mock
    mock.that_must_make.return_value = mock
    mock.and_must.return_value = mock
    mock.and_must_have.return_value = mock
    mock.and_must_use.return_value = mock
    mock.and_must_make.return_value = mock


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


def must_handle_synonyms(obj, synonym_dict):
    for member in inspect.getmembers(obj):
        m_name, m_val = member
        if callable(m_val) and not m_name.startswith('_') and m_name in synonym_dict:
            for alias in synonym_dict[m_name]:
                if not hasattr(obj, alias):
                    setattr(obj, alias, m_val)


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

    def create(self, universe, aliases, known_parameters):
        return SafeFactory(self._constructor)

    def matches(self, requirements, aliases):
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
        self._ordered_dependencies = [Plastic() for x in self._constructor_args]
        self._dependencies = dict(zip(self._constructor_args,self._ordered_dependencies))
        obj = constructor(**self._dependencies)  # TODO: THIS BLOWS UP! WATCH FOR EXPLOSIONS!
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

    def describe(self, member_name):
        if member_name == "__init__":
            arg_headers = [x[0]+' that '+str(x[1]) for x in self._dependencies.items()]
            return member_name+"(\n\t"+',\n\t'.join(arg_headers)+"\n) -> "+str(self._constructor)
        raise NotImplementedError  # TODO

    def mock_dependencies(self, method_name):
        if method_name == "__init__":
            mocks = map(lambda x: MagicMock(spec=[m[0] for m in inspect.getmembers(x)]), self._ordered_dependencies)
            map(_mock_must_return_itself_for_must_calls, mocks)
            return mocks
        raise NotImplementedError  # TODO

    def create(self, universe, aliases, known_parameters):
        params = {}
        for arg_name in self._dependencies:
            if arg_name in known_parameters:
                params[arg_name] = known_parameters[arg_name]
                must_be_checkable(params[arg_name])
            else:
                params[arg_name] = universe.create_with_namehint(str(self)+': "'+arg_name+'"', self._dependencies[arg_name])
        result = self._constructor(**params)
        must_handle_synonyms(result, aliases)
        must_be_checkable(result)
        return result

    def matches(self, requirements, aliases):
        isnt_factory = not requirements.is_factory
        has_properties = self.has(requirements.properties)
        takes_parameters = self.takes(requirements.known_parameters.keys())
        has_capabilities = self.can(requirements.capabilities, aliases)
        return isnt_factory and has_properties and takes_parameters and has_capabilities

    def has(self, attributes):
        return all([x in self._properties for x in attributes])

    def takes(self, parameters):
        return all([p in self._dependencies for p in parameters])

    def can(self, target_capabilities, aliases):
        for target_capability in target_capabilities.items():
            action = target_capability[0]
            taking = target_capability[1][0]
            returning = target_capability[1][1]
            if action in aliases:
                possible_actions = aliases[action]
                if not any([self.can_do_action(a,taking,returning) for a in possible_actions]):
                    return False
            else:
                if not self.can_do_action(action, taking, returning):
                    return False
        return True

    def can_do_action(self, action, taking, returning):
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
        self._aliases = {}
        self._patterns = []
        for c in constructors:
            if hasattr(c, '__call__'):
                class MustWrap:
                    def __init__(self):
                        pass
                setattr(MustWrap, c.__name__, c)
                self._patterns.append(ClassPattern(MustWrap))
            else:
                self._patterns.append(ClassPattern(c))
                self._patterns.append(FactoryPattern(c))

    def create_with_namehint(self, name_hint, requirements):
        possibilities = filter(lambda x: x.matches(requirements, self._aliases), self._patterns)
        assert len(possibilities) is 1, self._get_error_msg(name_hint, str(requirements), len(possibilities))
        return possibilities[0].create(self, self._aliases, requirements.known_parameters)

    def create(self, requirements):
        if isinstance(requirements, Plastic):
            return self.create_with_namehint('Object created from specification', requirements)
        elif isinstance(requirements, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p._constructor == requirements:
                    return p.create(self, self._aliases, {})
        raise Exception("Can't create object from unknown specficiation: "+str(requirements)+(" (%s)" % type(requirements)))

    def mock_dependencies(self, desired_pattern, function_name):
        if isinstance(desired_pattern, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p._constructor == desired_pattern:
                    return p.mock_dependencies(function_name)
        raise Exception("Unable to mock dependencies for %s.%s" % (str(desired_pattern), function_name))

    def alias(self, **aliases):
        for item in aliases.items():
            if item[0] in self._aliases:
                pool = self._aliases[item[0]]
                # Assume item[0] is in the pool
                if not item[1] in pool:
                    pool.append(item[1])
                    self._aliases[item[1]] = pool
            elif item[1] in self._aliases:
                pool = self._aliases[item[1]]
                # Assume item[1] is in the pool
                if not item[0] in pool:
                    pool.append(item[0])
                    self._aliases[item[0]] = pool
            else:
                new_synonym_pool = list(item)
                self._aliases[item[0]] = new_synonym_pool
                self._aliases[item[1]] = new_synonym_pool

    def _get_error_msg(self, name_hint, requirements_string, num_possibilities):
        # print "Patterns:"
        # for x in self._patterns:
        #    print '\t'+str(x)
        if num_possibilities is 0:
            return name_hint+' '+requirements_string+"; couldn't find any matches."
        elif num_possibilities is 1:
            return "WTF! Invalid error!"
        else:
            return name_hint+' '+requirements_string+"; found "+str(num_possibilities)+" matches!"
