from ..common import *

from abc import ABC, abstractmethod

class Module:
    def get_prompt(self, meta_goal=None):
        if meta_goal is None:
            meta_goal = "improve Alec's life"
        p = flatten_whitespace(f"""
            You are a component of Alec McGail's helpful AI assistant, named the "{self.name}".
            The date and time right now is {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.
            Ultimately you are helping to "{meta_goal}"

            You have been specifically tasked with the goal: "{self.goal}".
            
            Your response must be JSON-formatted.
            Always use double-quotes for keys and values.
            Lists CANNOT end in a comma.

            Your output must be defined according to the following template:\n{indent(flatten_whitespace(self.params), 14)}
        """)

        if hasattr(self, "detailed_instructions"):
            p += "\n\n" + flatten_whitespace(self.detailed_instructions) + "\n\n"

        return p
    
    def contemplate(self, query, meta_goal=None):
        prompt = self.get_prompt(meta_goal)

        # get the name of the file where the subclass is defined
        subclass_file = inspect.getfile(self.__class__)
        subclass_file = Path(subclass_file).stem

        print('\n\n***** ', type(self).__name__, 'in the', subclass_file, 'file ******\n\n')

        print( '--------- PROMPT ---------' )
        print(prompt)
        print( '--------- QUERY ----------')
        print(query)

        response = oai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [{
                "role": "system",
                "content": prompt
            }, {
                "role": "user",
                "content": f"Query:\n{query}"
            }]
        )
        response = response.choices[0].message.content
        print( '--------- RESPONSE -------')
        print(response)

        # some need to be decoded twice
        for i in range(2):
            try:
                response = json.loads(response)
            except:
                pass
        

        import traceback
        failed = False
        try:
            result = self.execute_it(response)
        except Exception as e:
            raise e
            if type(e) in {KeyboardInterrupt, SystemExit}:
                raise e
            
            failed = True
            info = traceback.format_exc()
        
        if not failed and result is None:
            failed = True
            info = f"Result was None."

        if False and failed:
            from .planner import Plan
            
            namespace = Path(self.__module__).stem
            new_goal = f"Module '{type(self).__name__}' in namespace '{namespace}' failed in execute_it function with the input ```{response}```. Here is more info on the error:\n" + indent(indent(info, 3, '-'), 1, ' ')

            new_plan = Plan()
            result = new_plan.contemplate(new_goal)

        return result
    
    @abstractmethod
    def execute_it(self, args):
        pass

class SubModule(Module):
    pass