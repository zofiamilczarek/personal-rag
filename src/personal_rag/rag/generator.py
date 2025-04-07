from transformers import AutoModelForCausalLM, AutoTokenizer

class Generator:
    def __init__(self, checkpoint):
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        self.llm = AutoModelForCausalLM.from_pretrained(checkpoint)
    
    def get_answer(self, prompt):
        inputs = self.tokenizer(prompt)
        answer = self.llm(**inputs)
        answer_decoded = self.tokenizer.decode(answer[0])
        return answer_decoded
    
    