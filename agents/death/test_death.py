from datetime import datetime
from agents.death.workflow import run_death_registration
from db.database import init_db

# Initialize database
init_db()

# Dummy file simulation
class DummyFile:
    def __init__(self, name):
        self.name = name
    def getbuffer(self):
        # Read actual dummy file content
        with open(f"agents/death/dummy_files/{self.name}", "rb") as f:
            return f.read()

uploaded_files = [
    DummyFile("id_document.pdf"),
    DummyFile("medical_certificate.pdf")
]

# Initial state
initial_state = {
    "national_id": "1234567890",
    "full_name": "John Doe",
    "gender": "Male",
    "dob": datetime(1980, 1, 1),
    "date_of_death": datetime(2025, 9, 6),
    "place_of_death": "Addis Ababa Hospital",
    "cause_of_death": "Natural Causes",
    "informant_name": "Jane Doe",
    "informant_id": "9876543210",
    "relation": "Spouse",
    "uploaded_files": uploaded_files
}

# Run workflow
final_state = run_death_registration(initial_state)

# Print results
print("Final Workflow State:")
for k, v in final_state.items():
    print(f"{k}: {v}")
