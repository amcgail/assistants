from modularity import *

class SummarizeText(Module):
    description = "This module summarizes long text."
    name = "text summarizer"
    goal = "to provide a summary of long text"
    params = """
        {"summarization": "<summarized text>"}
    """

    def execute_it(self, args):
        return args['summarization']
    
class WriteEssay(Module):
    description = "This module writes an essay."
    name = "essay writer"
    goal = "to outline and compile an essay"
    detailed_instructions = flatten_whitespace("""
        You are simply preparing right now to write, giving an outline that will be delegated to other writers.
        Based on the prompt, make the outline more or less detailed. Detail of the outline impacts the final length of the piece.
    """)

    params = """
        {
            "description": "Summarize here the goals and requirements of the essay.",
            "outline": {
                "Intro": [],
                "Section 1": {
                    "Section 1 paragraph 1 description",
                    "Section 2 paragraph 2 description",
                    "Section 3 paragraph 3": {
                        "Section 3 paragraph 3 sub-paragraph 1",
                        "Section 3 paragraph 3 sub-paragraph 2"
                    }
                },
                "Conclusion": []
            },
            "title": "Essay Title"
        }
    """

    def __init__(self):
        self.summary = []

    def execute_it(self, args):
        self.description = args['description']
        return self._execute_it(args['outline'])

    def _execute_it(self, args, depth=0):

        # some need to be decoded
        if type(args) == str:
            for _ in range(2):
                try:
                    args = json.loads(args)
                except:
                    print('can no longer decode this string: ', args)
                    pass
        
        if type(args) == list:
            parts = []
            for a in args:
                r = self._execute_it(a)
                parts.append(r)

            return "\n".join(parts)
        
        elif type(args) == dict:
            parts = []
            for k, v in args.items():
                r = self._execute_it(v)
                parts.append('=' * depth + f" {k} " + '=' * depth)
                parts.append(r)

            return "\n".join(parts)
        
        elif type(args) == str:
            smaller_writer = WriteSection()

            summ = '\n'.join(self.summary)
            summ = indent(summ, 1, '-')

            prompt = "Overview of the whole essay:\n{description}\n\n"
            prompt += "Description of paragraph you are writing:\n{args}"
            if len(summ):
                prompt += "\n\nA summary of sections you've written so far:\n{summ}"
            prompt = prompt.format(args=args, summ=summ, description=self.description)

            result = smaller_writer.contemplate(prompt)

            self.summary.append(result['summary'])
            return result['full content']
        
        else:
            raise Exception(f"Unexpected type: {type(args)}")
        

class WriteSection(SubModule):
    description = "This module writes a few paragraphs."
    name = "section writer"
    goal = "to write a few paragraphs."
    detailed_instructions = "ALWAYS write in paragraph form."

    params = """
        {
            "full content": "Full content of the section.",
            "summary": "Summary of the section."
        }
    """

    def execute_it(self, args):
        return args