from flask import Flask, render_template, request, session ,jsonify, redirect,url_for

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.u82lpnm.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.db8bteam4

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

import hashlib

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def login_post():
    userId_receive = request.form['userId_give']
    userPw_receive = request.form['userPw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(userPw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.account.find_one({'id': userId_receive, 'password': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
    # JWT 토큰에는, payload와 시크릿키가 필요합니다.
    # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
    # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
    # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.

        payload = {
            'id': userId_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': "아이디/비밀번호가 일치하지 않습니다."})

@app.route("/reply", methods=["GET"])
def reply_get():

    all_list = list(db.replydb.find({}, {'_id': False}))

    return jsonify({'list': all_list})

@app.route("/reply", methods=["POST"])
def reply_post():

    token_receive = request.cookies.get('mytoken')
    reply_receive = request.form['reply_give']

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.account.find_one({"id": payload['id']})

        doc = {
            "id" : user_info["id"],
            "reply": reply_receive
        }

        db.replydb.insert_one(doc)

        return jsonify({'msg':'등록 완료!'})
    except jwt.ExpiredSignatureError:
        return jsonify({'msg': "로그인 시간이 만료되었습니다."})
    except jwt.exceptions.DecodeError:
        return jsonify({'msg': "로그인 정보가 없습니다."})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
