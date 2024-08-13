import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="AUTO-DASH Generator", layout="wide")

st.title("AUTO-DASH: Automatic Dashboard Generator")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.success("File successfully uploaded!")
    
    # Save the uploaded file temporarily
    with open("temp_data.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
 
# Clean up temporary file
if os.path.exists("temp_data.csv"):
    os.remove("temp_data.csv")