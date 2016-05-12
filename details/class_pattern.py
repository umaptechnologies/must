import inspect
from mock import MagicMock
from plastic import Plastic
from util import must_be_checkable


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


def describe_function(name, argnames, arg_requirements, returns):
    arg_headers = [argnames[i]+' that '+str(arg_requirements[i]) for i in range(len(argnames))]
    if len(arg_headers) < 2:
        return name+"("+','.join(arg_headers)+") -> "+str(returns)
    return name+"(\n\t"+',\n\t'.join(arg_headers)+"\n) -> "+str(returns)


def must_handle_synonyms(obj, synonym_dict):
    for member in inspect.getmembers(obj):
        m_name, m_val = member
        if callable(m_val) and not m_name.startswith('_') and m_name in synonym_dict:
            for alias in synonym_dict[m_name]:
                if not hasattr(obj, alias):
                    setattr(obj, alias, m_val)


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
            return describe_function(member_name, self._constructor_args, self._ordered_dependencies, self._constructor)
        elif member_name in self._capabilities:
            return describe_function(member_name, self._capabilities[member_name], range(len(self._capabilities[member_name])), '???')  # TODO: FLESH ME OUT!
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
        right_type = requirements.type is None or requirements.type == 'object'
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
