
# Import necessary libraries
import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

# Load environment variables from .env file
load_dotenv()

def create_app(df):
    # Initialize the Dash app
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Define color scheme for consistent styling
    colors = {
        'background': '#F7F7F7',  # Light gray background
        'text': '#333333',        # Dark gray text
        'primary': '#3498DB',     # Bright blue for primary elements
        'secondary': '#2ECC71',   # Green for secondary elements (positive changes)
        'accent': '#F39C12',      # Orange for accents
        'negative': '#E74C3C'     # Red for negative changes (used sparingly)
    }

    # Define styles
    kpi_style = {
        'textAlign': 'center',
        'padding': '20px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
        'margin': '10px',
        'width': '200px',
        'transition': 'all 0.3s ease'
    }

    filter_style = {
        'display': 'flex', 
        'justifyContent': 'space-between', 
        'alignItems': 'flex-end', 
        'margin': '20px auto', 
        'width': '90%',
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)'
    }

    # Layout of the dashboard
    app.layout = dbc.Container([
        html.Div([
            html.H1('Employee Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            # Filter section
            html.Div([
                html.Div([
                    html.Label('Department', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-department',
                        options=[{'label': i, 'value': i} for i in df.department.unique()],
                        value=['Sales'],  # Default value as a list
                        multi=True,  # Enable multi-select
                        style={'width': '300px'}  # Increased width to accommodate multiple selections
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Hire Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['hire_date'].min(),
                        end_date=df['hire_date'].max(),
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Button('Reset Filters', id='reset-button', n_clicks=0, 
                                    style={'padding': '10px 20px', 'backgroundColor': colors['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'all 0.3s ease'})
                ])
            ], style=filter_style),
            
            # KPI indicators section
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),
            
            # Charts section
            dbc.Row([
                dbc.Col([dcc.Graph(id='employee-salary')], width=6),
                dbc.Col([dcc.Graph(id='employee-gender')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='employee-performance')], width=6),
                dbc.Col([dcc.Graph(id='employee-age-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    # Callback function for updating the dashboard
    @callback(
        [Output('kpi-indicators', 'children'),
         Output('employee-salary', 'figure'),
         Output('employee-gender', 'figure'),
         Output('employee-performance', 'figure'),
         Output('employee-age-distribution', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(departments, start_date, end_date, reset_clicks):
        # Convert string dates to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filter the dataframe based on selected departments and date range
        dff = df[df.department.isin(departments) & 
                     (df.hire_date >= start_date) & 
                     (df.hire_date <= end_date)]
        
        # Calculate KPI values for the selected period
        total_employees = dff['employee_id'].nunique()
        average_salary = dff['salary'].mean()
        gender_distribution = dff['gender'].value_counts()
        job_titles = dff['job_title'].value_counts()
        age_distribution = dff['date_of_birth'].dt.year.value_counts().sort_index()
        
        # Calculate KPI values for 6 months ago
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[df.department.isin(departments) & 
                          (df.hire_date >= past_start_date) & 
                          (df.hire_date <= past_end_date)]
        
        past_total_employees = past_dff['employee_id'].nunique()
        past_average_salary = past_dff['salary'].mean()
        past_gender_distribution = past_dff['gender'].value_counts()
        past_job_titles = past_dff['job_title'].value_counts()
        past_age_distribution = past_dff['date_of_birth'].dt.year.value_counts().sort_index()
        
        # Calculate changes
        employees_change = total_employees - past_total_employees
        salary_change = average_salary - past_average_salary
        
        # Function to create a KPI card
        def create_kpi_card(title, value, change):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.0f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                    html.Div([
                        html.Span('▲' if change > 0 else '▼', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px'}),
                        html.Span(f'{abs(change):,.0f}', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px', 'marginLeft': '5px'})
                    ], style={'marginTop': '5px'})
                ])
            ], style=kpi_style)
        
        # Create KPI indicators
        kpi_indicators = html.Div([
            create_kpi_card('Total Employees', total_employees, employees_change),
            create_kpi_card('Average Salary', f'{average_salary:,