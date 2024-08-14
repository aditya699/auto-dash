import streamlit as st
import os
import logging
from datetime import datetime
from src.data_loader import get_data, clean_data, validate_data_for_dashboard

# Set up logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = f"auto_dash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_filepath = os.path.join(log_directory, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler()
    ]
)

st.set_page_config(page_title="AUTO-DASH Generator", layout="wide")

st.title("AUTO-DASH: Automatic Dashboard Generator")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.success("File successfully uploaded!")
    
    # Save the uploaded file temporarily
    temp_file_path = "temp_data.csv"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Use the get_data function to load and log the data
    data = get_data(temp_file_path)
    
    if data is not None:
        st.write("Data loaded successfully!")
        st.write(f"Shape of the data: {data.shape}")
        st.write("First few rows of the data:")
        st.dataframe(data.head())
        
        if validate_data_for_dashboard(data):
            st.success("Basic data validation passed. Proceeding with data cleaning.")
            
            cleaned_data = clean_data(data)
            if cleaned_data is not None:
                st.write("Data Cleaning Done.")
                st.write("Cleaned data preview:")
                st.dataframe(cleaned_data.head())
                
                # You can add more data processing or visualization here
            else:
                st.error("Data cleaning failed. Please check the logs for more information.")
        else:
            st.error("Data failed basic validation. Please ensure your CSV file has proper column names and contains data.")
    else:
        st.error("Failed to load the data. Please check the logs for more information.")

    # Clean up temporary file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

# Add a button to view logs
if st.button("View Logs"):
    log_directory = "logs"
    log_files = [f for f in os.listdir(log_directory) if f.endswith('.log')]
    
    if log_files:
        latest_log = max(log_files, key=lambda f: os.path.getmtime(os.path.join(log_directory, f)))
        log_path = os.path.join(log_directory, latest_log)
        
        with open(log_path, 'r') as log_file:
            log_contents = log_file.read()
        
        st.text_area("Log Contents", log_contents, height=300)
    else:
        st.write("No log files found.")