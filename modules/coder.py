from ..common import *

new_module_template = Path(__file__).parent / "new_module_template.py"
with open(new_module_template) as f:
    new_module_template = f.read()

class CreateModule(Module):
    name = 'module creator'
    goal = "to create a new module."
    params = """
    FIRST LINE is the namespace, no quotes.
    THE REST of the response is the code, with correct spacing and indentation, ready to be pasted into the file.
    """
    detailed_instructions = """
    Here is a template for a module:
        from ..common import *
        {preliminary_code}

        class {class_name}(Module):
            description = "{description}"
            name = "{name}"
            goal = "{goal}"
            params = "{params}"

            def execute_it(self, args):
                {execute_it_code}

    For example:
        from ..common import *

        # [definition of send_email goes here]

        class SendEmail(Module):
            goal = "to send an email"
            name = "emailer"
            detailed_instructions = flatten_whitespace(\"\"\"
                You will need to provide an exact email address.
                If you don't know the email address, add Alec to the recipients and note in the message that Alec needs to forward the email.
                Please only provide a body, no subject.
                Sign the email as "Alec's AI Assistant".
                                                        
                Only send emails to the following addresses:
                - Mom: bajap123@gmail.com
                - Dad: bajap21@gmail.com
                - Alec: amcgail2@gmail.com
            \"\"\")
            params = \"\"\"
                {
                    'recipients': ['email address 1', 'email address 2'],
                    'subject': 'subject of the email',
                    'message': 'body of the email',
                }
            \"\"\"

            def execute_it(self, args):
                send_email(args['recipients'], args['subject'], args['message'])
                return True
    """

    def execute_it(self, args):
        # build the new module from a template
        args = args.split("\n")
        namespace = args[0]
        new_module = '\n'.join(args[1:])
        #new_module = args['code']
        #namespace = args['namespace']

        if len(args) == 2 and args[1][0] == "\"": # sometimes it returns a string
            new_module = json.loads(new_module)
            new_module = new_module.replace('\\n', '\n')

        # create a new file in this directory
        py_file = Path(__file__).parent / f"{namespace}.py"
        if not py_file.exists():
            # create the file
            with open(py_file, 'w') as f:
                f.write(new_module)
        else:
            # append to the file
            with open(py_file, 'a') as f:
                f.write('\n\n')
                f.write('# -------------------- auto-generated code -----------------------\n')
                f.write(new_module)

        # now test the module

        return True