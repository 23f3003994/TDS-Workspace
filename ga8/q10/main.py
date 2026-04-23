import hashlib
import functions_framework

@functions_framework.http
def process_text(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'text' not in request_json:
        return {'error': 'Missing "text" field in JSON body'}, 400

    text = str(request_json['text'])
    uppercase = text.upper()
    char_count = len(text.replace('-', '').replace(' ', ''))
    word_count = len(text.replace('-', ' ').split())
    sha = hashlib.sha256(text.encode()).hexdigest()[:16]
    verify = hashlib.sha256(
        f"upper:{uppercase}:chars:{char_count}:words:{word_count}".encode()
    ).hexdigest()[:12]

    return {
        'uppercase': uppercase,
        'char_count': char_count,
        'word_count': word_count,
        'sha256': sha,
        'verify': verify
    }