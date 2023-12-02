from .common import *

modules = {}
def load_modules_from(directory_name):

    if type(directory_name) == dict:
        for name, obj in directory_name.items():
            if inspect.isclass(obj) and issubclass(obj, Module) and not issubclass(obj, SubModule) and obj is not Module:
                modules['local.' + name] = obj
    
    elif type(directory_name) == str:
        from importlib.machinery import SourceFileLoader
        
        # compile all Module classes from files in this directory
        directory = Path(directory_name)
        py_files = directory.glob("*.py")
        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue
            if py_file.name == "new_module_template.py":
                continue
            if py_file.name == "planner.py":
                continue

            module_name = py_file.stem

            loader = SourceFileLoader(module_name, str(py_file))
            module = loader.load_module()

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Module) and not issubclass(obj, SubModule) and obj is not Module:
                    modules[module_name + '.' + name] = obj

# odd self-referential code.
# I love it
from .mods.planner import Plan
modules['planner.Plan'] = Plan

# load this (package) directory's modules
load_modules_from( Path(__file__).parent / 'modules' )