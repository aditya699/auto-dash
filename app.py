import streamlit as st
import os
import pandas as pd
from datetime import datetime
import time
from src.data_loader import get_data, clean_data, validate_data_for_dashboard
from src.feature_eng import feature_engineering
from src.prompt_builder import prompt_generator
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()
os.environ["ANTHROPIC_API_KEY"] = os.getenv('ANTHROPIC_API_KEY')

st.set_page_config(page_title="AUTO-DASH Generator", layout="wide")

st.title("🚀 AUTO-DASH: Your Personal Dashboard Wizard")
st.write("Upload a CSV file, and watch as we conjure up an interactive dashboard just for you!")

uploaded_file = st.file_uploader("📂 Choose your data potion (CSV file)", type="csv")

if uploaded_file is not None:
    with st.spinner("🧪 Brewing your data..."):
        temp_file_path = "Staging_Data/temp_data.csv"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        data = get_data(temp_file_path)
        
        if data is not None:
            st.success("✨ Data successfully summoned!")
            st.write(f"📊 Shape of your data realm: {data.shape}")
            
            with st.expander("👀 Peek at your data"):
                st.dataframe(data.head())
            
            if validate_data_for_dashboard(data):
                cleaned_data = clean_data(data)
                if cleaned_data is not None:
                    st.success("🧼 Data cleaning spell complete!")
                    
                    with st.expander("🔍 Inspect your squeaky clean data"):
                        st.dataframe(cleaned_data.head())
                    
                    perform_fe = st.radio("🧙‍♂️ Shall we enhance your data with some feature engineering magic?", ("Yes, please!", "No, thanks"), index=1)
                    
                    if perform_fe == "Yes, please!":
                        with st.spinner("🎩 Pulling new features out of the hat..."):
                            engineered_data, generated_code = feature_engineering(cleaned_data)
                        
                        if generated_code:
                            st.success("🌟 Feature engineering enchantment successful!")
                            with st.expander("🔮 Gaze upon your enhanced data"):
                                st.dataframe(engineered_data.head())
                        else:
                            st.info("🤔 Hmm, it seems your data was already quite magical. No new features added.")
                            engineered_data = cleaned_data
                    else:
                        st.info("👍 Keeping it simple, I see. No feature engineering performed.")
                        engineered_data = cleaned_data
                    
                    output_path = "Staging_Data/engineered_data.csv"
                    engineered_data.to_csv(output_path, index=False)
                    
                    start_time = time.time()
                    
                    with st.spinner("🧙‍♂️ Summoning the dashboard spirits..."):
                        dashboard_prompt = prompt_generator(engineered_data)
                        
                        llm = ChatAnthropic(
                            model="claude-3-5-sonnet-20240620",
                            temperature=0,
                            max_tokens=4096,
                            timeout=None,
                            max_retries=2,
                        )
                    
                    with st.spinner("🎨 Crafting your custom dashboard masterpiece..."):
                        response = llm.invoke(dashboard_prompt)
                        dashboard_code = response.content if hasattr(response, 'content') else str(response)
                    
                    with st.spinner("🔍 Giving your dashboard code a final polish..."):
                        correction_prompt = f"""
                        Review and correct the following Python code for a Dash dashboard. 
                        Make sure:
                        1. The charts are interacting with each other.
                        2. Filter has a select all feature (by default).
                        3. Reset Filters button should be working properly

                        The code should work with a pandas DataFrame named 'df' that contains the following columns:
                        {', '.join(engineered_data.columns)}

                        Here's the code to review:

                        {dashboard_code}

                        If you find any errors or potential improvements, provide ONLY the corrected version of the entire code. 
                        Do not include any explanations, comments, or anything other than the Python code itself.
                        If the code looks correct and doesn't need changes, return the original code as is.
                        """

                        correction_response = llm.invoke(correction_prompt)
                        corrected_code = correction_response.content if hasattr(correction_response, 'content') else str(correction_response)

                    end_time = time.time()
                    execution_time = round(end_time - start_time, 2)

                    output_directory = "Generated_Dashboards"
                    if not os.path.exists(output_directory):
                        os.makedirs(output_directory)
                    
                    output_filename = "gendb.py"
                    output_path = output_filename
                    
                    try:
                        with open(output_path, "w", encoding='utf-8') as f:
                            f.write(corrected_code)
                        st.success(f"🎉 Voila! Your dashboard is ready in just {execution_time} seconds! Let's take it for a spin!")
                    except Exception as e:
                        st.error(f"Oops! We hit a snag while saving your dashboard: {str(e)}")
                    
                    st.subheader("🚀 Your Custom Dashboard Code")
                    with st.expander("Click to reveal the magic"):
                        st.code(corrected_code, language="python")
                    
                    data_path = os.path.join(output_directory, "data.csv")
                    engineered_data.to_csv(data_path, index=False)
                    
                    st.subheader("🏃‍♂️ Run Your Dashboard")
                    st.info("""
                    Ready to see your dashboard in action? Here's how:
                    1. Open a new terminal or command prompt (your secret dashboard control center).
                    2. Navigate to the directory containing gendb.py (the dashboard's lair).
                    3. Cast this spell (run this command):
                       ```
                       python gendb.py
                       ```
                    4. Open your favorite web browser and journey to http://127.0.0.1:8050.
                    5. Behold your magnificent dashboard!
                    """)
                    
                    st.download_button(
                        label="📥 Download Your Dashboard Spell (Python Script)",
                        data=corrected_code,
                        file_name=output_filename,
                        mime="text/plain"
                    )
                    
                else:
                    st.error("🧹 Oops! Our cleaning spell fizzled. Please check your data and try again.")
            else:
                st.error("🚫 Data validation charm failed. Make sure your CSV file has proper column names and contains actual data.")
        else:
            st.error("📉 Uh-oh! We couldn't summon your data. Double-check your CSV file and give it another go.")

    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

st.sidebar.header("🧙‍♂️ About AUTO-DASH")
st.sidebar.info(
    "AUTO-DASH is your personal dashboard conjurer. It takes your CSV data and transforms it into an interactive Dash dashboard with a flick of its digital wand. "
    "Just upload your CSV file, and watch as AUTO-DASH weaves its magic to create a custom dashboard tailored to your data!"
)
st.sidebar.header("📚 Spell Instructions")
st.sidebar.markdown(
    """
    1. 📂 Upload your CSV scroll using the mystical file uploader.
    2. 👀 Review your data preview and decide if you want to sprinkle some feature engineering magic.
    3. ⏳ Wait patiently as we summon your dashboard from the digital realm.
    4. 📥 Download your generated dashboard spell (Python script).
    5. 🖥️ Cast the spell locally by following the arcane instructions provided.
    6. 🌐 Open the magic portal (URL) in your preferred browser to witness your dashboard in all its glory!
    """
)