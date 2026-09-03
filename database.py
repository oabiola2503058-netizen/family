import psycopg2

# Paste your Supabase PostgreSQL connection URI here
DB_URL = "postgresql://postgres:bhadboiace1386@db.rgtiiqkydjbqiwthamlh.supabase.co:5432/postgres"

def get_connection():
    return psycopg2.connect(DB_URL)

def init_db():
    # Tables are already initialized via Supabase SQL Editor
    pass

def add_user(username, password, role, email):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)", 
                  (username, password, role, email))
        c.execute("INSERT INTO leaderboard (username, score) VALUES (%s, 0) ON CONFLICT (username) DO NOTHING", (username,))
        conn.commit()
        return True
    except psycopg2.Error:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == password:
        return True
    return False

def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    users = c.fetchall()
    conn.close()
    return users

def get_user_email(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE username = %s", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def reset_user_password(username, new_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
    conn.commit()
    conn.close()

def add_countdown(title, target_date, created_by):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO countdowns (title, target_date, created_by) VALUES (%s, %s, %s)", 
              (title, target_date, created_by))
    conn.commit()
    conn.close()

def get_countdowns():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT title, target_date, created_by FROM countdowns ORDER BY target_date ASC")
    events = c.fetchall()
    conn.close()
    return events

def add_photo(title, caption, image_bytes, uploaded_by):
    import base64
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO photos (title, caption, image_data, uploaded_by) VALUES (%s, %s, %s, %s)", 
              (title, caption, b64_image, uploaded_by))
    conn.commit()
    conn.close()

def get_photos():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT title, caption, image_data, uploaded_by, created_at::text FROM photos ORDER BY id DESC")
    photos = c.fetchall()
    conn.close()
    return photos

def update_score(username, points):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE leaderboard SET score = score + %s WHERE username = %s", (points, username))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username, score FROM leaderboard ORDER BY score DESC")
    board = c.fetchall()
    conn.close()
    return board

def send_message(sender, recipient, message):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, recipient, message) VALUES (%s, %s, %s)", 
              (sender, recipient, message))
    conn.commit()
    conn.close()

def get_messages(user1, user2):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT sender, recipient, message, created_at::text 
        FROM messages 
        WHERE (sender = %s AND recipient = %s) OR (sender = %s AND recipient = %s) 
        ORDER BY id ASC
    """, (user1, user2, user2, user1))
    messages = c.fetchall()
    conn.close()
    return messages
