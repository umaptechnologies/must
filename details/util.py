import types


def must_be_checkable(obj):
    if type(obj) in (int, bool, str):
        return

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
