
# Import necessary libraries
import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

def load_data():
    # Load the CSV file from the current directory
    df = pd.read_csv('data.csv')
    
    # Convert date columns to datetime
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    
    # Calculate age
    df['age'] = (datetime.now() - df['date_of_birth']).dt.days // 365
    
    return df

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
                        value=['Sales Manager', 'Marketing Specialist'],  # Default value as a list
                        multi=True,  # Enable multi-select
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
                dbc.Col([dcc.Graph(id='employee-count')], width=6),
                dbc.Col([dcc.Graph(id='salary-distribution')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='tenure-distribution')], width=6),
                dbc.Col([dcc.Graph(id='age-distribution')], width=6),
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
         Output('employee-count', 'figure'),
         Output('salary-distribution', 'figure'),
         Output('tenure-distribution', 'figure'),
         Output('age-distribution', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('dropdown-job-title', 'value'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(departments, job_titles, reset_clicks):
        # Filter the data based on the selected departments and job titles
        filtered_df = df[(df['department'].isin(departments)) & (df['job_title'].isin(job_titles))]
        
        # Calculate KPIs
        total_employees = len(filtered_df)
        avg_salary = filtered_df['salary'].mean()
        avg_tenure = (datetime.now() - filtered_df['hire_date']).dt.days.mean() // 365
        avg_age = filtered_df['age'].mean()
        
        # Create KPI indicators
        kpi_indicators = html.Div([
            create_kpi_card('Total Employees', total_employees, 0),
            create_kpi_card('Average Salary', avg_salary, 0),
            create_kpi_card('Average Tenure', avg_tenure, 0),
            create_kpi_card('Average Age', avg_age, 0)
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
        
        # Create charts
        employee_count = px.bar(filtered_df, x='department', y='employee_id', title='Employee Count by Department')
        employee_count = update_chart_layout(employee_count)
        
        salary_distribution = px.histogram(filtered_df, x='salary', title='Salary Distribution')
        salary_distribution = update_chart_layout(salary_distribution)
        
        tenure_distribution = px.histogram(filtered_df, x='age', title='Tenure Distribution')
        tenure_distribution = update_chart_layout(tenure_distribution)
        
        age_distribution = px.histogram(filtered_df, x='age', title='Age Distribution')
        age_distribution = update_chart_layout(age_distribution)
        
        return kpi_indicators, employee_count, salary_distribution, tenure_distribution, age_distribution

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

    return app

def main():
    df = load_data()
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()
