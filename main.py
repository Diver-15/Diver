from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

import config

app = Flask(__name__)
app.secret_key = 'chm'

client = MongoClient(config.Mongo_key)
db = client.dbsparta

@app.route('/')
def home():
    return render_template('signin.html')

@app.route("/signup")
def signup_form():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)