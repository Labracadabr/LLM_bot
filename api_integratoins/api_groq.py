import json
import requests
from config import config
from pprint import pprint

api_key = config.GROQ_API_KEY
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
conversation_template = {"messages": [{"role": "user", "content": ''}]}
system_preset = "Please respond in {} language. Any character with code between 1 and 126 inclusively must be escaped anywhere with a preceding '\\' character"
xsystem_preset = """Please respond in {} language. Use only following HTML tags for text formatting:
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<a href="http://www.example.com/">inline URL</a>
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
<blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>
"""


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
