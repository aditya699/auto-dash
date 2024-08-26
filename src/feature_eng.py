import pandas as pd
import numpy as np
import logging
from langchain_anthropic import ChatAnthropic

from langchain_experimental.tools import PythonAstREPLTool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ["ANTHROPIC_API_KEY"] = os.getenv('ANTHROPIC_API_KEY')
def generate_llm_prompt(data):
    """Generate a prompt for the LLM based on the dataframe structure, including examples."""
    columns = ", ".join(data.columns)
    
    prompt = f"""
    Given a pandas DataFrame 'df' with the following columns: {columns}

    Generate Python code to perform basic feature engineering tasks like this.:
    1. For any date columns, extract year and month.

    2. If 'first_name' and 'last_name' columns exist, combine them into a 'full_name' column.


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

    Please generate similar code for the given DataFrame, applying  transformations which you feel are appropriate.
    """
    return prompt

def transform_data_with_llm(data):
    """Use LLM to generate and execute data transformation code."""
    llm = ChatAnthropic(
                            model="claude-3-5-sonnet-20240620",
                            temperature=0,
                            max_tokens=4096,
                            timeout=None,
                            max_retries=2,
                        )
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