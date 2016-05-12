import re
import types


def build_best_guess(taking, returning):
    def new_f(self, *args, **kwargs):
        return returning

    return new_f


class Plastic:
    ''' WRITEME '''
    def __init__(self):
        self.type = None  # This becomes a string as soon as a requirement is specified
        self.properties = []
        self.capabilities = {}
        self.parameters = []
        self.known_parameters = {}
        self.product = None  # Only applies in the case of factories

    def _make_type_err_str(self, desired_type):
        t = str(self.type)
        dt = str(desired_type)
        return "Thing (that "+str(self)+") is "+("an " if t[0] in 'aeuio' else "a ")+t+", but must be "+("an " if dt[0] in 'aeuio' else "a ")+dt+"!"

    def must_be_type(self, desired_type):
        assert isinstance(desired_type, str)
        assert self.type is None or self.type == desired_type, self._make_type_err_str(desired_type)
        self.type = desired_type
        return self

    def must_be_primitive(self, primitive_type):
        return self.must_be_type(primitive_type)

    def must(self, action, taking='', returning=''):
        if self.type == 'factory' and self.product is not None:
            self.product.must(action, taking, returning)
            return self
        self.must_be_type('object')
        self.capabilities[action] = [taking,returning]
        setattr(self, action, types.MethodType(build_best_guess(taking, returning), self))
        return self

    def must_have(self, *attributes):
        if self.type == 'factory' and self.product is not None:
            self.product.must_have(*attributes)
            return self
        self.must_be_type('object')
        self.properties.extend(attributes)
        return self

    def must_use(self, **known_parameters):
        if self.type == 'factory' and self.product is not None:
            self.product.must_use(**known_parameters)
            return self
        self.must_be_type('object')
        self.known_parameters.update(known_parameters)
        return self

    def must_make(self, obj_type, parameters):
        self.must_be_type('factory')
        self.parameters = re.split('\s*,\s*',parameters)
        setattr(self, 'make', types.MethodType(build_best_guess(parameters, obj_type), self))
        self.product = Plastic()
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
        if self.type is None:
            return 'could be anything'
        if self.type == 'factory':
            result += " be a factory ("+', '.join(self.parameters)+")"
            if self.product is not None:
                result += ' producing things that '+str(self.product)
        elif self.type != 'object':
            result += " be "+("an " if self.type[0] in 'aeiou' else "a ")+self.type
        else:
            if len(self.properties) > 0:
                result += " have "+', '.join(self.properties)
            if len(self.capabilities) > 0:
                result += ("," if len(self.known_parameters) > 0 else " and") if result != 'must' else ""
                result += " be able to "+', '.join(self.capabilities.keys())
            if len(self.known_parameters) > 0:
                result += " and" if result != 'must' else ""
                result += " be created with "+', '.join(self.known_parameters.keys())
        return result
