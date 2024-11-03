from flask import jsonify
import mysql.connector
from .database import database

class UserModel:
    def __init__(self, db_config):
        self.db = database(db_config)
    
    def username_exist(self, username1):
        conn = None
        cursor = None
        try:
            conn = self.db.get_con()
            cursor = conn.cursor(buffered=True)

            cursor.execute("SELECT username from USER WHERE username = %s", (username1,))
            exist = cursor.fetchone() is not None
            return exist  # Kembalikan boolean saja
            
        except Exception as e:
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def create_user(self, username, password, mail, role="Guest"):
        conn = None
        cursor = None
        try:
            # Cek username terlebih dahulu
            if self.username_exist(username):
                return jsonify({
                    "message": "Username already exists",
                    "status": "failed"
                }), 409

            conn = self.db.get_con()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO User (username, mail, password_md5, role) VALUES (%s, %s, %s, %s)", 
                (username, mail, password, "Player")
            )
            conn.commit()
            
            return jsonify({
                "message": "User created successfully",
                "status": "success"
            }), 201

        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            return jsonify({
                "message": "Database error",
                "error": str(e),
                "status": "failed"
            }), 500
        except Exception as e:
            if conn:
                conn.rollback()
            return jsonify({
                "message": "Unexpected error",
                "error": str(e),
                "status": "failed"
            }), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()