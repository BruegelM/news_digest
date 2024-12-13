import openai

async def summarize(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": f"Сделай краткое изложение следующего текста: {text}"}
        ]
    )
    summary = response['choices'][0]['message']['content']
    return summary
