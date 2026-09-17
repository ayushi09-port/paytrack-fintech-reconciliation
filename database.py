import sqlite3

DB_FILE = "paytrack.db"


def get_db_connection():
    """Establishes and returns a database connection with row factory configured."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite database and creates the transactions table schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cursor.fetchall()]

    if columns and "transaction_id" not in columns:
        cursor.execute("DROP TABLE transactions")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_id TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            customer_name TEXT,
            order_id TEXT,
            status TEXT NOT NULL,
            notes TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def add_transaction(
    reference_id,
    amount,
    payment_method,
    trans_date,
    trans_time,
    customer_name,
    order_id,
    status,
    notes,
):
    """Inserts a new transaction record into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (reference_id, amount, payment_method, date, time, customer_name, order_id, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            reference_id,
            amount,
            payment_method,
            trans_date,
            trans_time,
            customer_name,
            order_id,
            status,
            notes,
        ),
    )
    conn.commit()
    conn.close()


def update_transaction(
    reference_id,
    amount,
    payment_method,
    status,
    customer_name,
    order_id,
    notes,
):
    """Updates an existing transaction record by reference_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE transactions 
        SET amount = ?, payment_method = ?, status = ?, customer_name = ?, order_id = ?, notes = ?
        WHERE reference_id = ?
    """,
        (
            amount,
            payment_method,
            status,
            customer_name,
            order_id,
            notes,
            reference_id,
        ),
    )
    conn.commit()
    conn.close()


def delete_transaction(reference_id):
    """Deletes a transaction record by reference_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM transactions WHERE reference_id = ?", (reference_id,)
    )
    conn.commit()
    conn.close()


# Ensure database is initialized on module load
init_db()
