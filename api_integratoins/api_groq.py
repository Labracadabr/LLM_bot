import json
import requests
from config import config
import re
import html


api_key = config.GROQ_API_KEY
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
conversation_template = {"messages": [{"role": "user", "content": ''}]}
system_preset = "Please respond in {} language."


def custom_markup_to_html(text):
    # escape спец символов
    text = html.escape(text)

    # замена **text** на <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    # замена ```code``` на <code>code</code>, включая многострочный код
    text = re.sub(r'```(.*?)```', r'<code>\1</code>', text, flags=re.DOTALL)
    return text


def restart_context():
    pass


def save_json(data: dict, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(filename, 'saved')


def send_chat_request(conversation: list, model="llama3-70b-8192") -> dict:
    data = {
        "messages": conversation,
        "model": model
    }
    r = requests.post(url, headers=headers, json=data)
    print(f'{r.status_code = }')
    save_json(r.json(), 'groq_last_resp.json')
    print()
    if r.ok:
        return r.json()
    else:
        return {"error": "Request failed with status code: " + str(r.status_code)}


if __name__ == '__main__':
    pass
