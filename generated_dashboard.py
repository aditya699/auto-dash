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

def load_data():
    while True:
        try:
            n = os.environ.get('FILE_PATH')
            df = pd.read_csv(n)
            df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
            df['hire_date'] = pd.to_datetime(df['hire_date'])
            return df
        except FileNotFoundError:
            print("File not found. Please enter a valid file path.")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

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
                        value='IT',
                        style={'width': '180px'}
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
                dbc.Col([dcc.Graph(id='job-title-salary')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='gender-distribution')], width=6),
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
         Output('employee-salary', 'figure'),
         Output('job-title-salary', 'figure'),
         Output('gender-distribution', 'figure'),
         Output('age-distribution', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('employee-salary', 'clickData'),
         Input('job-title-salary', 'clickData'),
         Input('gender-distribution', 'clickData'),
         Input('age-distribution', 'selectedData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(department, start_date, end_date, employee_click, job_title_click, gender_click, age_selection, reset_clicks):
        # Convert string dates to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filter the dataframe based on selected department and hire date range
        dff = df[(df.department == department) & 
                 (df.hire_date >= start_date) & 
                 (df.hire_date <= end_date)]
        
        # Apply cross-filtering based on chart interactions
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                # Reset all filters
                dff = df[(df.department == department) & 
                         (df.hire_date >= start_date) & 
                         (df.hire_date <= end_date)]
            elif input_id == 'employee-salary' and employee_click:
                employee = employee_click['points'][0]['x']
                dff = dff[dff['employee_id'] == employee]
            elif input_id == 'job-title-salary' and job_title_click:
                job_title = job_title_click['points'][0]['x']
                dff = dff[dff['job_title'] == job_title]
            elif input_id == 'gender-distribution' and gender_click:
                gender = gender_click['points'][0]['x']
                dff = dff[dff['gender'] == gender]
            elif input_id == 'age-distribution' and age_selection:
                age_range = [age_selection['range']['x'][0], age_selection['range']['x'][1]]
                dff = dff[(dff['age'] >= age_range[0]) & (dff['age'] <= age_range[1])]

        
        # Calculate KPI values for the selected period
        total_salary = dff['salary'].sum()
        total_employees = dff['employee_id'].nunique()
        average_salary = dff['salary'].mean()
        
        # Calculate KPI values for 6 months ago
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[(df.department == department) & 
                      (df.hire_date >= past_start_date) & 
                      (df.hire_date <= past_end_date)]
        
        past_total_salary = past_dff['salary'].sum()
        past_total_employees = past_dff['employee_id'].nunique()
        past_average_salary = past_dff['salary'].mean()
        
        # Calculate changes
        salary_change = total_salary - past_total_salary
        employees_change = total_employees - past_total_employees
        average_salary_change = average_salary - past_average_salary
        
        # Function to create a KPI card
        def create_kpi_card(title, value, change):
                return html.Div([
                    html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                    html.Div([
                        html.Span(f'{value:,.0f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                        html.Div([
                            html.Span('^' if change > 0 else 'v', 
                                    style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px'}),
                            html.Span(f'{abs(change):,.0f}', 
                                    style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px', 'marginLeft': '5px'})
                        ], style={'marginTop': '5px'})
                    ])
                ], style=kpi_style)

        
        # Create KPI indicators
        kpi_indicators = html.Div([
            create_kpi_card('Total Salary', total_salary, salary_change),
            create_kpi_card('Total Employees', total_employees, employees_change),
            create_kpi_card('Avg Salary', average_salary, average_salary_change)
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
        
        # Create graphs with interactivity
        employee_salary = px.bar(dff, x='employee_id', y='salary', title="Employee Salary Analysis",
                                   color_discrete_sequence=[colors['primary']], labels={'employee_id': 'Employee ID', 'salary': 'Salary'})
        employee_salary = update_chart_layout(employee_salary)
        
        job_title_salary = px.bar(dff, x='job_title', y='salary', title="Job Title Salary Analysis",
                               color_discrete_sequence=[colors['primary']], labels={'job_title':'Job Title','salary':'Salary'})
        job_title_salary = update_chart_layout(job_title_salary)
        
        gender_distribution = px.histogram(dff, x='gender', title="Gender Distribution",
                                       color_discrete_sequence=[colors['primary']], labels={'gender':'Gender'})
        gender_distribution = update_chart_layout(gender_distribution)
        
        age_distribution = px.histogram(dff, x='date_of_birth', nbins=10, title="Employee Age Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'date_of_birth':'Date of Birth'})
        age_distribution = update_chart_layout(age_distribution)
        
        return kpi_indicators, employee_salary, job_title_salary, gender_distribution, age_distribution    

    return app

def main():
    df = load_data()
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()