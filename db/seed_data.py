from datetime import datetime
from db.database import init_db, add_citizen, add_informant, add_death_record, get_citizen_by_id

# --------------------------
# Seed Database
# --------------------------
def seed_database():
    # Initialize DB
    init_db()

    # --------------------------
    # Citizens
    # --------------------------
    citizens = [
        {"full_name": "John Doe", "national_id": "1234567890", "gender": "Male", "dob": "1980-01-01"},
        {"full_name": "Alice Smith", "national_id": "9876543210", "gender": "Female", "dob": "1990-05-12"},
        {"full_name": "Bob Johnson", "national_id": "5555555555", "gender": "Male", "dob": "1975-03-20"}
    ]
    citizen_ids = []
    for c in citizens:
        citizen = get_citizen_by_id(c['national_id'])
        if citizen:
            citizen_ids.append(citizen[0])
        else:
            citizen_ids.append(add_citizen(c['full_name'], c['national_id'], c['gender'], c['dob']))

    # --------------------------
    # Informants
    # --------------------------
    informants = [
        {"full_name": "Jane Doe", "id_number": "1111111111", "relation": "Spouse"},
        {"full_name": "Mary Smith", "id_number": "2222222222", "relation": "Parent"},
        {"full_name": "Tom Johnson", "id_number": "3333333333", "relation": "Sibling"}
    ]
    informant_ids = []
    for i in informants:
        informant_ids.append(add_informant(i['full_name'], i['id_number'], i['relation']))

    # --------------------------
    # Death Records
    # --------------------------
    death_records = [
        {"citizen_id": citizen_ids[0], "date_of_death": "2025-09-06", "place": "Addis Ababa Hospital", "cause_of_death": "Natural Causes", "informant_id": informant_ids[0], "certificate_number": "DC-2025-0001"},
        {"citizen_id": citizen_ids[1], "date_of_death": "2025-08-15", "place": "Health Center Bole", "cause_of_death": "Accident", "informant_id": informant_ids[1], "certificate_number": "DC-2025-0002"}
    ]
    for dr in death_records:
        add_death_record(
            citizen_id=dr['citizen_id'],
            date_of_death=dr['date_of_death'],
            place=dr['place'],
            cause_of_death=dr['cause_of_death'],
            informant_id=dr['informant_id'],
            certificate_number=dr['certificate_number']
        )

    print("Database seeded with default citizens, informants, and death records.")


# --------------------------
# Run seeding
# --------------------------
if __name__ == "__main__":
    seed_database()
