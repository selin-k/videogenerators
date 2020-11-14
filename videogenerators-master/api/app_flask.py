from flask import Flask
from flask import request
from flask import render_template
from datetime import datetime
import os, sys

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, World!"

@app.route("/uploader", methods=['POST', 'GET'])
def uploadAudio():
    if request.method == "POST":
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        f = open('C:\\Users\\Acer\\flask-app\\api\\imgs\\' + dt_string + ".mp3", "wb")
        f.write(request.get_data("audio_data"))
        f.close()
        print("writing audio to mp3 file...")
    return dt_string


if __name__ == "__main__":
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)


          
