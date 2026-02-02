import psycopg2
from psycopg2.extras import DictCursor

DB_PARAMS = {
    "host": "localhost",
    "port": "5432",
    "database": "eco_sys",
    "user": "postgres",
    "password": "ibrohim0811"
}


def get_all_users_from_db():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=DictCursor)
    
    # Kerakli ustunlarni tanlab olamiz
    query = "SELECT id, telegram_id, username, first_name, is_active, phone, uuid, balance, password, date_joined FROM app_user ORDER BY date_joined DESC"
    cur.execute(query)
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    return users


def get_all_tg_ids():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT telegram_id FROM app_user")
    ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return ids