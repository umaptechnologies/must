from util import must_be_checkable
from plastic import Plastic


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


def must_be_integer(possible_integer, example=0):
    if isinstance(possible_integer, Plastic):
        possible_integer.must_be_primitive('integer')
        return example
    assert isinstance(possible_integer, int), "%s must be an integer (because it's supposed to be a natural number)!" % str(possible_integer)
    return possible_integer
