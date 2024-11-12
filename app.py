from flask import Flask, request, jsonify, make_response, redirect, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, set_access_cookies, get_jwt, verify_jwt_in_request
from models.user import UserModel
import os
from datetime import timedelta
import hashlib
from functools import wraps
from recovery import send_reset_email, generate_reset_link, verify_reset_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'peduliapagwbjirwkwkakujugamalas!@^^*!******00012839')
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF untuk testing
app.config['JWT_COOKIE_SECURE'] = False  # Set True jika menggunakan HTTPS
jwt = JWTManager(app)

DB_CONFIG = {
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'database': os.environ.get('DB_NAME', 'rootme_db')
}

user_model = UserModel(DB_CONFIG)

def jwt_cookie_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request(locations=['cookies'])
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"msg": "Invalid or missing token", "error": str(e)}), 401
        return decorator
    return wrapper
    return wrapper

def md5encrypt(string):
    plain = string
    return hashlib.md5(plain.encode()).hexdigest()

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        password = md5encrypt(password)
        mail = request.form.get('mail')
        
        user_model.create_user(username, password, mail)
        return render_template('login.html', message="Registration successful", status="success")
        
    except Exception as e:
        return render_template('register.html', message="Registration failed", error=str(e), status="failed")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        password = md5encrypt(password)
        
        result, status_code = user_model.validate_user(username, password)
        
        if status_code == 200:
            print(result)
            access_token = result["access_token"]
            response = make_response(redirect("/home"))
            set_access_cookies(response, access_token)
            print("WOI")
            return response
        else:
            print("MBUT")
            return render_template('login.html', message=result.get('message'), status="failed")
        
    except Exception as e:
        print("OOO LU DISINI?")
        print(e)
        
        
        return render_template('login.html', message="Login failed", error=str(e), status="failed")

# Removed /protected route

@app.route('/home', methods=['GET'])
@jwt_cookie_required()
def home():
    claims = get_jwt()
    username = claims.get('username')
    role = claims.get("role")
    
    return render_template('chall.html', message=f"Welcome {username}! Your email is ! Your role is {role}", status="success")

@app.route('/check', methods=['GET'])
@jwt_cookie_required()
def check():
    claims = get_jwt()
    username = claims.get('username')
    role = claims.get("role")
    print(claims)
    print(role)
    print(username)
    return render_template('check.html', username=username, role=role)

@app.route('/logout', methods=['POST'])
@jwt_cookie_required()
def logout():
    response = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(response)
    return response, 200

@app.route('/create_soal', methods=['POST'])
@jwt_cookie_required()
def create_soal():
    try:
        kategori_id = request.form.get('kategori_id')
        soal_name = request.form.get('soal_name')
        soal_isi = request.form.get('soal_isi')
        attachment = request.form.get('attachment')
        koneksi_info = request.form.get('koneksi_info')
        value = request.form.get('value')
        
        result = user_model._model.create_soal(kategori_id, soal_name, soal_isi, attachment, koneksi_info, value)
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": "Failed to create soal", "error": str(e), "status": "failed"}), 400

@app.route('/request_reset', methods=['POST'])
@jwt_cookie_required()
def request_reset():
    try:
        email = request.form.get('email')
        reset_link = generate_reset_link(email)
        result = send_reset_email(email, reset_link)
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": "Failed to request password reset", "error": str(e), "status": "failed"}), 400

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        return render_template('reset_password.html', token=token)
    try:
        email = verify_reset_token(token)
        if not email:
            return jsonify({"message": "Invalid or expired token", "status": "failed"}), 400
        
        new_password = request.form.get('password')
        new_password = md5encrypt(new_password)
        user_model.change_pass(email, new_password)
        return jsonify({"message": "Password reset successful", "status": "success"})
    except Exception as e:
        return jsonify({"message": "Failed to reset password", "error": str(e), "status": "failed"}), 400

if __name__ == '__main__':
    app.run(debug=False)