import bcrypt
import mysql.connector
from datetime import datetime, timedelta

host="192.168.65.6"
user="hanskingdom"
password="06J3LND9NFH"
database="hanskingdom"


def save_profile_picture(encoded_string, filename):
    with open(filename, "wb") as image_file:
        image_file.write(encoded_string)


def prepare_image(profile_picture):
    if profile_picture:
        pass
    else:
        profile_picture="static/default_profile.png"
    with open(profile_picture,"rb") as image_file:
        encoded_string=image_file.read()
    return encoded_string


class UserAccountSystem:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            email VARCHAR(255) PRIMARY KEY,
                            username VARCHAR(255),
                            password VARCHAR(255),
                            password_last_changed DATETIME,
                            password_expires_at DATETIME,
                            is_2fa_enabled BOOLEAN,
                            profile_picture MEDIUMBLOB)

                    ''')
        self.conn.commit()

    def register_user(self, email, username, password, profile_picture=None):
        profile_picture=prepare_image(profile_picture)
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        expires_at = (datetime.utcnow() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (email, username, password, password_last_changed, password_expires_at, is_2fa_enabled, profile_picture) VALUES (%s, %s, %s, %s, %s, %s, %s)",(email, username, hashed_password, now, expires_at, False, profile_picture))
            self.conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False

    def authenticate_user(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        row = cursor.fetchone()
        if row is not None:
            hashed_password = row[2]
            if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                return True
        return False

    def delete_user(self, email):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE email=%s", (email,))
        self.conn.commit()

    def update_password(self, email, new_password):
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        expires_at = (datetime.utcnow() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET password=%s, password_last_changed=%s, password_expires_at=%s WHERE email=%s", (hashed_password, now, expires_at, email))
        self.conn.commit()

    def list_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT email, username FROM users")
        return [(row[0], row[1]) for row in cursor.fetchall()]

    def update_username(self, email, new_username):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET username=%s WHERE email=%s", (new_username, email))
        self.conn.commit()

    def get_username(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username FROM users WHERE email=%s", (email,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        return None
    
    def update_profile_picture(self, email, profile_picture=None):
        profile_picture=prepare_image(profile_picture)
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET profile_picture = %s WHERE email = %s", (profile_picture, email))
        self.conn.commit()

    def get_profile_picture(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT profile_picture FROM users WHERE email=%s", (email,))
        row = cursor.fetchone()
        if row is not None:           
            profile_pic=("static/temp/profile_pic/"+email+".png")
            save_profile_picture(row[0],profile_pic)
            return profile_pic
        return None