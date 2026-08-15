import json, os, time, re
from urllib.request import Request, urlopen
from urllib.error import URLError

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deepseek_config.json')

def load_key():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f).get('api_key', '')
    return os.environ.get('DEEPSEEK_API_KEY', '')

API_URL = 'https://api.deepseek.com/v1/chat/completions'

def ask(prompt, system='Ты — профессиональный карьерный консультант. Отвечай на русском языке.', max_tokens=1024, temperature=0.7, retries=1):
    key = load_key()
    if not key:
        raise ValueError('DeepSeek API key not found')
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': max_tokens,
        'temperature': temperature,
    }).encode('utf-8')
    req = Request(API_URL, data=body, headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    })
    for attempt in range(retries):
        try:
            resp = urlopen(req, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))
            text = data['choices'][0]['message']['content'].strip()
            return text
        except URLError as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError('DeepSeek API failed')
