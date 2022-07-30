from flask import Flask, request, jsonify, g
from models import User
from datetime import datetime, timedelta
from config import SECRET_KEY
from connections import postgres_db
from models.user import gen_pass_hash
from models import Product
from utils import send_email_verify
from flask_cors import CORS
from payments import momo_payment
from flask_socketio import SocketIO
import jwt
import logging
app = Flask(__name__)
app.config['SECRET_KEY'] = 'csdlmysql'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=False, logger=False, async_handlers=True)

@app.after_request
def after_request_handle(response):
    g.db.close()
    logging.debug("closed postgres connection")
    return response

@app.before_request
def before_rq_handle():
    g.db = postgres_db()
    logging.debug("created postgres connection")

@app.route("/login", methods=['POST'])
def login():
    data = dict(request.form)
    if not data:
        data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing username or password"}), 401
    user = User.authenticate(**data)
    if not user:
        return jsonify({ 'msg': 'Sai tài khoản hoặc mật khẩu',
                         'authenticated': False }), 401
    if user.verify == False:
        return jsonify({'msg': 'Tài khoản chưa được xác thực'}), 401


    token = jwt.encode({
        'email': user.email,
        'iat':datetime.now(),
        'exp': datetime.now() + timedelta(hours=12),
        'name': user.name,
        'id': user.id,
        },
        SECRET_KEY,
        algorithm="HS256").decode("UTF-8")
    # SECRET_KEY)
    return jsonify({
        'token': token,
        'email': user.email,
        'name': user.name,
        'id': user.id,
        'role': user.role,
        'phone': user.phone,
        'address': user.address,
    })

@app.route('/user', methods=['GET', 'POST'])
def user():
    params = request.get_json()
    if g.db.query(User).filter(User.email == params.get('email')).first():
        return jsonify({'msg': 'Email đã tồn tại'})
    e = User(email=params.get('email'), password=params['password'])
    e.name = params.get('name')
    e.username = params.get('username')
    e.phone = params.get('phone')
    e.address = params.get('address')
    e.role = params.get('role')
    e.password = gen_pass_hash(params.get('password'))
    g.db.add(e)
    g.db.commit()
    token = jwt.encode({
        'email': e.email,
        'iat':datetime.now(),
        'exp': datetime.now() + timedelta(hours=12),
        'name': e.name,
        'id': e.id,
        },
        SECRET_KEY,
        algorithm="HS256").decode("UTF-8") 
    send_email_verify(e.email, token)
    return jsonify({'msg': 'Chúc mừng bạn đã đăng ký thành công. Truy cập vào email để xác thực tài khoản!'})

@app.route('/products', methods=['GET', 'POST', 'PUT', 'DELETE'])
def products():
    if request.method == 'GET':
        kw = request.args.get('keyword')
        category = request.args.get('category')
        product_id = request.args.get('product_id')
        sort = request.args.get('sort')
        results = []
        if kw:
            for p in g.db.query(Product).filter(Product.title.contains(kw)):
                results.append(p.to_dict())
            return jsonify({'products': results}), 200
        elif sort and sort == "desc":
            for p in g.db.query(Product).order_by(Product._created.desc()):
                results.append(p.to_dict())
            return jsonify({'products': results}), 200
        elif sort and sort == "asc":
            for p in g.db.query(Product).order_by(Product._created.asc()):
                results.append(p.to_dict())
            return jsonify({'products': results}), 200
        elif sort and sort == "price_desc":
            for p in g.db.query(Product).order_by(Product.price.desc()):
                results.append(p.to_dict())
            return jsonify({'products': results}), 200
        elif sort and sort == "price_asc":
            for p in g.db.query(Product).order_by(Product.price.asc()):
                results.append(p.to_dict())
            return jsonify({'products': results}), 200
        elif product_id:
            for p in g.db.query(Product).filter(Product.id == product_id):
                return jsonify({'product': p.to_dict()}), 200
        elif category:
            for p in g.db.query(Product).filter(Product.category.contains(category)):
                results.append(p.to_dict())
            return jsonify({'products': results}), 200
        else:
            for p in g.db.query(Product):
                results.append(p.to_dict())
            return jsonify({'products': results}), 200

    if request.method == 'POST':
        body = request.get_json()
        p = Product()
        for k, v in body.items():
            if hasattr(p, k):
                setattr(p, k, v)
        g.db.add(p)
        g.db.commit()
        return jsonify({'msg': 'Đã thêm sản phẩm'})
    if request.method == 'PUT':
        body = request.get_json()
        _id = body.get('id')
        p = g.db.query(Product).get(_id)
        if not p:
            return jsonify({'msg': 'Product not found'})
        for k, v in body.items():
            if hasattr(p, k):
                setattr(p, k, v)
        g.db.add(p)
        g.db.commit()
        return jsonify({'msg': 'Đã cập nhật sản phẩm'})
    if request.method == 'DELETE':
        _id = request.args.get('id')
        p = g.db.query(Product).get(_id)
        g.db.delete(p)
        g.db.commit()
        return jsonify({'msg': 'Đã xoá sản phẩm'})


@app.route('/verify', methods=['GET'])
def verify():
    token = request.args.get('token')
    token = token.encode()
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user = g.db.query(User).filter(User.email == data.get('email')).first()
    if not user:
        return jsonify({"message": "user not found"}), 404
    user.verify = True
    g.db.add(user)
    g.db.commit()
    return jsonify({"message": "success"})

@app.route('/orders', methods=['POST', 'GET'])
def ordesr():
    return jsonify({"msg": "Tạo thành công order"})

@app.route('/payment', methods=['POST'])
def payment():
    body = request.get_json()
    items = body.get('items')
    if not items:
        return jsonify({"msg": "Not items"})
    total = 30000
    for item in items:
        total += (item.get('quantity') * item.get('price'))
    oke, url = momo_payment(total)
    if oke:
        socketio.emit("PAYMENT", {'msg': 'payment_succes', 'data': body, 'total': total}, broadcast=True)
    return jsonify({"url": url, 'status': oke})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
