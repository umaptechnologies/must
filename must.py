import inspect
import types
from mock import MagicMock
from plastic import Plastic


def _mock_must_return_itself_for_must_calls(mock):
    mock.must_be_type.return_value = mock
    mock.must_be_primitive = mock
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


class MustOutputToStdOut:
    ''' Wrapper for the "print" statement. '''
    def __init__(self):
        pass

    def output(self, text):
        print text


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
    if type(obj) in (int, bool, str):
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
    if isinstance(possible_list, Plastic):
        possible_list.must_be_primitive('list')
        return Plastic(parent=possible_list)
    assert isinstance(possible_list, list), "%s must be a list!" % str(possible_list)
    if len(possible_list) > 0:
        return must_be_checkable(possible_list[0])
    else:
        return SafeObject()


def must_be_string(possible_string, example=""):
    if isinstance(possible_string, Plastic):
        possible_string.must_be_primitive('string')
        return example
    assert isinstance(possible_string, str), "%s must be a string!" % str(possible_string)
    return possible_string


def must_be_natural_number(possible_natural_number, example=0):
    if isinstance(possible_natural_number, Plastic):
        possible_natural_number.must_be_primitive('natural number')
        return example
    assert isinstance(possible_natural_number, int), "%s must be an integer (because it's supposed to be a natural number)!" % str(possible_natural_number)
    assert possible_natural_number >= 0, "%s must be non-negative (because it's supposed to be a natural number)!" % str(possible_natural_number)
    return possible_natural_number


class Factory:
    ''' WRITEME '''
    def __init__(self, obj_constructor, constructor_args, product_pattern, universe, known_parameters):
        self._obj_constructor = obj_constructor
        self._constructor_args = constructor_args
        self._factory_header = constructor_args
        self._product_pattern = product_pattern
        self._universe = universe
        self._known_parameters = known_parameters

    def make(self, *args):
        arg_index = 0
        dependencies = []
        for a in self._constructor_args:
            if a in self._factory_header:
                dependencies.append(args[arg_index])
                arg_index += 1
            else:
                namehint = str(self._obj_constructor)+' needs '+('an' if a[0] in 'aeiou' else 'a')+' "'+a+'" that'
                dependencies.append(self._universe.create_with_namehint(namehint, self._product_pattern._dependencies[a]))
        # TODO: Incorporate self._known_parameters
        return self._obj_constructor(*dependencies)

    def must_make(self, obj_type, parameters):
        new_factory_header = parameters.split(', ')
        assert self._factory_header == self._constructor_args or new_factory_header == self._factory_header, "Factory parameters cannot be %s; already specified as %s." % (new_factory_header, self._factory_header)
        self._factory_header = new_factory_header
        return SafeObject()

    def that_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)

    def and_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)


class FactoryPattern:
    ''' WRITEME '''
    def __init__(self, constructor):
        self._constructor = constructor
        self._constructor_args = inspect.getargspec(constructor.__init__).args[1:]  # Ignore 'self'
        self._product = ClassPattern(constructor)

    def create(self, universe, aliases, known_parameters):
        return Factory(self._constructor, self._constructor_args, self._product, universe, known_parameters)

    def matches(self, requirements, aliases):
        is_factory = requirements.type == 'factory'
        has_parameters = self.has_parameters(requirements.parameters)
        product_matches = (requirements.product is None) or (self.product_matches(requirements.product, aliases))
        return is_factory and has_parameters and product_matches

    def has_parameters(self, parameters):
        return all([x in self._constructor_args for x in parameters])

    def product_matches(self, product, aliases):
        return self._product.matches(product, aliases)

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
        obj = constructor(**self._dependencies)  # WARNING: This blows up if the user doesn't must their stuff correctly. TODO: Provide better user notification.
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
            arg_headers = [a+' that '+str(self._dependencies[a]) for a in self._constructor_args]
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
                namehint = str(self._constructor)+' needs '+('an' if arg_name[0] in 'aeiou' else 'a')+' "'+arg_name+'" that'
                params[arg_name] = universe.create_with_namehint(namehint, self._dependencies[arg_name])
        result = self._constructor(**params)
        must_handle_synonyms(result, aliases)
        must_be_checkable(result)
        return result

    def matches(self, requirements, aliases):
        right_type = requirements.type == 'object'
        has_properties = self.has(requirements.properties)
        takes_parameters = self.takes(requirements.known_parameters.keys())
        has_capabilities = self.can(requirements.capabilities, aliases)
        return right_type and has_properties and takes_parameters and has_capabilities

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
        assert len(possibilities) is 1, self._get_error_msg(name_hint, str(requirements), possibilities)
        return possibilities[0].create(self, self._aliases, requirements.known_parameters)

    def create(self, requirements, **kwargs):
        known_parameters = {}
        for key in kwargs.keys():
            if key.startswith('with_'):
                known_parameters[key[5:]] = kwargs.get(key)
            else:
                raise KeyError('Unknown creation parameter "%s"' % key)

        if isinstance(requirements, Plastic):
            # TODO: Meld known_parameters into requirements
            return self.create_with_namehint('Object created from specification', requirements)
        elif isinstance(requirements, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p._constructor == requirements:
                    return p.create(self, self._aliases, known_parameters)
        raise Exception("Can't create object from unknown specficiation: "+str(requirements)+(" (%s)" % type(requirements)))

    def mock_dependencies(self, desired_pattern, function_name='__init__'):
        if isinstance(desired_pattern, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p._constructor == desired_pattern:
                    return p.mock_dependencies(function_name)
        raise Exception("Unable to mock dependencies for %s.%s" % (str(desired_pattern), function_name))

    def describe(self, desired_pattern):
        if isinstance(desired_pattern, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p._constructor == desired_pattern:
                    return p.describe('__init__')  # TODO: Add to me.
        raise Exception("Unable to describe %s" % str(desired_pattern))

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

    def _get_error_msg(self, name_hint, requirements_string, possibilities):
        # print "Patterns:"
        # for x in self._patterns:
        #    print '\t'+str(x)
        num_possibilities = len(possibilities)
        if num_possibilities is 0:
            return name_hint+' '+requirements_string+"; couldn't find any matches."
        elif num_possibilities is 1:
            return "WTF! Invalid error!"
        elif num_possibilities < 5:
            return name_hint+' '+requirements_string+"; too many matches: "+str(map(str, possibilities))
        else:
            return name_hint+' '+requirements_string+"; found "+str(num_possibilities)+" matches!"

    def __str__(self):
        return "MustHavePatterns(n=%d)" % len(self._patterns)
