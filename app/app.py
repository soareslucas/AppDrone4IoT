from flask import Flask, request, url_for, redirect

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return "teste do index"

@app.route('/map', methods=['GET'])
def findTrain():
    return "Teste do map"

if __name__ == '__main__':
    app.run()