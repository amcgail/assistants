from openai import OpenAI
import time
import json

client = OpenAI()

class Parameters:
    def __init__(self, type="object"):
        self.properties = {}
        self.required = []
        self.type = type

    def add_property(self, name, type, description=None, required=False):
        self.properties[name] = {
            "type": type,
            "description": description,
        }

        if required:
            self.required.append(name)

        return self

    def json(self):
        return {
            "type": self.type,
            "properties": self.properties,
            "required": self.required,
        }

class Thread:
    def __init__(self):
        self.thread = client.beta.threads.create()
        self.id = self.thread.id
        self.run_id = None

    def create_assistant(self, name, instructions, model="gpt-3.5-turbo"):
        return Assistant(
            thread=self,
            name=name,
            instructions=instructions,
            model=model,
        )

    def user_say(self, query):
        return client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=query,
        )
    
    def say(self, role, query):
        return client.beta.threads.messages.create(
            thread_id=self.id,
            role=role,
            content=query,
        )
    
    def print_last_message(self):
        print(self.last_message())

    def last_message(self):
        messages = client.beta.threads.messages.list(thread_id=self.id)
        for msg in messages:
            return f"{msg.role}: {msg.content[0].text.value}"

class Assistant:
    def __init__(self, thread, name, instructions, model="gpt-3.5-turbo"):
        self.name = name
        self.instructions = instructions
        
        self.tools = []
        self.tool_fns = {}

        self.model = model
        self.thread = thread

        self.assistant = None
        self.id = None

    def initialize(self):
        self.assistant = client.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
            tools=self._dump_tools(),
            model=self.model,
        )
        self.id = self.assistant.id

    def add_tool(self, *args, name=None, description=None, parameters=None, function=None, **kwargs):
        if len(args) == 1:
            tool = args[0]

        else:
            tool = {
                "name": name,
                "description": description,
                "parameters": parameters,
            }

        self.tools.append(tool)
        self.tool_fns[name] = function

    def _dump_tools(self):
        return [
            {
                "type": "function",
                "function": tool,
            }
            for tool in self.tools
        ]

    def complete(self):
        run = client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )

        run = self._wait_for_run_completion(run.id)

        # multiple chained actions...
        while run.status == 'requires_action':
            run = self._submit_tool_outputs(run.id, run.required_action.submit_tool_outputs.tool_calls)
            run = self._wait_for_run_completion(run.id)

        return self.thread.last_message()


    def _wait_for_run_completion(self, run_id):
        while True:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run_id)
            #print(f"Current run status: {run.status}")
            if run.status in ['completed', 'failed', 'requires_action']:
                return run
            
    def _submit_tool_outputs(self, run_id, tools_to_call):
        tool_output_array = []
        for tool in tools_to_call:
            output = None
            tool_call_id = tool.id
            function_name = tool.function.name
            function_args = tool.function.arguments

            print('Running tool', function_name, 'with args', function_args)
            fn = self.tool_fns[function_name]
            output = fn(**json.loads(function_args))

            if output:
                tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

        return client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=run_id,
            tool_outputs=tool_output_array
        )
    


if __name__ == "__main__":

    t = Thread()

    a = t.create_assistant(
        name="DM Joe",
        instructions="You are a Dungeon Master. Use the provided functions to properly conduct your duties.",
    )

    def roll_die(n_sides, type=None):
        import random
        result = random.randint(1, n_sides)
        if type is not None:
            result += type_modifiers[type]
        return result

    a.add_tool(
        name="roll_die",
        description=f"""
            Use the descriptions of the ability scores and their associated skills in the rulebook to help you decide what kind of ability check to use. Then determine how hard
            the task is so that you can set the DC for the check. The higher the DC, the more difficult the task. The easiest way to set a DC is to decide whether the task's difficulty is easy, moderate, or hard, and use these three DCs:
            + Easy (DC 10). An easy task requires a minimal level of competence or a modicum of luck to accomplish. Moderate (DC 15). A moderate task requires a slightly higher level of competence to accomplish. A character with a combination of natural aptitude and specialized training can accomplish a moderate task more often than not.
            + Hard (DC 20). Hard tasks include any effort that is beyond the capabilities of most people without aid or exceptional ability. Even with aptitude and training, a character needs some amount of luck - or a lot of specialized training - to pull off a hard task.
        """,
        parameters=(
            Parameters()
                .add_property("n_sides", "integer", "The number of sides on the die.", required=True)
                .add_property("type", "string", "The type of die to roll. For example, 'strength' or 'dexterity'.")
        ).json(),
        function=roll_die,
    )

    type_modifiers = {
        'strength': 2,
        'dexterity': 1,
        'constitution': 0,
        'intelligence': -1,
        'wisdom': -2,
        'charisma': -3,
    }

    def spell_lookup(name):
        print('searching for spell', name)

        import requests
        nameq = name.strip().replace(' ', '+')
        url = f"https://www.dnd5eapi.co/api/spells/?name={nameq}"
        response = requests.get(url)
        response = response.json()

        full = []
        for result in response['results']:
            url = result['url']
            response = requests.get(f"https://www.dnd5eapi.co{url}")
            full.append(response.json())

        if not len(full):
            return "No spells found."

        return json.dumps(full, indent=2)

    a.add_tool(
        name="spell_lookup",
        description=f"""
            Search the D&D 5e API for a spell.
        """,
        parameters=(
            Parameters()
                .add_property("name", "string", "The name of the spell you'd like to look up.", required=True)
        ).json(),
        function=spell_lookup,
    )

    # now let's begin!
    a.initialize()
    t.say("user", "Can I attack this guard? I'm currently bound.")
    a.complete()