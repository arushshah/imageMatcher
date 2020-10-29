import requests
import os
url = "http://localhost:5000/upload"
def send_file():
    local_file_to_send = 'tmp.jpg'
    files = {
     'file': (os.path.basename(local_file_to_send), open(local_file_to_send, 'rb'), 'application/octet-stream')
    }
    r = requests.post(url, files=files)

url2 = "http://localhost:5000/match"
def get_match():
    payload = {'imgName': 'tmp.jpg'}
    r = requests.get(url2, params=payload)
    print(r.text)

#send_file()
get_match()
