import requests
urls = [
    'http://localhost:8503/static/js/index-NF8OSF5.js',
    'http://localhost:8503/static/js/index.CV1sObFX.js',
    'http://localhost:8501/static/js/index.CV1sObFX.js'
]
for u in urls:
    try:
        r = requests.get(u, timeout=5)
        print(u, r.status_code, len(r.content))
    except Exception as e:
        print(u, 'ERROR', e)
