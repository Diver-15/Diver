from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
import config
import jwt
import datetime
import hashlib

# client = MongoClient('mongodb://3.34.44.93', 27017, username="sparta", password="woowa")
client = MongoClient(config.Mongo_key)
db = client.dbsparta

SECRET_KEY = 'SPARTA'


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('shop.html', name=user_info["name"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login"))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/shopping')
def shoppingmall():
    return render_template('shop.html')


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive})

    return jsonify({'result': 'success'})


# [회원가입 아이디 중복확인 API]
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.user.find_one({"id": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# [로그인 API]
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


# [쇼핑몰 관련 API]
@app.route("/clothes_male", methods=["GET"])
def male_get():
    token_reveive = request.cookies.get('mytoken')
    payload = jwt.decode(token_reveive, SECRET_KEY, algorithms=['HS256'])

    clothe_list = list(db.shoppingmall.find({'gender': '남'}))
    for cloth in clothe_list:
        cloth["_id"] = str(cloth["_id"])
        cloth["count_heart"] = db.likes.count_documents({"post_id": cloth["_id"], "type": "heart"})
        cloth["heart_by_me"] = bool(db.likes.find_one({"post_id": cloth["_id"], "type": "heart", "username": payload['id']}))
    return jsonify({'clothes': clothe_list})


@app.route("/clothes_female", methods=["GET"])
def female_get():
    token_reveive = request.cookies.get('mytoken')
    payload = jwt.decode(token_reveive, SECRET_KEY, algorithms=['HS256'])

    clothe_list = list(db.shoppingmall.find({'gender': '여'}))
    for cloth in clothe_list:
        cloth["_id"] = str(cloth["_id"])
        cloth["count_heart"] = db.likes.count_documents({"post_id": cloth["_id"], "type": "heart"})
        cloth["heart_by_me"] = bool(db.likes.find_one({"post_id": cloth["_id"], "type": "heart", "username": payload['id']}))
    return jsonify({'clothes': clothe_list})


# 좋아요 API
@app.route('/update_like', methods=['POST'])
def update_like():
    token_reveive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_reveive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["id"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)
