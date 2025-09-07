import streamlit as st
from ui.components.death_form import death_registration_form

st.set_page_config(page_title="Death Registration", layout="wide")

st.title("Death Registration Service")
st.write("Fill in the form below to register a death and generate a certificate.")

death_registration_form()
