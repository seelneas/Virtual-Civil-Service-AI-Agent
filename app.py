import streamlit as st
from ui.components.death_form import death_registration_form

st.title("Virtual Civil Service AI Agent")
st.sidebar.header("Choose Service")
service = st.sidebar.selectbox("Service", ["Death Registration", "Birth Registration", "Marriage Registration", "Divorce Registration"])  # Later add Birth, Marriage, Divorce

if service == "Death Registration":
    death_registration_form()
