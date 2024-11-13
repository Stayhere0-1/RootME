from flask import jsonify, redirect, make_response
import mysql.connector
from .database import database
from flask_jwt_extended import create_access_token
import datetime

class UserModel:
    def __init__(self, db_config):
        self.db = database(db_config)

    def username_exist(self, username):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT username FROM User WHERE username = %s", (username,))
            exist = cursor.fetchone() is not None
            return exist  # Kembalikan boolean saja

        except Exception as e:
            print(e)
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
    def get_user_id(self, username):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT id FROM User WHERE username = %s", (username,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_kategori_id(self, kategori_name):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT Kategori_id FROM kategori_soal WHERE Kategori_name = %s"
            cursor.execute(query, (kategori_name,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()            
    def validate_user(self, username, password):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT id, password_md5, role FROM User WHERE username = %s", (username,))
            row = cursor.fetchone()
            
            if row and row[1] == password:
                buat_cookie = {
                    "username": username,
                    "role": row[2]
                }
                
                expires = datetime.timedelta(hours=3)
                access_token = create_access_token(
                    identity=row[0],
                    additional_claims=buat_cookie,
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
    
    def create_soal(self, kategori_id, soal_name, soal_isi, attachment, koneksi_info, value, flag):
            try:
                conn = self.db.get_con()
                cursor = conn.cursor()
                query = """
                    INSERT INTO soal (Kategori_id, Soal_name, Soal_Isi, Attachment, Koneksi_Info, Value, flag)
                    VALUES (%s, %s, %s, %s, %s, %s,%s)
                """
                cursor.execute(query, (kategori_id, soal_name, soal_isi, attachment, koneksi_info, value,flag))
                conn.commit()
                return {"message": "Soal created successfully", "status": "success"}
            except mysql.connector.Error as err:
                return {"message": "Failed to create soal", "error": str(err), "status": "failed"}
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def edit_soal(self, kategori_id, soal_name, soal_isi,attachment, koneksi_info, value,flag, soal_id):
        try:
            conn = self.db.get_con()
            cursor = conn.cursor()
            query = """
            UPDATE soal
            SET Kategori_id = %s, Soal_name = %s, Soal_Isi = %s, Attachment = %s, Koneksi_Info = %s, Value = %s, flag = %s
            WHERE id = %s
            """
            cursor.execute(query, (kategori_id, soal_name, soal_isi, attachment, koneksi_info, value, flag, soal_id))
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
    
    def change_username(self, username, new_username):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            
            if self.username_exist(new_username):
                return jsonify({
                    "message": "Username already exists",
                    "status": "failed"
                }), 409 #Conflict
            
            query = "UPDATE User SET username = %s WHERE username = %s"
            cursor.execute(query, (new_username, username))
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
                #Cancel perubahan
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
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            
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
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
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

    def submit_flag(self, user_id, soal_id, flag):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT flag, Value FROM soal WHERE Soal_id = %s"
            cursor.execute(query, (soal_id,))
            row = cursor.fetchone()
            
            if row:
                correct_flag = row[0]
                value = row[1]
                status = 'Benar' if correct_flag == flag else 'Salah'
                
                query = """
                    INSERT INTO submit (ID, Soal_ID, Record_Submit, Benar_Salah)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (user_id, soal_id, flag, status))
                conn.commit()
                
                if status == 'Benar':
                    query = "SELECT Total_Point FROM leaderboard WHERE ID = %s"
                    cursor.execute(query, (user_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        total_point = row[0] + value
                        query = "UPDATE leaderboard SET Total_Point = %s WHERE ID = %s"
                        cursor.execute(query, (total_point, user_id))
                    else:
                        query = "INSERT INTO leaderboard (ID, Total_Point) VALUES (%s, %s)"
                        cursor.execute(query, (user_id, value))
                    
                    conn.commit()
                    
                    return {
                        "status": "success",
                        "message": "Flag submitted successfully"
                    }, 200
                else:
                    return {
                        "status": "failed",
                        "message": "Incorrect flag"
                    }, 400
            else:
                return {
                    "status": "failed",
                    "message": "Soal not found"
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

    def get_leaderboard(self):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = """
                SELECT u.username, l.Total_Point
                FROM leaderboard l
                JOIN User u ON l.username = u.username
                ORDER BY l.Total_Point DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            leaderboard = [{"username": row[0], "total_point": row[1]} for row in rows]
            return {
                "status": "success",
                "leaderboard": leaderboard
            }, 200

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

    


