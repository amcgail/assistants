from ..common import *

import traceback

# compile all Module classes from files in this directory
py_files = Path(__file__).parent.glob("*.py")
modules = {}
for py_file in py_files:
    if py_file.name == "__init__.py":
        continue
    if py_file.name == "planner.py":
        continue
    if py_file.name == "new_module_template.py":
        continue

    module_name = py_file.stem
    module = importlib.import_module(f".{module_name}", __package__)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Module) and not issubclass(obj, SubModule) and obj is not Module:
            modules[module_name + '.' + name] = obj

# compile a meta-prompt to describe the modules
meta_prompt = []
for name, module in modules.items():
    meta_prompt.append(f"{name}:{module.goal}")

meta_prompt = "\n".join(meta_prompt)

class Plan(Module):
    name = 'planner'
    goal = "to plan out how other modules should interact with each other to accomplish a goal."

    detailed_instructions = f"The following are the only modules available:\n{meta_prompt}"
    params = """
        [
            {
                'name': 'name of the module',
                'goal': 'a detailed textual description of the goal you want to give to the module',
            },
            ...
        ]
    """

    def execute_it(self, args):
        # args is a list of dicts
        # each dict has a 'name' and 'goal' key
        # we need to find the corresponding module and call its contemplate method
        responses = []
        for arg in args:
            name = arg['name']
            goal = arg['goal']
            if name not in modules:
                responses.append(f"Module {name} not found.")
                continue

            module = modules[name]()
            result = module.contemplate(goal)

            responses.append(result)

        return "\n".join(str(x) for x in responses)
    
p = Plan()
#print(p.contemplate("Negotiate with Patrick and Mom to decide where to go for dinner."))
#print(p.contemplate("Can you create a new module that will go get the current value of a given stock ticker?"))
#print(p.contemplate("What is the current price of AAPL?"))
#print(p.contemplate("Write a new module in the namespace 'writer' which summarizes long text."))
print(p.contemplate("Write a long-ish essay about how the singularity is basically here, based on your (an LLM) ability to divide up writing the essay into logical sub-parts, ability to debug. But also be imaginative and reference as many sci-fi novels as possible."))