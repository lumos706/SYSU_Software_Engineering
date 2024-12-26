import pymysql

def create_database(user, password, host, port, database):
    # Connect to MySQL server
    conn = pymysql.connect(
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = conn.cursor()

    # Create database if it does not exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()

def create_database_from_sql(sql_file_path, user, password, host, port, database):
    # Create the database
    create_database(user, password, host, port, database)

    # Connect to the newly created database
    conn = pymysql.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    cursor = conn.cursor()

    # Read the .sql file
    with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
        sql_script = sql_file.read()

    # Execute the SQL script
    try:
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
        print("Database created successfully.")
    except pymysql.MySQLError as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        cursor.close()
        conn.close()

# Usage example
create_database_from_sql('drone_system.sql', 'root', '123456', 'localhost', 3306, 'drone_system')