import os

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

header_code = """
@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
"""
if "def add_header" not in code:
    code = code.replace('app = Flask(__name__)', 'app = Flask(__name__)\n' + header_code)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Added no-cache headers to server.py")
else:
    print("Already added")
