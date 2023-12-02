from abc import ABC, abstractmethod

class Module:
    def __init__(self, debug=False, meta_goal=None, meta_info=None):
        
        self.messages = []
        self.debug = debug
        self.meta_goal = meta_goal
        self.meta_info = meta_info

        self.add_message("system", self.get_prompt(meta_goal))

    def copy(self):
        new = type(self)(debug=self.debug, meta_goal=self.meta_goal)
        new.messages = [ dict(x) for x in self.messages ]
        return new
        
    def add_message(self, who, what):
        self.messages.append({'role': who, 'content': what})
        
    def get_prompt(self, meta_goal=None):
        if meta_goal is None:
            meta_goal = "improve Alec's life"

        format = getattr(self, "format", "json")
        if format == 'text':
            format_string = "paragraph format"
        elif format == 'json':
            format_string = "JSON-formatted"
        else:
            format_string = f"'{format.lower()}'"
                               
            
        p = flatten_whitespace(f"""
            You are a component of Alec McGail's helpful AI assistant, named the "{self.name}".
            The date and time right now is {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.
            Ultimately you are helping to "{meta_goal}"
        """)+"\n\n"
        if self.meta_info is not None:
            p += flatten_whitespace(self.meta_info) + "\n\n"

        p += flatten_whitespace(f"""
            You have been specifically tasked with the goal: "{self.goal}".
            
            Your response must be {format_string}.
            Always use double-quotes for keys and values.
            Lists CANNOT end in a comma.
        """)

        if hasattr(self, "params"):
            p += f"\n\nYour output must be defined according to the following template:\n{indent(flatten_whitespace(self.params), 2)}"

        if hasattr(self, "detailed_instructions"):
            p += "\n\n" + flatten_whitespace(self.detailed_instructions) + "\n\n"

        return p

    def generate(self):
        # get the name of the file where the subclass is defined
        subclass_file = inspect.getfile(self.__class__)
        subclass_file = Path(subclass_file).stem

        print('\n\n***** ', type(self).__name__, 'in the', subclass_file, 'file ******\n\n')

        for m in self.messages:
            print(f"-- -- -- -- -- -- -- -- -- {m['role']} -- -- -- -- -- --")
            print(m['content'])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = self.messages,
            max_tokens=None,
            temperature=0.9,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            #stop=["\n"],
        )
        
        response = response.choices[0].message.content
        print(' -- -- -- -- -- -- generation:: -- -- -- -- -- --')
        print(response)

        return response
    
    def contemplate(self, query=None):
        if query is not None:
            self.add_message("user", query)

        response = self.generate()
        self.messages.append({'role': 'system', 'content': response})

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
        return args

class SubModule(Module):
    pass