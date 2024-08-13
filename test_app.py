'''
Author -Aditya Bhatt 7:25 AM 13-08-2024

Objective-
1.Create a system that would generate code for dash and hence u will have a dashboard 
on the fly


'''
#Library import
import pandas as pd
import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
import logging
from datetime import timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
from langchain_google_genai import ChatGoogleGenerativeAI
from prompt_template import generate_prompt
from datetime import datetime
import json
load_dotenv()
file_path=os.environ.get('FILE_PATH')
os.environ["GOOGLE_API_KEY"]=os.environ.get('GEMINI_API_KEY')

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
# Set up logging
logging.basicConfig(filename='dashboard_generator.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

if not file_path:
    logging.error("FILE_PATH environment variable is not set")
    raise ValueError("FILE_PATH environment variable is not set")

# Set up logging

def get_data(filepath):
    """
    Load data from the given file path, replace missing values with 'NA',
    provide a basic analysis, and save the processed data to the Staging_Data folder.
    
    Args:
    filepath (str): Path to the CSV file in the Raw_Data folder.
    
    Returns:
    pd.DataFrame: Dataframe with missing values replaced by 'NA'.
    dict: Data analysis results.
    """
    try:
        # Attempt to read the CSV file
        logging.info(f"Attempting to read file: {filepath}")
        df = pd.read_csv(filepath)
        
        # Log initial data shape
        logging.info(f"Data shape: {df.shape}")
        
        # Replace all missing values with 'NA'
        df = df.fillna('NA')
        logging.info("Replaced all missing values with 'NA'")
        
        # Basic analysis
        analysis = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "na_counts": (df == 'NA').sum().to_dict(),
            "unique_values": {col: df[col].nunique() for col in df.columns}
        }
        
        # Convert date columns to datetime
        date_columns = df.columns[df.columns.str.contains('date', case=False)]
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].fillna('NA')  # Replace NaT with 'NA' after conversion
                logging.info(f"Converted '{col}' to datetime")
            except Exception as e:
                logging.error(f"Failed to convert '{col}' to datetime: {str(e)}")
        
        # Save processed data to Staging_Data folder
        filename = os.path.basename(filepath)
        staging_path = os.path.join('Staging_Data', filename)
        df.to_csv(staging_path, index=False)
        logging.info(f"Saved processed data to {staging_path}")
        
        # Log analysis results
        logging.info("Data analysis completed")
        for key, value in analysis.items():
            if key != "dtypes":  # dtypes can be too verbose for logging
                logging.info(f"{key}: {value}")
        
        return df, analysis
    
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise
    except pd.errors.EmptyDataError:
        logging.error(f"Empty CSV file: {filepath}")
        raise
    except pd.errors.ParserError:
        logging.error(f"Parser error while reading CSV: {filepath}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error occurred while processing {filepath}: {str(e)}")
        raise


try:
    df, data_analysis = get_data(file_path)
    logging.info("Data loading, processing, and analysis completed successfully")
except Exception as e:
    logging.error(f"Failed to process data: {str(e)}")
    raise

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def get_data_insights(df):
    logging.info("Starting data insights extraction")
    
    insights = {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numerical_columns": df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
        "date_columns": df.select_dtypes(include=['datetime64']).columns.tolist(),
        "unique_values": {col: int(df[col].nunique()) for col in df.columns},
        "sample_data": json.loads(df.head().to_json(orient='records', date_format='iso'))
    }
    
    logging.info(f"Found {len(insights['columns'])} total columns")
    logging.info(f"Numerical columns: {', '.join(insights['numerical_columns'])}")
    logging.info(f"Categorical columns: {', '.join(insights['categorical_columns'])}")
    logging.info(f"Date columns: {', '.join(insights['date_columns'])}")
    
    # Simplified summary statistics
    summary_stats = {}
    for col in insights['numerical_columns']:
        summary_stats[col] = {
            "mean": float(df[col].mean()),
            "median": float(df[col].median()),
            "min": float(df[col].min()),
            "max": float(df[col].max())
        }
        logging.info(f"Summary stats for {col}: {summary_stats[col]}")
    
    insights["summary_stats"] = summary_stats
    
    # Log unique value counts for categorical columns
    for col in insights['categorical_columns']:
        unique_count = insights['unique_values'][col]
        logging.info(f"Column '{col}' has {unique_count} unique values")
    
    # Handle date columns
    for col in insights['date_columns']:
        insights[f"{col}_min"] = df[col].min().isoformat()
        insights[f"{col}_max"] = df[col].max().isoformat()
        logging.info(f"Date range for {col}: {insights[f'{col}_min']} to {insights[f'{col}_max']}")
    
    logging.info("Data insights extraction completed")
    return insights

try:
    df, data_analysis = get_data(file_path)
    logging.info("Data loading, processing, and analysis completed successfully")
except Exception as e:
    logging.error(f"Failed to process data: {str(e)}")
    raise

try:
    logging.info("Attempting to extract data insights")
    data_insights = get_data_insights(df)
    logging.info("Data insights extracted successfully")
except Exception as e:
    logging.error(f"Error occurred while extracting data insights: {str(e)}")
    data_insights = None

def generate_dashboard_code(data_insights):
    prompt = generate_prompt(data_insights)
    try:
        response = llm.invoke(prompt)
        generated_code = response.content
        
        # Extract only the Python code from the response
        code_start = generated_code.find("### BEGIN DASH CODE ###")
        code_end = generated_code.rfind("### END DASH CODE ###")
        if code_start != -1 and code_end != -1:
            generated_code = generated_code[code_start + len("### BEGIN DASH CODE ###"):code_end].strip()
        
        logging.info("Dashboard code generated successfully")
        return generated_code
    except Exception as e:
        logging.error(f"Error generating dashboard code: {str(e)}")
        return None

def update_dashboard_file(generated_code):
    try:
        with open('generated_dashboard.py', 'w',encoding='utf-8') as f:
            f.write(generated_code)
        logging.info("Dashboard code written to generated_dashboard.py")
    except Exception as e:
        logging.error(f"Error writing dashboard code to file: {str(e)}")

def main():
    generated_code = generate_dashboard_code(data_insights)
    if generated_code:
        update_dashboard_file(generated_code)
        print("Dashboard code generated and saved to generated_dashboard.py")
        print("You can now run this file to launch your Dash application.")
    else:
        print("Failed to generate dashboard code. Check the logs for more information.")

if __name__ == '__main__':
    main()