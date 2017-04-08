import importlib

class DummyModule(object):

    def __init__(self, error):
        self._error = error

    def _raise(self):
        raise self._error

    def __getattr__(self, name):
        self._raise()

    def __call__(self):
        self._raise()

def maybe_import_module(name, package=None):
    try:
        return importlib.import_module(name, package)
    except ModuleNotFoundError as error:
        return DummyModule(error)

def maybe_load_base(name, base=None):
    base_name, *sub_names = name.split('.')
    if base is None:
        base = maybe_import_module(base_name)
    tmp_name, tmp = base_name, base
    for sub_name in sub_names:
        if isinstance(tmp, DummyModule):
            return base
        sub = maybe_import_module('.' + sub_name, tmp_name)
        setattr(tmp, sub_name, sub)
        tmp_name += '.' + sub_name
        tmp = getattr(tmp, sub_name)
    return base

def maybe_load_from(name, import_list=[]):
    module_names = map(lambda x: '{}.{}'.format(name, x), import_list)
    modules = map(maybe_import_module, module_names)
    return tuple(modules)

def maybe_load(name, base=None, import_list=[]):
    if import_list:
        return maybe_load_from(name=name, import_list=import_list)
    else:
        return maybe_load_base(name=name, base=base)
