import os
import google.generativeai as genai
import json

GEMINI_MODEL = 'gemini-2.0-flash'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

class GeminiService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    

    def is_pet_related(self, query_text):
        """Check if the query is related to pet care"""
        prompt = f"""
        Determine if the following query is related to pet care or animal health.
        Query: "{query_text}"
        
        Return only a JSON object with a single key "is_pet_related" with a boolean value.
        Example: {{"is_pet_related": true}} or {{"is_pet_related": false}}
        """
        
        response = self.model.generate_content(
                    prompt,
                    generation_config={
                                    'response_mime_type': 'application/json',
                    })
        try:
            result = json.loads(response.text)
            return result.get("is_pet_related", False)
        except:
            # Default to False if we can't parse the response
            return False
    
    
    def generate_followup_questions(self, query_text, num_questions=5):
        """Generate follow-up questions related to the pet care query"""
        prompt = f"""
        Generate {num_questions} follow-up questions to better understand this pet care query:
        "{query_text}"
        
        The questions should help gather more information to provide accurate pet care advice.
        Return only a JSON array of questions.
        Example: ["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config={
                            'response_mime_type': 'application/json',
                    })

        try:
            questions = json.loads(response.text)
            return questions if isinstance(questions, list) else []
        except:
            # Return empty list if we can't parse the response
            return []
    
    
    
    def generate_remedy(self, query_text, qa_pairs):
        """Generate a remedy based on the query and all question-answer pairs"""
        qa_formatted = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs])
        
        prompt = f"""
        Based on the following pet care query and the additional information provided,
        suggest appropriate care advice, remedies, or next steps.
        
        Original Query: "{query_text}"
        
        Additional Information:
        {qa_formatted}
        
        Provide a comprehensive but concise response with practical advice for the pet owner.
        Focus only on pet care advice and avoid any disclaimers or introductions.
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config={
                                'response_mime_type': 'application/json',
                    })
        return response.text