import inspect
import types
from details.plastic import Plastic
from details.factories import FactoryPattern
from details.class_pattern import ClassPattern
from details.util import must_be_checkable

must_be_something = Plastic  # This is an alias for importing.


class MustOutputToStdOut:
    ''' Wrapper for the "print" statement. '''
    def __init__(self):
        pass

    def output(self, text):
        print text


class SafeObject:
    ''' Never fails a must. '''
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
            elif inspect.isclass(c):
                self._patterns.append(ClassPattern(c))
                self._patterns.append(FactoryPattern(c))
            else:
                raise TypeError('Must cannot handle %s because it is of %s.' % (str(c), type(c)))

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
                    members = p.describe('__init__')+"\n"
                    for c in p._capabilities:
                        members += p.describe(c)+"\n"
                    return ("\n%s:\n\t" % p._constructor) + members.replace("\n","\n\t")
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
