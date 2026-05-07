import pymysql
import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.hashers import make_password

conn = pymysql.connect(host='127.0.0.1', port=3308, user='root', password='', db='django_db')
cursor = conn.cursor()

def insert_user(username, password, role):
    pwd_hash = make_password(password)
    # Check if exists
    cursor.execute("SELECT id FROM auth_user WHERE username=%s", (username,))
    row = cursor.fetchone()
    if not row:
        import datetime
        now = datetime.datetime.now()
        # insert into auth_user
        cursor.execute("INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (%s, 0, %s, '', '', '', 0, 1, %s)", (pwd_hash, username, now))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"Created {username}")
    else:
        user_id = row[0]
        
    # Check profile
    cursor.execute("SELECT id FROM app_userprofile WHERE user_id=%s", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO app_userprofile (user_id, role) VALUES (%s, %s)", (user_id, role))
    else:
        cursor.execute("UPDATE app_userprofile SET role=%s WHERE user_id=%s", (role, user_id))
    conn.commit()
    print(f"Role {role} set for {username}")

insert_user('admin_user', 'admin123', 'admin')
insert_user('manager_user', 'manager123', 'production_manager')
insert_user('viewer_user', 'viewer123', 'viewer')
