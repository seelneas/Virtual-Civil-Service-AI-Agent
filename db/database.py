import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "civil_service.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Citizens table
    c.execute('''
    CREATE TABLE IF NOT EXISTS citizens (
        citizen_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        national_id TEXT UNIQUE,
        gender TEXT,
        dob DATE
    )
    ''')

    # Informants table
    c.execute('''
    CREATE TABLE IF NOT EXISTS informants (
        informant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        id_number TEXT,
        relation TEXT
    )
    ''')

    # Death records table
    c.execute('''
    CREATE TABLE IF NOT EXISTS death_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        citizen_id INTEGER,
        date_of_death DATE,
        place TEXT,
        cause_of_death TEXT,
        informant_id INTEGER,
        certificate_number TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Citizen helpers
def add_citizen(full_name, national_id, gender, dob):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO citizens (full_name, national_id, gender, date_of_birth) VALUES (?, ?, ?, ?)",
                   (full_name, national_id, gender, dob))
    conn.commit()
    citizen_id = cursor.lastrowid
    conn.close()
    return citizen_id

def get_citizen_by_id(national_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citizens WHERE national_id=?", (national_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# Informant helpers
def add_informant(full_name, id_number, relation):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO informants (full_name, id_number, relation_to_deceased) VALUES (?, ?, ?)",
                   (full_name, id_number, relation))
    conn.commit()
    informant_id = cursor.lastrowid
    conn.close()
    return informant_id

# Death record helpers
def add_death_record(citizen_id, date_of_death, place, cause, informant_id, certificate_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO death_records (citizen_id, date_of_death, place_of_death, cause_of_death, informant_id, certificate_number)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (citizen_id, date_of_death, place, cause, informant_id, certificate_number))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id
def check_duplicate_death(citizen_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT record_id FROM death_records WHERE citizen_id = ?', (citizen_id,))
    result = c.fetchone()
    conn.close()
    return result is not None