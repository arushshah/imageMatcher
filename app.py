from flask import Flask, request, jsonify
#import getMatch

app = Flask(__name__)

@app.route('/')
def index():
	return "<h1>Image Matcher</h1>"

@app.route('/match/', methods=['GET'])
def match():
    imgName = request.args.get("imgName", None)
#   return getMatch.getImg(str(imgName))
    
if __name__ == '__main__':
    app.run(threaded=True, port=5000)
