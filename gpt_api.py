from openai import OpenAI

from key import openai_organization_key, openai_api_key

class GPTAPI():
    def __init__(self) -> None:
        self.client = OpenAI(organization=openai_organization_key, api_key=openai_api_key)

    # def __init__(self) -> None:
    #     # self.client = OpenAI(api_key=api_key)
    #     self.client = OpenAI()

    def chat_gpt4o_mini(self, prompt: str, mode: str, temp:float=0):
        response_type = "json_object" if mode == "json" else "text"
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temp,
            response_format={ "type": response_type }
        )

        return completion.choices[0].message.content
    
if __name__ == '__main__':
    api = GPTAPI()
    print(api.chat_gpt4o_mini("What is the meaning of life?", "text", 0.5))