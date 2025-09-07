import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "civil_service.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Citizens table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citizens (
        citizen_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        national_id TEXT UNIQUE,
        gender TEXT,
        date_of_birth TEXT,
        status TEXT DEFAULT 'alive'
    )
    """)

    # Informants table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS informants (
        informant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        id_number TEXT UNIQUE,
        relation_to_deceased TEXT
    )
    """)

    # Death Records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS death_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        citizen_id INTEGER,
        date_of_death TEXT,
        place_of_death TEXT,
        cause_of_death TEXT,
        informant_id INTEGER,
        certificate_number TEXT UNIQUE,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (citizen_id) REFERENCES citizens(citizen_id),
        FOREIGN KEY (informant_id) REFERENCES informants(informant_id)
    )
    """)

    # Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        doc_type TEXT,
        file_path TEXT,
        verified INTEGER DEFAULT 0,
        FOREIGN KEY (record_id) REFERENCES death_records(record_id)
    )
    """)

    # Fraud Checks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fraud_checks (
        check_id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        check_type TEXT,
        result TEXT,
        checked_at TEXT,
        FOREIGN KEY (record_id) REFERENCES death_records(record_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized at:", DB_PATH)

if __name__ == "__main__":
    init_db()
