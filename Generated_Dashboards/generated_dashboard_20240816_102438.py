Here's the modified Dash application code that creates a tailored dashboard for the new dataset:

```python
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
                        value=['Sales'],  # Default value as a list
                        multi=True,  # Enable multi-select
                        style={'width': '300px'}  # Increased width to accommodate multiple selections
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Job Title', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-job-title',
                        options=[{'label': i, 'value': i} for i in df.job_title.unique()],
                        value=['Sales Representative'],  # Default value as a list
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
                dbc.Col([dcc.Graph(id='employee-age-distribution')], width=6),
                dbc.Col([dcc.Graph(id='employee-salary-distribution')], width=6),
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
         Output('employee-age-distribution', 'figure'),
         Output('employee-salary-distribution', 'figure'),
         Output('employee-tenure', 'figure'),
         Output('employee-gender-distribution', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('dropdown-job-title', 'value'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(departments, job_titles, reset_clicks):
        # Filter the dataframe based on selected departments and job titles
        dff = df[df.department.isin(departments) & df.job_title.isin(job_titles)]
        
        # Apply cross-filtering based on chart interactions
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                # Reset all filters
                dff = df
        
        # Calculate KPI values for the selected filters
        total_employees = len(dff)
        average_salary = dff['salary'].mean()
        average_tenure = (datetime.now() - dff['hire_date']).dt.days.mean() / 365.25
        
        # Calculate KPI values for 6 months ago
        past_start_date = datetime.now() - timedelta(days=180)
        past_dff = df[df.hire_date <= past_start_date]
        past_total_employees = len(past_dff)
        past_average_salary = past_dff['salary'].mean()
        past_average_tenure = (past_start_date - past_dff['hire_date']).dt.days.mean() / 365.25
        
        # Calculate changes
        employees_change = total_employees - past_total_employees
        salary_change = average_salary - past_average_salary
        tenure_change = average_tenure - past_average_tenure
        
        # Function to create a KPI card
        def create_kpi_card(title, value, change):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.0f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                    html.Div([
                        html.Span('▲' if change > 0 else '▼', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px'}),
                        html.Span(f'{abs(change):,.2f}', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px', 'marginLeft': '5px'})
                    ], style={'marginTop': '5px'})
                ])
            ], style=kpi_style)
        
        # Create KPI indicators
        kpi_indicators = html.Div([
            create_kpi_card('Total Employees', total_employees, employees_change),
            create_kpi_card('Average Salary', average_salary, salary_change),
            create_kpi_card('Average Tenure (Years)', average_tenure, tenure_change),
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
        employee_age_distribution = px.histogram(dff, x='date_of_birth', nbins=10, title="Employee Age Distribution",
                                                color_discrete_sequence=[colors['primary']], labels={'date_of_birth': 'Age'})
        employee_age_distribution = update_chart_layout(employee_age_distribution)
        
        employee_salary_distribution = px.histogram(dff, x='salary', nbins=10, title="Employee Salary Distribution",
                                                   color_discrete_sequence=[colors['primary']], labels={'salary': 'Salary'})
        employee_salary_distribution = update_chart_layout(employee_salary_distribution)
        
        employee_tenure = px.bar(dff, x='first_name', y='hire_date', title="Employee Tenure",
                                color_discrete_sequence=[colors['primary']], labels={'first_name': 'Employee', 'hire_date': 'Hire Date'})
        employee_tenure = update_chart_layout(employee_tenure)
        
        employee_gender_distribution = px.pie(dff, names='gender', title="Employee Gender Distribution",
                                              color_discrete_sequence=[colors['primary'], colors['secondary']])
        employee_gender_distribution = update_chart_layout(employee_gender_distribution)
        
        return kpi_indicators, employee_age_distribution, employee_salary_distribution, employee_tenure, employee_gender_distribution

    return app

def main():
    df = pd.DataFrame({
        'employee_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'first_name': ['John', 'Jane', 'Bob', 'Alice', 'Tom', 'Emily', 'David', 'Sarah', 'Michael', 'Jessica'],
        'last_name': ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Wilson', 'Anderson', 'Thompson', 'Martinez'],
        'date_of_birth': ['1985-05-15', '1990-08-22', '1978-12-03', '1982-03-28', '1975-11-09', '1988-06-17', '1992-02-14', '1980-09-01', '1987-04-30', '1983-07-25'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'job_title': ['Sales Representative', 'Sales Representative', 'Manager', 'Sales Representative', 'Sales Representative', 'Manager', 'Sales Representative', 'Sales Representative', 'Sales Representative', 'Sales Representative'],
        'department': ['Sales', 'Sales', 'Sales', 'Sales', 'Sales', 'Sales', 'Sales', 'Sales', 'Sales', 'Sales'],
        'salary': [50000, 55000, 80000, 52000, 48000, 75000, 53000, 51000, 49000, 54000],
        'hire_date': ['2018-01-01', '2019-03-15', '2015-06-01', '2017-09-01', '2020-02-01', '2016-04-01', '2021-05-01', '2018-11-01', '2019-08-01', '2017-02-01']
    })
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['age'] = (datetime.now() - df['date_of_birth']).dt.days // 365
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()
```

Key changes:

1. Analyzed the new data columns and determined the following KPIs: Total Employees, Average Salary, and Average Tenure.
2. Modified the KPI cards to display the relevant metrics based on the new dataset.
3. Adjusted the charts to visualize the new data effectively:
   - Employee Age Distribution
   - Employee Salary Distribution
   - Employee Tenure
   - Employee Gender Distribution
4. Updated the filter section to use the 'department' and 'job_title' columns from the new dataset.
5. Ensured that all variable names, column references, and data manipulations are consistent with the new DataFrame structure.

The dashboard now provides a comprehensive overview of the employee data, including insights into the age distribution, salary distribution, tenure, and gender distribution of the workforce. The filter options allow the business person to explore the data based on department and job title.