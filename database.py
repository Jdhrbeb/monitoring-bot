import sqlite3


DB_NAME = "messages.db"


# =========================
# DATABASE CONNECTION
# =========================
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


# =========================
# TABLE YARATISH
# =========================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            text TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =========================
# XABAR SAQLASH
# status: "bad" yoki "normal"
# =========================
def save_message(username, text, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (username, text, status)
        VALUES (?, ?, ?)
    """, (username, text, status))

    conn.commit()
    conn.close()


# =========================
# GURUH STATISTIKASI
# =========================
def get_group_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status='bad' THEN 1 ELSE 0 END) as bad
        FROM messages
    """)

    result = cursor.fetchone()
    conn.close()

    total = result[0] if result[0] else 0
    bad = result[1] if result[1] else 0

    return total, bad


# =========================
# RISK SCORE HISOBLASH
# =========================
def get_risk_score():
    total, bad = get_group_stats()

    if total == 0:
        return 0

    return int((bad / total) * 100)


# =========================
# TOP USERS
# =========================
def get_top_users(limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, COUNT(*) as total
        FROM messages
        GROUP BY username
        ORDER BY total DESC
        LIMIT ?
    """, (limit,))

    result = cursor.fetchall()
    conn.close()

    return result
def get_statistics():

    conn = get_connection()
    cursor = conn.cursor()

    total = cursor.execute(
        "SELECT COUNT(*) FROM messages"
    ).fetchone()[0]

    normal = cursor.execute(
        "SELECT COUNT(*) FROM messages WHERE status='normal'"
    ).fetchone()[0]

    bad = cursor.execute(
        "SELECT COUNT(*) FROM messages WHERE status='bad'"
    ).fetchone()[0]

    conn.close()

    return total, normal, bad
def get_last_messages(limit=10):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, status, text
        FROM messages
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    result = cursor.fetchall()
    conn.close()

    return result
def get_all_messages():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, text, status
    FROM messages
    ORDER BY id DESC
""")

    result = cursor.fetchall()
    conn.close()

    return result
