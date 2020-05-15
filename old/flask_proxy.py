from flask import Flask, request
import telepot
import urllib3




#from flask import Flask
from requests import get

app = Flask(__name__)
SITE_NAME = 'https://google.com/'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
  return get(f'{SITE_NAME}{path}').content

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080)
