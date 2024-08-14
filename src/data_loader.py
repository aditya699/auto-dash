import pandas as pd
import logging
from datetime import datetime
import os
# Set up logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = f"data_loader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_filepath = os.path.join(log_directory, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler()
    ]
)
def get_data(file_path):
    """This function will be used to load data (CSV)

    Args:
        file_path (str): Filepath
    """
    logging.info(f"Attempting to load data from {file_path}")
    try:
        data = pd.read_csv(file_path)
        logging.info("Data successfully loaded")
        logging.info(f"Data shape: {data.shape}")
        logging.info(f"Columns: {', '.join(data.columns)}")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except pd.errors.EmptyDataError:
        logging.error(f"Empty CSV file: {file_path}")
    except pd.errors.ParserError:
        logging.error(f"Error parsing CSV file: {file_path}")
    except Exception as e:
        logging.error(f"Error loading the file: {str(e)}")
    
    return None

def clean_data(data):
    """This function will be used to clean the loaded data

    Args:
        data (pd.DataFrame): Loaded data
    """
    logging.info("Starting data cleaning process")
    try:
        # Handle null values
        nulls = data.isnull().sum()
        logging.info(f"Null values in each column:\n{nulls}")
        
        data = data.fillna("NA")
        logging.info("Replaced null values with 'NA'")
        
        # Convert date columns to datetime
        date_columns = data.columns[data.columns.str.contains('date', case=False)]
        for col in date_columns:
            try:
                data[col] = pd.to_datetime(data[col], errors='coerce')
                data[col] = data[col].fillna('NA')  # Replace NaT with 'NA' after conversion
                logging.info(f"Converted '{col}' to datetime")
            except Exception as e:
                logging.error(f"Failed to convert '{col}' to datetime: {str(e)}")
        
        logging.info("Data cleaning process completed successfully")
        return data
    except Exception as e:
        logging.error(f"Error during data cleaning: {str(e)}")
        return None

def validate_data_for_dashboard(data):
    """
    Perform basic validation checks on the data.
    
    Args:
        data (pd.DataFrame): The data to validate
    
    Returns:
        bool: True if data passes basic checks, False otherwise
    """
    logging.info("Starting basic data validation for dashboard")
    
    # Check if data is not empty
    if data.empty:
        logging.error("Data is empty")
        return False
    
    # Check if there are any columns
    if len(data.columns) == 0:
        logging.error("No columns found in the data")
        return False
    
    # Check for duplicate column names
    if len(data.columns) != len(set(data.columns)):
        logging.error("Duplicate column names detected")
        return False
    
    # Check if column names are all strings (not numbers)
    if not all(isinstance(col, str) for col in data.columns):
        logging.error("Non-string column names detected")
        return False
    
    # Check if there's at least one row of data (excluding header)
    if len(data) == 0:
        logging.error("No data rows found")
        return False
    
    logging.info("Basic data validation completed successfully")
    return True