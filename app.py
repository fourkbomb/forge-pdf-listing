from flask import Flask, render_template
import flask
import json
import requests

app = Flask(__name__)

cached_github_files = []

def request_github_api():
    r = requests.get('https://api.github.com/repos/AiryShift/ForgeInformaticsNotes/contents?ref=master')
    if r.status_code != 200:
        return None
    if not r.headers['content-type'].startswith('application/json'):
        return None

    return r.json()

def make_size_pretty(byte):
    suffix = ['B', 'kB', 'MB', 'GB']
    sidx = 0
    while byte > 10000 and sidx < len(suffix): 
        byte /= 1000
        sidx += 1

    return str(byte) + suffix[sidx]

@app.route('/')
def show_index():
    display = []
    print(cached_github_files)
    for fentry in cached_github_files:
        print(fentry['name'], fentry['name'].endswith('.pdf'))
        if fentry['name'].endswith('.pdf') and fentry['type'] == 'file':
            el = {
                'name': fentry['name'].split('.pdf')[0],
                'size': make_size_pretty(fentry['size']),
                'link': fentry['download_url']
            }
            display.append(el)
    return render_template('index.html', files=display)





if __name__ == '__main__':
    cached_github_files = request_github_api()
    if cached_github_files is None:
        print("WARNING: no cached github files :(")
    app.run(threaded=True, port=8080, host='0.0.0.0')

