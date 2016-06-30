import inspect
from mock import MagicMock
from plastic import Plastic
from util import must_be_checkable
from cant_find_dependency import CantFindDependency
from primitive_musts import SafeObject


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


def must_handle_synonyms(obj, synonym_dict):
    for member in inspect.getmembers(obj):
        m_name, m_val = member
        if callable(m_val) and not m_name.startswith('_') and m_name in synonym_dict:
            for alias in synonym_dict[m_name]:
                if not hasattr(obj, alias):
                    setattr(obj, alias, m_val)


class ParameterSignature:
    '''WRITEME'''
    def __init__(self, param_name):
        self.name = param_name
        self.requirements = Plastic()

    def __str__(self):
        return self.name+' that '+str(self.requirements)

    def get_param_mold(self):
        return self.requirements

    def mock(self):
        result = MagicMock(spec=[m[0] for m in inspect.getmembers(self.requirements)])
        _mock_must_return_itself_for_must_calls(result)
        return result


class FunctionSignature:
    '''WRITEME'''
    def __init__(self, f, owner_obj=None, ignore_warnings=False):
        self.function = f
        self.name = f.__name__
        self.args, self.varargs, self.keywords, self.defaults = inspect.getargspec(f.__init__ if inspect.isclass(f) else f)
        self.is_method = self.args[0] == 'self' and owner_obj is not None
        self.is_constructor = self.args[0] == 'self' and owner_obj is None
        if self.args[0] == 'self':
            self.args = self.args[1:]  # Shave off 'self'
        self.param_signatures = [ParameterSignature(x) for x in self.args]
        self.returns = None
        self.has_explicit_return_value = False
        if self.is_method:
            def note_return(*x):
                if len(x) == 1:
                    x = x[0]
                self.has_explicit_return_value = True
                self.returns = x
                if type(x) is tuple:
                    self.returns = map(Plastic, x)
                elif type(x) is str:
                    self.returns = Plastic(x)
                return self.returns
            owner_obj.must_return = note_return
        try:
            self.mold_result = f(*[p.get_param_mold() for p in self.param_signatures])
        except Exception as ex:
            if self.has_explicit_return_value is False and not ignore_warnings:
                # TODO: Provide better user notification and details on failure
                self.mold_result = ex
                print 'I MUST WARN YOU: ' + str(ex)
                print 'Warning in ' + str(self)
                print ''
        if self.is_method:
            del owner_obj.must_return
        if self.returns is None:
            self.returns = self.name if inspect.isclass(f) else None

    def get_default(self, index):
        if self.defaults is None:
            return None
        index += len(self.defaults) - len(self.args)
        if index >= 0:
            return self.defaults[index]
        else:
            return None

    def mock_params(self):
        return [x.mock() for x in self.param_signatures]

    def _return_str(self):
        if self.has_explicit_return_value:
            return str(self.returns)
        else:
            return '???'

    def __str__(self):
        arg_headers = [str(p) for p in self.param_signatures]
        for i in range(len(self.args)):
            if self.get_default(i) is not None:
                arg_headers[i] += ' (default='+str(self.get_default(i))+')'
        if len(arg_headers) < 2:
            return self.name+"("+','.join(arg_headers)+") -> "+self._return_str()
        return self.name+"(\n\t"+',\n\t'.join(arg_headers)+"\n) -> "+self._return_str()


class ClassPattern:
    ''' WRITEME '''
    def __init__(self, constructor, ignore_warnings=False):
        self._constructor = FunctionSignature(constructor, ignore_warnings=ignore_warnings)
        self._properties = []
        self._capabilities = {}

        obj = self._constructor.mold_result
        members = filter(lambda x: not x[0].startswith('_'), inspect.getmembers(obj))
        for m in members:
            m_name, m_val = m
            if callable(m_val):
                self._capabilities[m_name] = FunctionSignature(m_val, obj, ignore_warnings=ignore_warnings)
            else:
                self._properties.append(m_name)

    def reflects_class(self, possible_class):
        return possible_class == self._constructor.function

    def describe(self, member_name=None):
        if member_name is None:
            members = self.describe('__init__')+"\n"
            for c in self._capabilities:
                members += self.describe(c)+"\n"
            return ("\n%s:\n\t" % self._constructor.name) + members.replace("\n","\n\t")

        if member_name == "__init__":
            return str(self._constructor)
        elif member_name in self._capabilities:
            return str(self._capabilities[member_name])
        raise NotImplementedError  # TODO

    def mock_dependencies(self, method_name):
        if method_name == "__init__":
            return self._constructor.mock_params()
        raise NotImplementedError  # TODO

    def create(self, universe, aliases, known_parameters):
        params = {}
        for i in range(len(self._constructor.args)):
            arg_name = self._constructor.args[i]
            if arg_name in known_parameters:
                params[arg_name] = known_parameters[arg_name]
                must_be_checkable(params[arg_name])
            else:
                try:
                    namehint = str(self._constructor.function)+' needs '+('an' if arg_name[0] in 'aeiou' else 'a')+' "'+arg_name+'" that'
                    params[arg_name] = universe.create_with_namehint(namehint, self._constructor.param_signatures[i].get_param_mold())
                except CantFindDependency as ex:
                    default = self._constructor.get_default(i)
                    if default is not None:
                        params[arg_name] = default
                    else:
                        raise ex
        result = self._constructor.function(**params)
        must_handle_synonyms(result, aliases)
        must_be_checkable(result)
        result.must_return = lambda *x: SafeObject()
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
        return all([p in self._constructor.args for p in parameters])

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
        if action in self._capabilities:
            numberOfArgsTaken = 0 if len(taking) is 0 else taking.count(',')+1  # TODO: This is bad and should feel bad.
            numberOfArgsProvided = len(self._capabilities[action].args)
            sameNumberOfArgs = numberOfArgsTaken == numberOfArgsProvided
            if sameNumberOfArgs:
                if returning and self._capabilities[action].returns:
                    if isinstance(self._capabilities[action].returns, type):
                        return self._capabilities[action].returns == returning
                    else:
                        if type(self._capabilities[action].returns) is list:
                            # TODO: THIS IS A BAD CHECK
                            return len(self._capabilities[action].returns) == returning.count(',')+1
                        else:
                            return self._capabilities[action].returns.matches(returning, aliases)
                return True
            return False
        return False

    def __str__(self):
        result = str(self._constructor.function)
        if len(self._properties) > 0:
            result += " has "+', '.join(self._properties)
        if len(self._capabilities) > 0:
            result += " and can " if len(self._properties) > 0 else " can "
            result += ', '.join(self._capabilities.keys())
        return result
