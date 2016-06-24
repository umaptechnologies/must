import inspect
import types
from details.plastic import Plastic
from details.factories import FactoryPattern
from details.class_pattern import ClassPattern
from details.cant_find_dependency import CantFindDependency
from details.primitive_musts import must_be_string
from details.primitive_musts import must_be_natural_number
from details.primitive_musts import must_list_objects

must_be_something = Plastic  # This is an alias for importing.
_ = (
    must_be_string,
    must_be_natural_number,
    must_list_objects,
)  # Just to get the linter to shut up


class MustOutputToStdOut:
    ''' Wrapper for the "print" statement. '''
    def __init__(self):
        pass

    def output(self, text):
        text = must_be_string(text)
        self.must_return(None)
        print text


class MustHavePatterns:
    ''' Nothing to see here... '''
    def __init__(self, *constructors):
        self._aliases = {}
        self._patterns = []
        self.add_all(constructors)

    def add(self, constructor, ignore_warnings=False):
        self.add_all([constructor], ignore_warnings)

    def add_all(self, constructors, ignore_warnings=False):
        for c in constructors:
            if hasattr(c, '__call__'):
                class MustWrap:
                    def __init__(self):
                        pass
                setattr(MustWrap, c.__name__, c)
                self._patterns.append(ClassPattern(MustWrap, ignore_warnings))
            elif inspect.isclass(c):
                self._patterns.append(ClassPattern(c, ignore_warnings))
                self._patterns.append(FactoryPattern(c, ignore_warnings))
            else:
                raise TypeError('Must cannot handle %s because it is of %s.' % (str(c), type(c)))

    def create_with_namehint(self, name_hint, requirements):
        possibilities = filter(lambda x: x.matches(requirements, self._aliases), self._patterns)
        if len(possibilities) is not 1:
            raise CantFindDependency(name_hint, requirements, possibilities)
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
                if p.reflects_class(requirements):
                    return p.create(self, self._aliases, known_parameters)
        raise Exception("Can't create object from unknown specficiation: "+str(requirements)+(" (%s)" % type(requirements)))

    def mock_dependencies(self, desired_pattern, function_name='__init__'):
        if isinstance(desired_pattern, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p.reflects_class(desired_pattern):
                    return p.mock_dependencies(function_name)
        raise Exception("Unable to mock dependencies for %s.%s" % (str(desired_pattern), function_name))

    def describe(self, desired_pattern):
        if isinstance(desired_pattern, (types.TypeType, types.ClassType)):
            for p in self._patterns:
                if p.reflects_class(desired_pattern):
                    return p.describe()
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

    def __str__(self):
        return "MustHavePatterns(n=%d)" % len(self._patterns)
