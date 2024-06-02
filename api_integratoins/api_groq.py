import json
from config import config
import re
import html
import httpx


api_key = config.GROQ_API_KEY
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
conversation_template = {"messages": [{"role": "user", "content": ''}]}


# сформировать системный промпт в качестве первичного сообщения
def system_message_preset(language: str, extra='') -> dict:
    prompt = "Please respond in {} language. When writing a block of code, always specify programming language. "
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
    payload = {"messages": conversation, "model": model}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=payload)

    print(f'{r.status_code = }')

    save_json(r.json(), 'groq_last_resp.json')
    return r.json()


if __name__ == '__main__':
    pass
