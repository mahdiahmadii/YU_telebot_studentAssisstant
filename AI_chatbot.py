import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GPT_API_TOKEN"), 
)

def answering_question(question):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="gpt-3.5-turbo",
        )
        return chat_completion.choices[0].message.content
    except:
        return "این سرویس موقتا از دسترس خارج شده است"


if __name__ == "__main__":
    answering_question(question)