from modularity import modules, Module
from modularity.common import *

class Plan(Module):
    name = 'planner'
    goal = "to organize any multi-step task into a series of sub-tasks, and then execute them in order."

    params = flatten_whitespace("""
        [
            {
                'name': 'name of the module',
                'goal': 'a detailed textual description of the goal you want to give to the module',
            },
            ...
        ]
    """)

    @property
    def meta_prompt(self):
        # compile a meta-prompt to describe the modules
        mp = []
        for name, module in sorted(self.goals.items()):
            mp.append(f"{name}: {module.goal}")

        mp = "\n".join(mp)
        return mp

    @property
    def detailed_instructions(self):
        module_names = list(self.goals)
        module_names = ", ".join(sorted(module_names))

        return flatten_whitespace(f"""
        If you believe no internal steps need taken to accomplish your goal, you just write text to respond to the user.
        Otherwise, you must provide a list of actions.
        Once all these tasks are completed, you will have the opportunity to respond to the user, or to plan further.

        Please be as specific as possible in your description of the goal of each sub-module.
        Each goal will have access to the results of previous goals.
        This functionality can be used to split a very large task into smaller sub-goals.

        The following are the names and descriptions of the only modules you have available:\n{indent(self.meta_prompt, 10, ' ')}
                                  
        Use planning.Plan to plan further planning.
        All other small tasks should be delegated to the modules you know: {module_names}.
        """)

    def __init__(self, **kwargs):

        goals = kwargs.pop('goals', None)
        if goals is None:
            goals = {}
        self.goals = dict(modules, **goals)

        super().__init__(**kwargs)

    def execute_it(self, args):
        # args is a list of dicts
        # each dict has a 'name' and 'goal' key
        # we need to find the corresponding module and call its contemplate method

        if type(args) == str:
            return args
        elif type(args) != list or len(args) == 0 or type(args[0]) != dict:
            self.add_message('system', "You must provide a list of actions.")
            return self.contemplate()

        goals = []
        responses = []
        for arg in args:
            name = arg['name']
            goal = arg['goal']
            if name not in self.goals:
                responses.append(f"Module {name} not found.")
                continue

            prompt = ""

            prior = []
            for g, r in zip(goals, responses):
                r = str(r)
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

            module = self.goals[name](meta_goal=goal)
            result = module.contemplate(prompt)

            goals.append(goal)
            responses.append(result)

        pprime = self.copy()
        pprime.add_message('system', "Results of Plan:\n" + "\n".join(f"- {str(x)}" for x in responses))
        pprime.add_message('assistant', "Now that I see these results, I'll construct a response to the user, or return further actions which should be taken.")

        result = pprime.generate()

        if type(result) == str:
            return result
        elif type(result) != list or len(result) == 0 or type(result[0]) != dict:
            pprime.add_message('system', "You must provide a list of actions.")
            return pprime.contemplate()
    
if __name__ == "__main__":
    # add detailed_instructions as a class attribute to Plan
    p = Plan()
    #print(p.contemplate("Negotiate with Patrick and Mom to decide where to go for dinner."))
    #print(p.contemplate("Can you create a new module that will go get the current value of a given stock ticker?"))
    #print(p.contemplate("What is the current price of AAPL?"))
    #print(p.contemplate("Write a new module in the namespace 'writer' which summarizes long text."))
    #print(p.contemplate("Write a long-ish essay about how the singularity is basically here, based on your (an LLM) ability to divide up writing the essay into logical sub-parts, ability to debug. But also be imaginative and reference as many sci-fi novels as possible."))
    #print(p.contemplate("Make a schedule for Alec for tomorrow. It should include a meeting with Patrick at 930am, at least 4 hours of \"collectivity research,\" and at least 4 hours of \"chatbot research\". 2 hour chunks, with breaks, seems right. And approximate Lunch and Dinner breaks. Make a meeting for getting up and eating breakfast, too."))
    #print(p.contemplate("Check the schedule tomorrow and add a 20 minute event to call Mama Mireille. And one to call Dad. I also want a short 30m workout in the morning."))
    #print(p.contemplate("Could you duplicate all the main tasks of my schedule from monday to tuesday? But please switch the positions of chatbot research and collectivity research."))
    print(p.contemplate("Write short novel about how the singularity is basically here, based on your (an LLM) ability to divide up writing the essay into logical sub-parts, ability to debug. But also be imaginative and reference as many sci-fi novels as possible. When you're finished, send it to amcgail2@gmail.com"))