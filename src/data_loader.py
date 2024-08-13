import pandas as pd
import os
import logging
from datetime import datetime
import numpy as np
def load_data(file_path):
    """
    Load data from the given file path, replace missing values with 'NA',
    provide a basic analysis, and save the processed data to the Staging_Data folder.
    
    Args:
    file_path (str): Path to the CSV file.
    
    Returns:
    pd.DataFrame: Dataframe with missing values replaced by 'NA'.
    dict: Data analysis results.
    """
    try:
        logging.info(f"Attempting to read file: {file_path}")
        df = pd.read_csv(file_path)
        
        logging.info(f"Data shape: {df.shape}")
        
        df = df.fillna('NA')
        logging.info("Replaced all missing values with 'NA'")
        
        analysis = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "na_counts": (df == 'NA').sum().to_dict(),
            "unique_values": {col: df[col].nunique() for col in df.columns}
        }
        
        date_columns = df.columns[df.columns.str.contains('date', case=False)]
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].fillna('NA')
                logging.info(f"Converted '{col}' to datetime")
            except Exception as e:
                logging.error(f"Failed to convert '{col}' to datetime: {str(e)}")
        
        filename = os.path.basename(file_path)
        staging_path = os.path.join('Staging_Data', filename)
        df.to_csv(staging_path, index=False)
        logging.info(f"Saved processed data to {staging_path}")
        
        for key, value in analysis.items():
            if key != "dtypes":
                logging.info(f"{key}: {value}")
        
        return df, analysis
    
    except Exception as e:
        logging.error(f"Error in load_data: {str(e)}")
        raise

def convert_to_serializable(obj):
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return str(obj)

def get_data_insights(df):
    logging.info("Starting data insights extraction")
    
    insights = {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numerical_columns": df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
        "date_columns": df.select_dtypes(include=['datetime64']).columns.tolist(),
        "unique_values": {col: int(df[col].nunique()) for col in df.columns},
        "sample_data": df.head().applymap(convert_to_serializable).to_dict(orient='records')
    }
    
    summary_stats = {}
    for col in insights['numerical_columns']:
        summary_stats[col] = {
            "mean": float(df[col].mean()),
            "median": float(df[col].median()),
            "min": convert_to_serializable(df[col].min()),
            "max": convert_to_serializable(df[col].max())
        }
    
    insights["summary_stats"] = summary_stats
    
    for col in insights['date_columns']:
        insights[f"{col}_min"] = convert_to_serializable(df[col].min())
        insights[f"{col}_max"] = convert_to_serializable(df[col].max())
    
    # Convert all values in insights to JSON serializable format
    insights = {k: convert_to_serializable(v) for k, v in insights.items()}
    
    logging.info("Data insights extraction completed")
    return insights

