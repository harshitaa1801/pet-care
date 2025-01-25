import google.generativeai as genai
import json

GEMINI_MODEL = 'gemini-2.0-flash'

class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    def get_response(self, system_message: str, user_message: str) -> dict:
        response  = self.client.generate_content(
            f"{system_message} \n\n {user_message}",
            generation_config={
            'response_mime_type': 'application/json',
        })

        return json.loads(response.text)



def get_response_from_gemini(system_message, user_message):
    
    ai_client = GeminiClient('abcd', GEMINI_MODEL)
    ai_response = ai_client.get_response(system_message, user_message)    
    
    return ai_response
