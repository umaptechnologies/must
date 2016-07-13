import inspect
from details.plastic import Plastic
from details.factories import FactoryPattern
from details.class_pattern import ClassPattern
from details.cant_find_dependency import CantFindDependency
from details.primitive_musts import must_be_string
from details.primitive_musts import must_be_natural_number
from details.primitive_musts import must_be_real_number
from details.primitive_musts import must_list_objects
from details.standard_patterns import MustOutputToStdOut

must_be_something = Plastic  # This is an alias for importing.
_ = (
    must_be_string,
    must_be_natural_number,
    must_be_real_number,
    must_list_objects,
    MustOutputToStdOut,
)  # Just to get the linter to shut up


def _function_to_class(f):
    class MustWrap(object):
        def __init__(self):
            pass
    setattr(MustWrap, f.__name__, f)
    return MustWrap


class MustHavePatterns(object):
    ''' Nothing to see here... '''
    def __init__(self, *constructors):
        self._aliases = {}
        self._patterns = []
        self.add_all(constructors)

    def _collect_known_parameters(self, kwargs):
        results = {}
        for key in kwargs.keys():
            if key.startswith('with_'):
                results[key[5:]] = kwargs.get(key)
            else:
                raise KeyError('Unknown creation parameter "%s"' % key)
        return results

    def _get_patterns(self, desired_pattern):
        if inspect.isclass(desired_pattern):
            return [p for p in self._patterns if p.reflects_class(desired_pattern)]
        elif hasattr(desired_pattern, '__call__'):
            # TODO: This is ugly. Clean it up!
            name = desired_pattern.__name__
            args, varargs, keywords, defaults = inspect.getargspec(desired_pattern)
            if len(args) > 0 and args[0] == 'self':
                args = args[1:]
            plastic = Plastic().that_must(name, ', '.join(args))
            return [p for p in self._patterns if p.matches(plastic, {})]
        raise Exception("Can't handle patterns of type: %s" % type(desired_pattern))

    def add(self, new_pattern, ignore_warnings=False):
        self.add_all([new_pattern], ignore_warnings)

    def add_all(self, new_patterns, ignore_warnings=False):
        for p in new_patterns:
            if inspect.isclass(p):
                self._patterns.append(ClassPattern(p, ignore_warnings=ignore_warnings))
                self._patterns.append(FactoryPattern(p, ignore_warnings=ignore_warnings))
            elif hasattr(p, '__call__'):
                self._patterns.append(ClassPattern(_function_to_class(p), is_function_wrapper=True, ignore_warnings=ignore_warnings))
            else:
                raise TypeError('Must cannot handle %s because it is of %s.' % (str(p), type(p)))

    def create_with_namehint(self, name_hint, requirements, **kwargs):
        known_parameters = self._collect_known_parameters(kwargs)
        if isinstance(requirements, Plastic):
            known_parameters.update(requirements.known_parameters)
            possibilities = filter(lambda x: x.matches(requirements, self._aliases), self._patterns)
        else:
            possibilities = self._get_patterns(requirements)
        if len(possibilities) is not 1:
            raise CantFindDependency(name_hint, requirements, possibilities)
        return possibilities[0].create(self, self._aliases, known_parameters)

    def create(self, requirements, **kwargs):
        if isinstance(requirements, Plastic):
            return self.create_with_namehint('Object created from specification', requirements, **kwargs)
        return self.create_with_namehint(str(requirements), requirements, **kwargs)

    def mock_dependencies(self, desired_pattern, function_name='__init__'):
        return self._get_patterns(desired_pattern)[0].mock_dependencies(function_name)

    def describe(self, desired_pattern):
        return self._get_patterns(desired_pattern)[0].describe()

    def describe_all(self):
        return ''.join([p.describe() for p in self._patterns if isinstance(p, ClassPattern)])

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
