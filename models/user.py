from flask import jsonify, redirect, make_response
import mysql.connector
from .database import database
from flask_jwt_extended import create_access_token
import datetime

class UserModel:
    def __init__(self, db_config):
        self.db = database(db_config)

    def username_exist(self, username1):
        conn = None
        cursor = None
        try:
            conn = self.db.get_con()
            cursor = conn.cursor(buffered=True)

            cursor.execute("SELECT username FROM User WHERE username = %s", (username1,))
            exist = cursor.fetchone() is not None
            return exist  # Kembalikan boolean saja

        except Exception as e:
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def create_user(self, username, password, mail, role="Player"):
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
                (username, mail, password, role)
            )
            conn.commit()

            return jsonify({
                "message": "User  created successfully",
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

    def validate_user(self, username, password):
        conn = None
        cursor = None
        try:
            conn = self.db.get_con()
            cursor = conn.cursor(buffered=True)
            
            cursor.execute("SELECT id, password_md5, role FROM User WHERE username = %s", (username,))
            row = cursor.fetchone()
            
            if row and row[1] == password:
                additional_claims = {
                    "username": username,
                    "role": row[2]
                }
                
                expires = datetime.timedelta(hours=3)
                access_token = create_access_token(
                    identity=row[0],
                    additional_claims=additional_claims,
                    expires_delta=expires
                )
                
                return {
                    "status": "success",
                    "message": "Login successful",
                    "access_token": access_token
                }, 200
            else:
                return {
                    "status": "failed",
                    "message": "Invalid username or password"
                }, 401

        except mysql.connector.Error as e:
            return {
                "status": "failed",
                "message": "Database error",
                "error": str(e)
            }, 500
        except Exception as e:
            return {
                "status": "failed",
                "message": "Unexpected error",
                "error": str(e)
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def create_soal(self, kategori_id, soal_name, soal_isi, attachment, koneksi_info, value):
            try:
                conn = self.db.get_con()
                cursor = conn.cursor()
                query = """
                    INSERT INTO soal (Kategori_id, Soal_name, Soal_Isi, Attachment, Koneksi_Info, Value)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (kategori_id, soal_name, soal_isi, attachment, koneksi_info, value))
                conn.commit()
                return {"message": "Soal created successfully", "status": "success"}
            except mysql.connector.Error as err:
                return {"message": "Failed to create soal", "error": str(err), "status": "failed"}
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def edit_soal(self, kategori_id, soal_name, soal_isi,attachment, koneksi_info, value, soal_id):
        try:
            conn = self.db.get_con()
            cursor = conn.cursor()
            query = """
            UPDATE soal
            SET Kategori_id = %s, Soal_name = %s, Soal_Isi = %s, Attachment = %s, Koneksi_Info = %s, Value = %s
            WHERE id = %s
            """
            cursor.execute(query, (kategori_id, soal_name, soal_isi, attachment, koneksi_info, value, soal_id))
            conn.commit()
            return {"message": "Soal updated successfully", "status": "success"}
        except mysql.connector.Error as err:
            return {"message": "Failed to update soal", "error": str(err), "status": "failed"}
        finally:
            if cursor:
                cursor.close()
            if conn:    
                conn.close()

    def delete_soal(self, soal_id):
        try:
            conn = self.db.get_con()
            cursor = conn.cursor()
            query = "DELETE FROM soal WHERE id = %s"
            cursor.execute(query, (soal_id,))
            conn.commit()
            return {"message": "Soal deleted successfully", "status": "success"}
        except mysql.connector.Error as err:
            return {"message": "Failed to delete soal", "error": str(err), "status": "failed"}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def change_username(self, user_id, new_username):
        conn = None
        cursor = None
        try:
            conn = self.db.get_con()
            cursor = conn.cursor()
            
            if self.username_exist(new_username):
                return jsonify({
                    "message": "Username already exists",
                    "status": "failed"
                }), 409
            
            query = "UPDATE User SET username = %s WHERE id = %s"
            cursor.execute(query, (new_username, user_id))
            conn.commit()
            
            return jsonify({
                "message": "Username updated successfully",
                "status": "success"
            }), 200
        
        #DEBUG DEFAULT:)
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
    
    #GET MAIL from DATABASE baseon Username
    def get_mail(self, username):
        conn = None
        cursor = None
        try:
            conn = self.db.get_con()
            cursor = conn.cursor(buffered=True)
            
            query = "SELECT mail FROM User WHERE username = %s"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "status": "success",
                    "mail": row[0]
                }, 200
            else:
                return {
                    "status": "failed",
                    "message": "User not found"
                }, 404

        except mysql.connector.Error as e:
            return {
                "status": "failed",
                "message": "Database error",
                "error": str(e)
            }, 500
        except Exception as e:
            return {
                "status": "failed",
                "message": "Unexpected error",
                "error": str(e)
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def change_pass(self, mail, new_pass):
        print("MAIL:",mail)
        conn = None
        cursor = None
        try:
            conn = self.db.get_con()
            cursor = conn.cursor()
            
            
            query = "UPDATE User SET password_md5 = %s WHERE mail = %s"
            cursor.execute(query, (new_pass,mail ))
            conn.commit()
            
            return jsonify({
                "message": "Password updated successfully",
                "status": "success"
            }), 200
        
        #DEBUG DEFAULT:)
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