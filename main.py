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

@app.route("/register", methods=["POST"])
def register_post():
    name_receive = request.form['name_give']
    id_receive = request.form['id_give']
    pwd_receive = request.form['pwd_give']

    all_users = list(db.registers.find({}, {'_id': False}))

    count = len(all_users) + 1

    doc = {
        'num':count,
        'name':name_receive,
        'id':id_receive,
        'pwd':pwd_receive
    }

    db.registers.insert_one(doc)

    return jsonify({'msg':'회원가입을 축하드립니다! 로그인해주세요'})

@app.route("/register/check", methods=["POST"])
def register_check():
    id_receive = request.form['id_give']
    check_registers = bool(db.registers.find_one({'id':id_receive}))
    return jsonify({'result': 'success', 'exists': check_registers})


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)