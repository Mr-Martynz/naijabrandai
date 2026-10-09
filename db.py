import sqlite3

DB_PATH = "naijabrandai.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read columns by name
    return conn


def normalize_number(number):
    """Keep digits only, so '+234 813 705 9102' becomes '2348137059102'."""
    return "".join(ch for ch in str(number) if ch.isdigit())


def init_db():
    """Create the tables if they don't exist yet. Safe to run every startup."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                whatsapp_number TEXT NOT NULL UNIQUE,
                phone_number_id TEXT,
                delivery_info TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL REFERENCES vendors(id),
                name TEXT NOT NULL,
                description TEXT,
                price_kobo INTEGER NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                image_path TEXT
            );
        """)
        conn.commit()
    finally:
        conn.close()


def add_vendor(business_name, whatsapp_number, phone_number_id=None, delivery_info=None):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO vendors (business_name, whatsapp_number, phone_number_id, delivery_info) "
            "VALUES (?, ?, ?, ?)",
            (business_name, normalize_number(whatsapp_number), phone_number_id, delivery_info),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_vendor_by_sender(whatsapp_number):
    """Return the vendor row for this number, or None if it isn't a vendor."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM vendors WHERE whatsapp_number = ?",
            (normalize_number(whatsapp_number),),
        ).fetchone()
    finally:
        conn.close()
        