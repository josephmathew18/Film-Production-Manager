import pymysql

try:
    conn = pymysql.connect(host='127.0.0.1', port=3308, user='root', password='', db='django_db')
    cursor = conn.cursor()
    
    # Create the user profile table manually to bypass Django migration issues
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_userprofile (
        id bigint AUTO_INCREMENT PRIMARY KEY,
        user_id int NOT NULL UNIQUE,
        role varchar(25) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    
    # Give all existing users the role of admin so the user doesn't get locked out
    cursor.execute("""
    INSERT INTO app_userprofile (user_id, role)
    SELECT id, 'admin' FROM auth_user 
    WHERE NOT EXISTS (SELECT 1 FROM app_userprofile WHERE user_id = auth_user.id)
    """)
    conn.commit()
    print("Table created and users updated via PyMySQL!")
    
except Exception as e:
    print(f"Failed: {e}")
