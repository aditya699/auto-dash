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
load_dotenv()
file_path=os.environ.get('FILE_PATH')

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
    data, data_analysis = get_data(file_path)
    logging.info("Data loading, processing, and analysis completed successfully")
except Exception as e:
    logging.error(f"Failed to process data: {str(e)}")
    raise


