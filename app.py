import streamlit as st
import os
import logging
from datetime import datetime
from src.data_loader import get_data, clean_data, validate_data_for_dashboard
from src.feature_eng import feature_engineering
from src.prompt_builder import generate_dash_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv('GEMINI_API_KEY')

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
        logging.FileHandler(log_filepath, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

st.set_page_config(page_title="AUTO-DASH Generator", layout="wide")

st.title("AUTO-DASH: Automatic Dashboard Generator")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.success("File successfully uploaded!")
    
    # Save the uploaded file temporarily
    temp_file_path = "Staging_Data/temp_data.csv"
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
                
                # Ask user if they want to perform feature engineering
                st.write("Would you like to perform automated feature engineering?")
                st.write("Note: This process may yield creative results but could also produce some incorrect or unexpected outcomes.")
                perform_fe = st.radio("Choose an option:", ("Yes", "No"), index=1)
                
                if perform_fe == "Yes":
                    # Perform feature engineering
                    st.write("Performing feature engineering...")
                    engineered_data, generated_code = feature_engineering(cleaned_data)
                    
                    if generated_code:
                        st.write("Engineered data preview:")
                        st.dataframe(engineered_data.head())
                        
                        # Save the engineered data
                        output_path = "Staging_Data/engineered_data.csv"
                        engineered_data.to_csv(output_path, index=False)
                        st.success(f"Engineered data saved to {output_path}")
                    else:
                        st.warning("No new features were added during feature engineering.")
                else:
                    st.write("Skipping feature engineering.")
                    engineered_data = cleaned_data
                
                # Generate Dash code
                st.write("Generating Dash code...")
                prompt = generate_dash_prompt(engineered_data)
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
                
                try:
                    response = llm.invoke(prompt)
                    dash_code = response.content
                    
                    # Save the generated Dash code
                    dash_code_path = "Generated_Dashboard/dashboard.py"
                    os.makedirs(os.path.dirname(dash_code_path), exist_ok=True)
                    with open(dash_code_path, "w", encoding='utf-8') as f:
                        f.write(dash_code)
                    
                    st.success(f"Dash code generated and saved to {dash_code_path}")
                    st.code(dash_code, language="python")
                    
                    # Provide instructions to run the dashboard
                    st.write("To run the generated dashboard:")
                    st.code("python Generated_Dashboard/dashboard.py", language="bash")
                    
                    # Option to download the generated code
                    st.download_button(
                        label="Download Dash Code",
                        data=dash_code.encode('utf-8'),
                        file_name="dashboard.py",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating Dash code: {str(e)}")
                    logging.error(f"Error generating Dash code: {str(e)}")
                
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
        
        with open(log_path, 'r', encoding='utf-8') as log_file:
            log_contents = log_file.read()
        
        st.text_area("Log Contents", log_contents, height=300)
    else:
        st.write("No log files found.")