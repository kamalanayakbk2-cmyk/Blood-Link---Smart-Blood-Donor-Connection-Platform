
from database import get_connection

connection = get_connection()
cursor = connection.cursor(dictionary=True)

phone = "9876543210"

cursor.execute(
    "SELECT user_id, name, email, phone, role FROM Users WHERE phone = %s",
    (phone,)
)

users = cursor.fetchall()

print("\nAccounts using this phone number:")
print(users)

cursor.close()
connection.close()
