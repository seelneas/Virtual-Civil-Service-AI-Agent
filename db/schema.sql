CREATE TABLE IF NOT EXISTS citizens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    national_id TEXT UNIQUE NOT NULL,
    gender TEXT,
    dob TEXT
);

CREATE TABLE IF NOT EXISTS informants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_number TEXT NOT NULL,
    relation TEXT
);

CREATE TABLE IF NOT EXISTS death_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citizen_id INTEGER NOT NULL,
    date_of_death TEXT,
    place TEXT,
    cause TEXT,
    informant_id INTEGER,
    certificate_number TEXT,
    FOREIGN KEY(citizen_id) REFERENCES citizens(id),
    FOREIGN KEY(informant_id) REFERENCES informants(id)
);
