
import mysql.connector

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3308,
            user="bloodlink_user",
            password="BloodLinkUser2026",
            database="bloodlink_db"
        )

        if connection.is_connected():
            print("BloodLink database connected successfully!")
            return connection

    except mysql.connector.Error as error:
        print("Database connection failed:", error)
        return None
