import json
from config import config
import re
import html
import httpx


# сформировать системный промпт в качестве первичного сообщения
def system_message_preset(language: str, extra: str = None) -> dict:
    if not extra:
        extra = ''

    prompt = "Speak {} language. "
    system_message = {
        "role": "system",
        "content": prompt.format(language.upper())+extra
    }
    return system_message


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


def save_json(data: dict, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(filename, 'saved')


async def send_chat_request(conversation: list, model="llama3-70b-8192") -> dict:
    if not model:
        model = "llama3-70b-8192"

    # model endpoint & api
    if model == 'codestral-latest':
        url = "https://codestral.mistral.ai/v1/chat/completions"
        api_key = config.MISTRAL_API_KEY
    else:
        url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = config.GROQ_API_KEY

    # request
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {"messages": conversation, "model": model}
    save_json(payload, 'api_integrations/llm_last_request.json')
    print(f'{url, api_key = }')
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=payload)
        print(f'{r.status_code = }')

    save_json(r.json(), 'api_integrations/llm_last_response.json')
    return r.json()


if __name__ == '__main__':
    pass
