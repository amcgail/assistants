from ..common import *

import traceback

# compile all Module classes from files in this directory
py_files = Path(__file__).parent.glob("*.py")
modules = {}
for py_file in py_files:
    if py_file.name == "__init__.py":
        continue
    if py_file.name == "new_module_template.py":
        continue
    if py_file.name == "planner.py":
        continue

    module_name = py_file.stem
    module = importlib.import_module(f".{module_name}", __package__)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Module) and not issubclass(obj, SubModule) and obj is not Module:
            modules[module_name + '.' + name] = obj

class Plan(Module):
    name = 'planner'
    goal = "to organize any multi-step task into a series of sub-tasks, and then execute them in order."

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
        goals = []
        responses = []
        for arg in args:
            name = arg['name']
            goal = arg['goal']
            if name not in modules:
                responses.append(f"Module {name} not found.")
                continue

            prompt = ""

            prior = []
            for g, r in zip(goals, responses):
                r = r.strip('\n')
                if len(r.split('\n')) > 1:
                    r = indent(r, 1, ' ')
                    prior.append(f"{g}:\n{r}")
                else:
                    prior.append(f"{g}: {r}")

            if len(prior):

                prior = "\n".join(prior)
                prior = indent( indent(prior, 2) , 3, '.')
                prompt += f"/// prior goals and their results: ///\n{prior}"

            prompt += "\n\n"
            prompt += f"/// current goal: ///\n{goal}"

            module = modules[name]()
            result = module.contemplate(prompt, goal)

            goals.append(goal)
            responses.append(result)

        return "\n".join(str(x) for x in responses)
    
# odd self-referential code.
# I love it
modules['planner.Plan'] = Plan

# compile a meta-prompt to describe the modules
meta_prompt = []
for name, module in modules.items():
    meta_prompt.append(f"{name}: {module.goal}")

meta_prompt = "\n".join(meta_prompt)

detailed_instructions = f"""
Please be as specific as possible in your description of the goal of each sub-module.
Each goal will have access to the results of previous goals.

This can also be useful to split a very large task into smaller sub-goals.

The following are the names and descriptions of the only modules available:\n{indent(meta_prompt, 2, ' ')}

Use planning.Plan to plan further planning, once the prior modules have been completed.
For instance, to duplicate tasks from one day to another, 
    you would use calenderer.Search to query first for the tasks on the first day, 
    and then planning.Plan to plan the creation of those tasks on the second day.
"""

if __name__ == "__main__":
    # add detailed_instructions as a class attribute to Plan
    Plan.detailed_instructions = detailed_instructions

    p = Plan()
    #print(p.contemplate("Negotiate with Patrick and Mom to decide where to go for dinner."))
    #print(p.contemplate("Can you create a new module that will go get the current value of a given stock ticker?"))
    #print(p.contemplate("What is the current price of AAPL?"))
    #print(p.contemplate("Write a new module in the namespace 'writer' which summarizes long text."))
    #print(p.contemplate("Write a long-ish essay about how the singularity is basically here, based on your (an LLM) ability to divide up writing the essay into logical sub-parts, ability to debug. But also be imaginative and reference as many sci-fi novels as possible."))
    #print(p.contemplate("Make a schedule for Alec for tomorrow. It should include a meeting with Patrick at 930am, at least 4 hours of \"collectivity research,\" and at least 4 hours of \"chatbot research\". 2 hour chunks, with breaks, seems right. And approximate Lunch and Dinner breaks. Make a meeting for getting up and eating breakfast, too."))
    #print(p.contemplate("Check the schedule tomorrow and add a 20 minute event to call Mama Mireille. And one to call Dad. I also want a short 30m workout in the morning."))
    print(p.contemplate("Could you duplicate all the main tasks of my schedule from monday to tuesday? But please switch the positions of chatbot research and collectivity research."))