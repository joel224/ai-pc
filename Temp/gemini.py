# gemini.py
import model_api

class Gemini:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = model_api.Model("text-bison")

    def generate_text(self, prompt):
        response = self.model.generate(prompt=prompt)
        return response