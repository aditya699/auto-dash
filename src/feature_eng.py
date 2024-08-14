import pandas as pd
import numpy as np
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.tools import PythonAstREPLTool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv('GEMINI_API_KEY')

def generate_llm_prompt(data):
    """Generate a prompt for the LLM based on the dataframe structure, including examples."""
    columns = ", ".join(data.columns)
    
    prompt = f"""
    Given a pandas DataFrame 'df' with the following columns: {columns}

    Generate Python code to perform these basic feature engineering tasks:
    1. For any date columns, extract year and month.

    2. If 'first_name' and 'last_name' columns exist, combine them into a 'full_name' column.

    Only perform these tasks if applicable. Do not add any other transformations.

    Here are two examples of the kind of code we're looking for:

    Example 1 (for a date column):
    ```python
    if 'order_date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['order_date']):
        df['order_year'] = df['order_date'].dt.year
        df['order_month'] = df['order_date'].dt.month
        df['order_day'] = df['order_date'].dt.day
    ```

    Example 2 (for string columns and name combination):
    ```python

    if 'first_name' in df.columns and 'last_name' in df.columns:
        df['full_name'] = df['first_name'] + ' ' + df['last_name']
    ```

    Please generate similar code for the given DataFrame, applying these transformations where appropriate.
    """
    return prompt

def transform_data_with_llm(data):
    """Use LLM to generate and execute data transformation code."""
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    prompt = generate_llm_prompt(data)
    
    try:
        response = llm.invoke(prompt)
        code = response.content
        logging.info("LLM generated transformation code")
        
        locals_dict = {"df": data.copy(), "pd": pd, "np": np}
        tool = PythonAstREPLTool(locals=locals_dict)
        result = tool.run(code)
        logging.info("Transformation code executed successfully")
        
        return locals_dict["df"], code
    except Exception as e:
        logging.error(f"Error in data transformation: {str(e)}")
        return data, None

def feature_engineering(data):
    """Perform feature engineering on the data."""
    transformed_data, generated_code = transform_data_with_llm(data)
    return transformed_data, generated_code