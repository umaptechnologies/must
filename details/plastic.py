import re
import types


def build_best_guess(taking, returning):
    def new_f(self, *args, **kwargs):
        return returning

    return new_f


class Plastic(object):
    ''' WRITEME '''
    def __init__(self, name=None, parent=None):
        self.name = name
        self.parent = parent  # TODO: This has to do with lists of plastic or something. Idk. Needs to be figured out.
        self.type = None  # This becomes a string as soon as a requirement is specified
        self.properties = []
        self.capabilities = {}
        self.parameters = []
        self.known_parameters = {}
        self.product = None  # Only applies in the case of factories

    def _make_type_err_str(self, desired_type):
        t = str(self.type)
        dt = str(desired_type)
        return ('Thing' if self.name is None else '"'+self.name+'"')+" (that "+str(self)+") is "+("an " if t[0] in 'aeuio' else "a ")+t+", but must be "+("an " if dt[0] in 'aeuio' else "a ")+dt+"!"

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

    def matches(self, requirements, aliases):
        # TODO: This is mirrored in class_pattern. Figure out a way to fuse them.
        if self.type is not None and self.type != 'object':
            return self.type_matches(requirements)
        right_type = requirements.type is None or requirements.type == self.type
        has_properties = self.has(requirements.properties)
        has_capabilities = self.can(requirements.capabilities, aliases)
        return right_type and has_properties and has_capabilities

    def type_matches(self, other):
        if self.type == 'real number':
            return type(other) is float or type(other) is int
        else:
            raise NotImplementedError("Must doesn't know how to check type of: "+str(self.type))

    def has(self, attributes):
        return all([x in self.properties for x in attributes])

    def can(self, target_capabilities, aliases):
        for target_capability in target_capabilities.items():
            action = target_capability[0]
            taking = target_capability[1][0]
            returning = target_capability[1][1]
            if action in aliases:
                possible_actions = aliases[action]
                if not any([self.can_do_action(a,taking,returning,aliases) for a in possible_actions]):
                    return False
            else:
                if not self.can_do_action(action, taking, returning, aliases):
                    return False
        return True

    def can_do_action(self, action, taking, returning, aliases):
        if action in self.capabilities:
            numberOfArgsTaken = 0 if len(taking) is 0 else taking.count(',')+1  # TODO: This is bad and should feel bad.
            numberOfArgsProvided = len(self.capabilities[action].args)
            sameNumberOfArgs = numberOfArgsTaken == numberOfArgsProvided
            if sameNumberOfArgs:
                if returning and self.capabilities[action].returns:
                    return self.capabilities[action].returns.matches(returning, aliases)
                return True
            return False
        return False

    def __str__(self):
        result = ''
        if self.name is not None:
            result += '"'+self.name+'" that '
        result += 'must'
        if self.type is None:
            if self.name is not None:
                return '"'+self.name+'" (could be anything)'
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
                if len(self.capabilities) > 1:
                    result += " be able to "+', '.join(self.capabilities.keys())
                else:
                    result += " be able to "+self._describe_capability(0)
            if len(self.known_parameters) > 0:
                result += " and" if result != 'must' else ""
                result += " be created with "+', '.join(self.known_parameters.keys())
        return result

    def _return_str(self, capability):
        result = str(capability[1])
        if result == '':
            return '??'
        return result

    def _describe_capability(self, index):
        return self.capabilities.keys()[index]+'('+self.capabilities.values()[index][0]+') -> '+self._return_str(self.capabilities.values()[index])
