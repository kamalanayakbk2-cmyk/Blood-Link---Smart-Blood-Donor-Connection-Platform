from database import get_connection

connection = get_connection()

if connection:
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")

    print("\nBloodLink Database Tables:")
    for table in cursor.fetchall():
        print(table[0])

    cursor.close()
    connection.close()
    print("\nConnection closed successfully.")