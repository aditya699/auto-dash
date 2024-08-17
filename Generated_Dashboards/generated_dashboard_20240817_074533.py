
# Import necessary libraries
import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
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
                        value=['Sales', 'Marketing'],  # Default value as a list
                        multi=True,  # Enable multi-select
                        style={'width': '300px'}  # Increased width to accommodate multiple selections
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Job Title', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-job-title',
                        options=[{'label': i, 'value': i} for i in df.job_title.unique()],
                        value=['Manager', 'Analyst'],  # Default value as a list
                        multi=True,  # Enable multi-select
                        style={'width': '300px'}  # Increased width to accommodate multiple selections
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Gender', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-gender',
                        options=[{'label': i, 'value': i} for i in df.gender.unique()],
                        value=['Male', 'Female'],  # Default value as a list
                        multi=True,  # Enable multi-select
                        style={'width': '300px'}  # Increased width to accommodate multiple selections
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
                dbc.Col([dcc.Graph(id='employee-age-distribution')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='employee-tenure')], width=6),
                dbc.Col([dcc.Graph(id='employee-gender-distribution')], width=6),
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
         Output('employee-age-distribution', 'figure'),
         Output('employee-tenure', 'figure'),
         Output('employee-gender-distribution', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('dropdown-job-title', 'value'),
         Input('dropdown-gender', 'value'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(departments, job_titles, genders, reset_clicks):
        # Filter the dataframe based on selected filters
        dff = df[df.department.isin(departments) & 
                 df.job_title.isin(job_titles) & 
                 df.gender.isin(genders)]
        
        # Apply reset filter if the button is clicked
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df
        
        # Calculate KPI values for the selected filters
        total_employees = dff.shape[0]
        average_salary = dff['salary'].mean()
        average_age = dff['date_of_birth'].apply(lambda x: (datetime.now() - x).days // 365).mean()
        average_tenure = (datetime.now() - dff['hire_date'].mean()).days // 365
        
        # Function to create a KPI card
        def create_kpi_card(title, value):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.0f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                ], style={'marginTop': '5px'})
            ], style=kpi_style)
        
        # Create KPI indicators
        kpi_indicators = html.Div([
            create_kpi_card('Total Employees', total_employees),
            create_kpi_card('Average Salary', average_salary),
            create_kpi_card('Average Age', average_age),
            create_kpi_card('Average Tenure', average_tenure)
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
        
        # Function to update chart layout
        def update_chart_layout(fig):
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
                font_color=colors['text'],
                title_font_size=20,
                title_font_color=colors['primary'],
                legend_title_font_color=colors['primary'],
                legend_title_font_size=14,
                legend_font_size=12,
                clickmode='event+select'
            )
            fig.update_xaxes(showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            return fig
        
        # Create graphs
        employee_salary = px.histogram(dff, x='salary', nbins=10, title="Employee Salary Distribution",
                                       color_discrete_sequence=[colors['primary']], labels={'salary':'Salary'})
        employee_salary = update_chart_layout(employee_salary)
        
        employee_age_distribution = px.histogram(dff, x='date_of_birth', nbins=10, title="Employee Age Distribution",
                                                color_discrete_sequence=[colors['primary']], labels={'date_of_birth':'Date of Birth'})
        employee_age_distribution = update_chart_layout(employee_age_distribution)
        
        employee_tenure = px.histogram(dff, x='hire_date', nbins=10, title="Employee Tenure Distribution",
                                       color_discrete_sequence=[colors['primary']], labels={'hire_date':'Hire Date'})
        employee_tenure = update_chart_layout(employee_tenure)
        
        employee_gender_distribution = px.pie(dff, names='gender', title="Employee Gender Distribution",
                                              color_discrete_sequence=[colors['primary'], colors['secondary']])
        employee_gender_distribution = update_chart_layout(employee_gender_distribution)
        
        return kpi_indicators, employee_salary, employee_age_distribution, employee_tenure, employee_gender_distribution

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()
