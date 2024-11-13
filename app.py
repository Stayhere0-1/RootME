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
            print(result)
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

@app.route('/create_soal', methods=['POST', 'GET'])
@jwt_cookie_required()
def create_soal():
    if request.method == 'GET':
        return render_template('create_soal.html')
    try:
        kategori_name = request.form.get('kategori_id')
        soal_name = request.form.get('soal_name')
        soal_isi = request.form.get('soal_isi')
        attachment = request.form.get('attachment')
        koneksi_info = request.form.get('koneksi_info')
        value = request.form.get('value')
        kategori_id = user_model.get_kategori_id(kategori_name)
        flag = request.form.get("flag")
        value = int(value)
        print(f"kategori_id: {kategori_id}, soal_name: {soal_name}, soal_isi: {soal_isi}, attachment: {attachment}, koneksi_info: {koneksi_info}, value: {value}, flag: {flag}")
        result = user_model.create_soal(kategori_id, soal_name, soal_isi, attachment, koneksi_info, value,flag)
        print(result)
        return jsonify(result)
    
    except Exception as e:
        print(e)
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

@app.route('/change_username', methods=['POST','GET'])
@jwt_cookie_required()
def change_username():
    try:
        new_username = request.form.get('new_username')
        claims = get_jwt()
        user_now = claims.get('username')
        
        result = user_model.change_username(user_now, new_username)
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": "Failed to change username", "error": str(e), "status": "failed"}), 400

@app.route('/submit_flag', methods=['POST', 'GET'])
@jwt_cookie_required()
def submit_flag():
    if request.method == 'GET':
        return render_template('submit_flag.html')
    try:
        claims = get_jwt()
        username = claims.get('username')
        user_id = user_model.get_user_id(username)
        soal_id = request.form.get('soal_id')
        flag = request.form.get('flag')
        
        result, status_code = user_model.submit_flag(user_id, soal_id, flag)
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"message": "Failed to submit flag", "error": str(e), "status": "failed"}), 400

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        result, status_code = user_model.get_leaderboard()
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"message": "Failed to fetch leaderboard", "error": str(e), "status": "failed"}), 400

@app.route('/get_mail', methods=['GET'])
@jwt_cookie_required()
def get_mail():
    try:
        claims = get_jwt()
        username = claims.get('username')
        
        result, status_code = user_model.get_mail(username)
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"message": "Failed to get mail", "error": str(e), "status": "failed"}), 400

@app.route('/change_pass', methods=['POST'])
@jwt_cookie_required()
def change_pass():
    try:
        claims = get_jwt()
        username = claims.get('username')
        mail = user_model.get_mail(username)['mail']
        new_pass = request.form.get('new_pass')
        new_pass = md5encrypt(new_pass)
        
        result, status_code = user_model.change_pass(mail, new_pass)
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"message": "Failed to change password", "error": str(e), "status": "failed"}), 400

@app.route('/edit_soal', methods=['POST'])
@jwt_cookie_required()
def edit_soal():
    try:
        kategori_id = request.form.get('kategori_id')
        soal_name = request.form.get('soal_name')
        soal_isi = request.form.get('soal_isi')
        attachment = request.form.get('attachment')
        koneksi_info = request.form.get('koneksi_info')
        value = request.form.get('value')
        flag = request.form.get('flag')
        soal_id = request.form.get('soal_id')
        
        result = user_model.edit_soal(kategori_id, soal_name, soal_isi, attachment, koneksi_info, value, flag, soal_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": "Failed to edit soal", "error": str(e), "status": "failed"}), 400

@app.route('/delete_soal', methods=['POST'])
@jwt_cookie_required()
def delete_soal():
    try:
        soal_id = request.form.get('soal_id')
        
        result = user_model.delete_soal(soal_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": "Failed to delete soal", "error": str(e), "status": "failed"}), 400

@app.route('/get_kategori_id', methods=['GET'])
@jwt_cookie_required()
def get_kategori_id():
    try:
        kategori_name = request.args.get('kategori_name')
        kategori_id = user_model.get_kategori_id(kategori_name)
        
        if kategori_id:
            return jsonify({"status": "success", "kategori_id": kategori_id}), 200
        else:
            return jsonify({"status": "failed", "message": "Kategori not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to get Kategori_id", "error": str(e), "status": "failed"}), 400

if __name__ == '__main__':
    app.run(debug=False)