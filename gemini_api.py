import google.generativeai as genai
from google.api_core.exceptions import InternalServerError, ResourceExhausted
from vertexai.preview import tokenization
import time

from key import api_keys

class GeminiAPIFreeTier():
    def __init__(self, api_key) -> None:
        self.api_key = api_key

        self.safety_setting = [
            {
                "category": "HARM_CATEGORY_DANGEROUS",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]

        self.model_name = 'gemini-1.5-pro'
        self.model = genai.GenerativeModel(self.model_name,
                                    safety_settings=self.safety_setting
                                    )
        self.request_history = [] #(time, tokens)
        self.resource_exhausted_counter = 0
        

    def check_quota(self, new_tokens:int) -> bool:
        t = time.time()
        request_counter = 1
        token_counter = new_tokens

        for request_content in self.request_history:
            if t - request_content[0] < 60:
                request_counter += 1
                token_counter += request_content[1]

        '''
        gemini pro
        2 RPM (requests per minute)
        32,000 TPM (tokens per minute)
        50 RPD (requests per day)

        gemini flash
        15 RPM (requests per minute)
        1 million TPM (tokens per minute)
        1,500 RPD (requests per day)
        '''

        if self.model_name == 'gemini-1.5-pro':
            if request_counter > 2:
                return False
            elif token_counter > 32000:
                return False
            elif len(self.request_history) > 50:
                return False
            
        elif self.model_name == 'gemini-1.5-flash':
            if request_counter > 15:
                return False
            elif token_counter > 1000000:
                return False
            elif len(self.request_history) > 1500:
                return False

        return True   


    def chat_gemini(self, prompt: str, tokens_amount:int, mode: str, temp:float=0) -> str:
        genai.configure(api_key=self.api_key)
        while not self.check_quota(tokens_amount):
            time.sleep(10)

        if mode == 'json':
            generation_config = {"response_mime_type": "application/json", "temperature": temp}
        elif mode == 'text':
            generation_config = {"response_mime_type": "text/plain", "temperature": temp}
        else:
            raise ValueError('mode should be json or text')

        for i in range(3):
            try:
                response = self.model.generate_content(prompt, generation_config=generation_config)
                response_text = response.text
                self.request_history.append((time.time(), tokens_amount)) 
                return response_text
            except ValueError as e:            
                print(f'security refuse..., attempt {i+1}')
            except InternalServerError:
                print(f'Internal server error..., attempt {i+1}')
        return None


class GeminiAPIRotate():
    def __init__(self) -> None:
        self.gemini_objects = [GeminiAPIFreeTier(api_key) for api_key in api_keys]
        self.model_amount = len(self.gemini_objects)
        self.model_number = 0
        self.RESOURCE_EXHAUSTED_THRESHOLD = 3
        print(f'Gemini API Rotate: {self.model_amount} models')

    def cal_token_lens(self, text:str, model_name='gemini-1.5-pro') -> int:
        tokenizer = tokenization.get_tokenizer_for_model(model_name)
        result = tokenizer.count_tokens(text)
        return result.total_tokens

    def remove_model(self, model_number:int) -> None:
        self.gemini_objects.pop(model_number)
        self.model_amount -= 1
        self.model_number -= 1
        if not self.gemini_objects:
            print('no model available')
            exit()

    def chat_gemini(self, prompt: str, mode: str, temp:float=0) -> str:
        self.model_number = (self.model_number + 1) % self.model_amount
        tokens_amount = self.cal_token_lens(prompt)
        if tokens_amount > 32000:
            print('tokens amount exceed 32000! pass')
            return None
        
        try:
            return self.gemini_objects[self.model_number].chat_gemini(prompt, tokens_amount, mode, temp)        
        except ResourceExhausted:
            self.gemini_objects[self.model_number].resource_exhausted_counter += 1
            if self.gemini_objects[self.model_number].resource_exhausted_counter > self.RESOURCE_EXHAUSTED_THRESHOLD:
                print(f'resource exhausted, model removed')
                self.remove_model(self.model_number)

            return self.chat_gemini(prompt, mode, temp)

if __name__ == '__main__':
    api = GeminiAPIRotate()
    print(api.chat_gemini('hi', 'text'))