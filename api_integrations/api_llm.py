import json
import requests
from utils import save_json
from config import config
import re
import html
import tiktoken
import httpx

session = requests.Session()

# параметры запроса
def prepare_request(conversation: list, model, stream=False):
    # model endpoint & api key
    if model == 'codestral-latest':
        url = "https://codestral.mistral.ai/v1/chat/completions"
        api_key = config.MISTRAL_API_KEY
    elif 'gpt' in model:
        url = "https://api.openai.com/v1/chat/completions"
        api_key = config.OPENAI_API_KEY
    else:
        url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = config.GROQ_API_KEY

    # request
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {"messages": conversation, "model": model, "stream": stream, }
    save_json(payload, 'api_integrations/llm_last_request.json')
    return url, headers, payload


async def send_chat_request(conversation: list, model="llama3-70b-8192") -> dict:
    if not model:
        model = "llama3-70b-8192"

    # request
    url, headers, payload = prepare_request(conversation, model)

    # response - 60 sec timeout
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            r = await client.post(url, headers=headers, json=payload)
            print(f'{r.status_code = }')
            response_dict: dict = r.json()
            response_dict['status_code'] = r.status_code
        except Exception as e:
            return {'error': e, 'status_code': r.status_code}

    save_json(response_dict, 'api_integrations/llm_last_response.json')
    return response_dict


# сформировать системный промпт в качестве первичного сообщения
def system_message(language: str, extra: str = None) -> dict:
    if not extra:
        extra = ''

    prompt = f"Respond in {language.upper()} language. "
    msg_dict = {
        "role": "system",
        "content": prompt + extra
    }
    return msg_dict


# сообщение от юзера в чат с LLM
def user_message(prompt: str, encoded_image=None) -> dict:
    # если сообщение с изображением (только для gpt-4o)
    if encoded_image:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url":
                {"url": f"data:image/jpeg;base64,{encoded_image}"}
             }
        ]
        msg_dict = {"role": "user", "content": content, "max_tokens": 300, }

    # если только текст
    else:
        msg_dict = {"role": "user", "content": prompt, }
    return msg_dict


# разметка, пригодная для aiogram
def custom_markup_to_html(text: str) -> str:
    # escape спец символов
    text = html.escape(text)

    # замена **text** на <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    # код с указанием ЯП
    def code_replacement(match):
        lang = match.group(1)
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'

    text = re.sub(r'```(\w+)\n(.*?)```', code_replacement, text, flags=re.DOTALL)

    # код без указания ЯП: замена ```code``` на <code>code</code>, включая многострочный код
    text = re.sub(r'```(.*?)```', r'<code>\1</code>', text, flags=re.DOTALL)
    # замена `code` на <code>code</code>
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text, flags=re.DOTALL)
    return text


# стриминг генерации
def stream(conversation: list, model="llama3-70b-8192", batch_size=16):
    if not model:
        model = "llama3-70b-8192"

    # когда число chunk_count достигает batch_size - вернуть и обнулить batch
    chunk_count = 0
    batch = ''

    # request
    url, headers, payload = prepare_request(conversation, model, stream=True)
    response = session.post(url, headers=headers, json=payload, stream=True)

    # stream response
    for line in response.iter_lines():
        if line:
            chunk = line.decode('utf-8')
            if chunk.startswith("data: "):
                chunk = chunk[len("data: "):]
            try:
                # прочитать контент чанка
                chunk_json = json.loads(chunk)
                delta = chunk_json['choices'][0]['delta']
                if 'content' in delta:
                    chunk_count += 1
                    batch += delta['content']

                    # вернуть и обнулить batch. если это второй чанк (первый всегда пустой) - доставить его сразу
                    if chunk_count % batch_size == 0 or chunk_count == 2:
                        print(f'{chunk_count, batch = }')
                        yield batch
                        batch = ''

            except json.JSONDecodeError:
                pass
    yield batch


# посчитать число токенов в тексте
def count_tokens(text: str, model='gpt-4o') -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)


if __name__ == '__main__':
    pass
