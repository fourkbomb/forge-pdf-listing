from flask import Flask, render_template
import flask
import json
import os
import requests

app = Flask(__name__)

cached_github_files = []

github_data = {}

def request_github_api():
    r = requests.get('https://raw.githubusercontent.com/AiryShift/ForgeInformaticsNotes/master/info.json')
    if r.status_code != 200:
        return None
    try:
        obj = r.json()
        cachedGithubResps = {}
        other = []
        for el in obj:
            # grab github response
            d = '/'.join(el['pdf'].split('/')[:-1])
            name = el['pdf'].split('/')[-1]
            resp = {}
            if d in cachedGithubResps:
                resp = cachedGithubResps[d]
            else:
                r = requests.get('https://api.github.com/repos/AiryShift/ForgeInformaticsNotes/contents/' + d + '?ref=master')
                resp = r.json() # if this fails we're pretty rip anyway so meh
                cachedGithubResps[d] = resp
            for f in resp:
                # find our one
                if f['name'].lower() == name.lower():
                    # got it
                    other.append({
                        'pretty': el['name'],
                        'pdflink': f['download_url'],
                        'texlink': f['download_url'].replace(el['pdf'], el['tex']), # entirely legit
                        'sizePDF': make_size_pretty(f['size']),
                        'sizeTex': '4kB' # chosen by fair dice roll. guaranteed to be random
                    })
        return other
    except e as Exception:
        print("invalid api response received",e)
        return None

def make_size_pretty(byte):
    suffix = ['B', 'kB', 'MB', 'GB']
    sidx = 0
    while byte > 10000 and sidx < len(suffix):
        byte /= 1000
        sidx += 1

    return str(int(byte)) + suffix[sidx]

@app.route('/')
def show_index():
    return render_template('index.html', files=cached_github_files)



if __name__ == '__main__':
    ip = os.environ.get('OPENSHIFT_PYTHON_IP', '0.0.0.0')
    port = int(os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))
    cached_github_files = request_github_api()
    if cached_github_files is None:
        print("WARNING: no cached github files :(")
    app.run(debug=True,threaded=True, port=port, host=ip)

