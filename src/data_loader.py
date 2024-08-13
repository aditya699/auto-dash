import os
import numpy as np
import pandas as pd
import logging
from datetime import datetime

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

if __name__ == "__main__":
    file_path = "path/to/your/csv/file.csv"  # Replace with your actual file path
    logging.info("Starting data loading process")
    data = get_data(file_path)
    if data is not None:
        logging.info("Data loading process completed successfully")
    else:
        logging.warning("Data loading process failed")