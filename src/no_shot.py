import pandas as pd
import numpy as np

def prompt_generator(DataFrame):
    data = DataFrame
    data_dtypes = data.dtypes
    column_descriptions = "\n".join([f"- {col}: {dtype}" for col, dtype in data_dtypes.items()])
    
    prompt = f"""
    You are an expert in creating dashboards using Dash. 
    
    Instructions-

    1. Create KPI cards and charts which will give the business owner meaningful insights about data.
    2. Make sure filters have a select all option.
    3. Charts should interact with each Other.
    4. Reset Filters button is must.
    5. The code will always run this file df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    
    New Dataset Information:
    
    The DataFrame contains the following columns and their respective data types:
    {column_descriptions}

    Here's an example of how to structure your code for a similar dataset:

    import os
    from dash import Dash, html, dcc, callback, Output, Input, ctx
    import plotly.express as px
    import pandas as pd
    from datetime import datetime, timedelta
    from dotenv import load_dotenv
    import dash_bootstrap_components as dbc

    load_dotenv()

    def create_app(df):
        # Data preprocessing
        df['date_column'] = pd.to_datetime(df['date_column'])
        
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        # Define color scheme and styles
        colors = {{
            'background': '#F7F7F7',
            'text': '#333333',
            'primary': '#3498DB',
            'secondary': '#2ECC71',
            'accent': '#F39C12',
            'negative': '#E74C3C'
        }}
        
        # App layout
        app.layout = dbc.Container([
            # Title
            html.H1('Dashboard Title'),
            
            # Filters
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='dropdown-filter', multi=True),
                    dcc.DatePickerRange(id='date-range-filter'),
                    html.Button('Reset Filters', id='reset-button')
                ])
            ]),
            
            # KPI Cards
            html.Div(id='kpi-cards'),
            
            # Charts
            dbc.Row([
                dbc.Col([dcc.Graph(id='chart1')]),
                dbc.Col([dcc.Graph(id='chart2')])
            ]),
            dbc.Row([
                dbc.Col([dcc.Graph(id='chart3')]),
                dbc.Col([dcc.Graph(id='chart4')])
            ])
        ])
        
        @callback(
            [Output('kpi-cards', 'children'),
             Output('chart1', 'figure'),
             Output('chart2', 'figure'),
             Output('chart3', 'figure'),
             Output('chart4', 'figure')],
            [Input('dropdown-filter', 'value'),
             Input('date-range-filter', 'start_date'),
             Input('date-range-filter', 'end_date'),
             Input('reset-button', 'n_clicks'),
             Input('chart1', 'selectedData'),
             Input('chart2', 'clickData'),
             Input('chart3', 'selectedData'),
             Input('chart4', 'clickData')]
        )
        def update_dashboard(filter_value, start_date, end_date, n_clicks, chart1_data, chart2_data, chart3_data, chart4_data):
            # Filter data based on inputs
            # Create KPI cards
            # Create charts
            # Implement cross-filtering logic
            # Return updated KPI cards and charts
        
        return app

    def main():
        df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
        df = pd.read_csv(df_path)
        app = create_app(df)
        app.run(debug=True)

    if __name__ == '__main__':
        main()

    Based on the example above and the provided dataset information, create a complete Dash application code. The output should be only Python code, without any comments or markdown. Begin the code with the necessary imports and end with the main function and the if __name__ == '__main__': block.
    """
    return prompt