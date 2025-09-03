from .claude_llm import ClaudeCodeLLM

class ClaudeIntegrationCore:
    def __init__(self):
        self.llm = ClaudeCodeLLM()
        self.memory = {}
        self.prompt_templates = {"basic_qa": "Question: {question}"}
        self.chains = {"basic_qa": "basic_qa_chain"}

    def ask_question(self, question, chain_type="basic_qa"):
        return self.llm._call(question)

class ClaudeChain:
    def __init__(self, core):
        self.core = core
        self.llm = core.llm
