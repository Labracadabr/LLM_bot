from utils import save_json
from config import config
import re
import html
import httpx


async def send_chat_request(conversation: list, model="llama3-70b-8192") -> dict:
    if not model:
        model = "llama3-70b-8192"

    # model endpoint & api
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
    payload = {"messages": conversation, "model": model}
    save_json(payload, 'api_integrations/llm_last_request.json')

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


if __name__ == '__main__':
    pass
