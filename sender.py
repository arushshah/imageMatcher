import requests
import os
url = "http://localhost:5000/upload"
def send_request():
    local_file_to_send = 'sub1.png' 
    files = {
     'file': (os.path.basename(local_file_to_send), open(local_file_to_send, 'rb'), 'application/octet-stream')
    }
    r = requests.post(url, files=files)

send_request()
