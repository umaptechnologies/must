import inspect
from class_pattern import ClassPattern


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
        for i in range(len(self._constructor_args)):
            a = self._constructor_args[i]
            if a in self._factory_header:
                dependencies.append(args[arg_index])
                arg_index += 1
            else:
                namehint = str(self._obj_constructor)+' needs '+('an' if a[0] in 'aeiou' else 'a')+' "'+a+'" that'
                dependencies.append(self._universe.create_with_namehint(namehint, self._product_pattern._constructor.param_signatures[i].get_param_mold()))
        # TODO: Incorporate self._known_parameters
        return self._obj_constructor(*dependencies)

    def must_make(self, obj_type, parameters):
        new_factory_header = parameters.split(', ')
        assert self._factory_header == self._constructor_args or new_factory_header == self._factory_header, "Factory parameters cannot be %s; already specified as %s." % (new_factory_header, self._factory_header)
        self._factory_header = new_factory_header
        return self

    def that_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)

    def and_must_make(self, obj_type, parameters):
        return self.must_make(obj_type, parameters)

    def must(self, action, taking='', returning=''):
        return self

    def must_have(self, *attributes):
        return self

    def must_use(self, **known_parameters):
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


class FactoryPattern:
    ''' WRITEME '''
    def __init__(self, constructor):
        self._constructor = constructor
        self._constructor_args = inspect.getargspec(constructor.__init__).args[1:]  # Ignore 'self'
        self._product = ClassPattern(constructor)

    def reflects_class(self, possible_class):
        return False

    def create(self, universe, aliases, known_parameters):
        return Factory(self._constructor, self._constructor_args, self._product, universe, known_parameters)

    def matches(self, requirements, aliases):
        is_factory = requirements.type == 'factory'
        has_parameters = self.has_parameters(requirements.parameters)
        product_matches = (requirements.product is None) or \
                          (self._product.matches(requirements.product, aliases))
        return is_factory and has_parameters and product_matches

    def has_parameters(self, parameters):
        return all([x in self._constructor_args for x in parameters])

    def __str__(self):
        result = str(self._constructor)+" factory("
        result += ', '.join(self._constructor_args)
        result += ")"
        return result
