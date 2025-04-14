import pymysql

conn = pymysql.connect(host="localhost", user="root", password="root123")
cursor = conn.cursor()

db1 = 'brandsinfo2'
db2 = 'brandsinfo'

# Fetch tables from both databases
cursor.execute(f"SHOW TABLES FROM {db1}")
db1_tables = [row[0] for row in cursor.fetchall()]

cursor.execute(f"SHOW TABLES FROM {db2}")
db2_tables = [row[0] for row in cursor.fetchall()]

# Loop through matching tables
for table in db1_tables:
    if table in db2_tables:
        print(f"\nProcessing table: {table}")
        # Get column names
        cursor.execute(f"SHOW COLUMNS FROM {db1}.{table}")
        cols1 = [row[0] for row in cursor.fetchall()]

        cursor.execute(f"SHOW COLUMNS FROM {db2}.{table}")
        cols2 = [row[0] for row in cursor.fetchall()]

        # Determine common columns
        common_cols = list(set(cols1) & set(cols2))

        if not common_cols:
            print("No common columns.")
            continue

        col_str = ', '.join(common_cols)
        src_col_str = ', '.join([f"src.`{col}`" for col in common_cols])  # Use src. prefix for SELECT

        # Attempt to find primary key
        cursor.execute(f"SHOW KEYS FROM {db1}.{table} WHERE Key_name = 'PRIMARY'")
        primary_key_info = cursor.fetchone()

        try:
            if primary_key_info:
                primary_col = primary_key_info[4]  # Column_name
                sql = f"""
                INSERT INTO {db2}.{table} ({col_str})
                SELECT {src_col_str}
                FROM {db1}.{table} src
                LEFT JOIN {db2}.{table} tgt ON src.`{primary_col}` = tgt.`{primary_col}`
                WHERE tgt.`{primary_col}` IS NULL;
                """
            else:
                # Fallback: insert all rows with no JOIN
                sql = f"INSERT INTO {db2}.{table} ({col_str}) SELECT {src_col_str} FROM {db1}.{table} src;"

            cursor.execute(sql)
            print(f"Inserted data into {table}")
        except Exception as e:
            print(f"Error inserting into {table}: {e}")

conn.commit()
cursor.close()
conn.close()
