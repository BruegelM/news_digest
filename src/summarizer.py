import openai

# Конфигурация OpenAI
OPENAI_API_KEY = 'sk-proj-QbgfirTaZ3bhrM6zm6XMNKIkDhX6Tz2_HXqNzZNw3fJ58f-L-8N1DqpzLJZSMl5IhTFQZn_u3uT3BlbkFJ393n_zkJk_bi0B82Z43WICKjw81U1Thhejp4fU-8ORLSRHX_6hvSBiMH0egODw6BCC_Ng1_YoApi_key'

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
