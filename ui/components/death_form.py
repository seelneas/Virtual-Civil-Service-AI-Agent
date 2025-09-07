import streamlit as st
import os
from db.database import add_citizen, add_informant, add_death_record
from agents.death.workflow import run_death_registration
from agents.death.config import DOCUMENTS_PATH
from pathlib import Path

def death_registration_form():
    st.header("Death Registration Form")

    with st.form("death_form"):
        st.subheader("Deceased Details")
        full_name = st.text_input("Full Name")
        national_id = st.text_input("National ID")
        gender = st.selectbox("Gender", ["Male", "Female"])
        dob = st.date_input("Date of Birth")
        date_of_death = st.date_input("Date of Death")
        place_of_death = st.text_input("Place of Death")
        cause_of_death = st.text_area("Cause of Death")

        st.subheader("Informant Details")
        informant_name = st.text_input("Informant Full Name")
        informant_id = st.text_input("Informant ID Number")
        relation = st.text_input("Relation to Deceased")

        st.subheader("Upload Required Documents")
        uploaded_files = st.file_uploader("Upload PDFs/Images", accept_multiple_files=True)

        submitted = st.form_submit_button("Submit")

        if submitted:
            citizen_id = add_citizen(full_name, national_id, gender, dob)
            informant_id_db = add_informant(informant_name, informant_id, relation)
            record_id = add_death_record(citizen_id, date_of_death, place_of_death, cause_of_death, informant_id_db, certificate_number=None)

            # Save uploaded files locally
            os.makedirs(DOCUMENTS_PATH, exist_ok=True)
            for file in uploaded_files:
                file_path = os.path.join(DOCUMENTS_PATH, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

            # Run agent workflow
            data = {
                "record_id": record_id,
                "full_name": full_name,
                "national_id": national_id,
                "date_of_death": date_of_death,
                "place_of_death": place_of_death,
                "cause_of_death": cause_of_death,
                "informant_name": informant_name,
                "informant_id": informant_id,
                "relation": relation,
                "citizen_id": citizen_id
            }

            result = run_death_registration(data)
            cert_path = result.get('certificate_path', None)

            if cert_path and Path(cert_path).exists():
                st.success(f"Certificate generated: {cert_path}")
                
                # Open the file in binary mode
                with open(cert_path, "rb") as f:
                    pdf_bytes = f.read()
                
                # Download button
                st.download_button(
                    label="Download Certificate",
                    data=pdf_bytes,
                    file_name=Path(cert_path).name,
                    mime="application/pdf"
                )
            else:
                st.warning("Certificate path not found. Please check the workflow.")

