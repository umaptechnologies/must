import re
import types


def build_best_guess(taking, returning):
    def new_f(self, *args, **kwargs):
        return returning

    return new_f


class Plastic:
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

    def must(self, action, taking='', returning=''):
        self.must_not_be_factory()
        self.capabilities[action] = [taking,returning]
        setattr(self, action, types.MethodType(build_best_guess(taking, returning), self))
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
