
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
            html.H1('Employee Insights Dashboard', style={
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
                        value=df.department.unique().tolist(),  # Default value as a list
                        multi=True,  # Enable multi-select
                        style={'width': '300px'}  # Increased width to accommodate multiple selections
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
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
                dbc.Col([dcc.Graph(id='employee-count')], width=6),
                dbc.Col([dcc.Graph(id='salary-distribution')], width=6),
            ], className='mb-4'),

            dbc.Row([
                dbc.Col([dcc.Graph(id='gender-distribution')], width=6),
                dbc.Col([dcc.Graph(id='department-salary')], width=6),
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
         Output('gender-distribution', 'figure'),
         Output('department-salary', 'figure')],
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

        # Apply cross-filtering based on chart interactions
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                # Reset all filters
                dff = df[df.department.isin(departments) & 
                         (df.hire_date >= start_date) & 
                         (df.hire_date <= end_date)]

        # Calculate KPI values for the selected period
        total_employees = dff['employee_id'].nunique()
        average_salary = dff['salary'].mean()

        # Calculate KPI values for 6 months ago
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[df.department.isin(departments) & 
                      (df.hire_date >= past_start_date) & 
                      (df.hire_date <= past_end_date)]

        past_total_employees = past_dff['employee_id'].nunique()
        past_average_salary = past_dff['salary'].mean()

        # Calculate changes
        employee_change = total_employees - past_total_employees
        salary_change = average_salary - past_average_salary

        # Function to create a KPI card
        def create_kpi_card(title, value, change):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.0f}' if isinstance(value, int) else f'{value:,.2f}', 
                              style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                    html.Div([
                        html.Span('▲' if change > 0 else '▼', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px'}),
                        html.Span(f'{abs(change):,.0f}' if isinstance(change, int) else f'{abs(change):,.2f}', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px', 'marginLeft': '5px'})
                    ], style={'marginTop': '5px'})
                ])
            ], style=kpi_style)

        # Create KPI indicators
        kpi_indicators = html.Div([
            create_kpi_card('Total Employees', total_employees, employee_change),
            create_kpi_card('Average Salary', average_salary, salary_change),
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
        employee_count = px.histogram(dff, x='department', title="Employee Count by Department",
                                   color_discrete_sequence=[colors['primary']], labels={'department': 'Department'})
        employee_count = update_chart_layout(employee_count)

        salary_distribution = px.histogram(dff, x='salary', nbins=10, title="Salary Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'salary':'Salary'})
        salary_distribution = update_chart_layout(salary_distribution)

        gender_distribution = px.pie(dff, names='gender', title="Gender Distribution",
                                    color_discrete_sequence=[colors['primary'], colors['secondary']])
        gender_distribution = update_chart_layout(gender_distribution)

        department_salary = px.box(dff, x='department', y='salary', title="Salary Distribution by Department",
                                   color_discrete_sequence=[colors['primary']], labels={'department':'Department', 'salary':'Salary'})
        department_salary = update_chart_layout(department_salary)

        return kpi_indicators, employee_count, salary_distribution, gender_distribution, department_salary    

    return app

def main():
    # Sample DataFrame (Replace with your actual data loading)
    data = {'employee_id': [1, 2, 3, 4, 5],
            'first_name': ['John', 'Jane', 'Michael', 'Emily', 'David'],
            'last_name': ['Doe', 'Doe', 'Smith', 'Jones', 'Brown'],
            'date_of_birth': pd.to_datetime(['1980-01-01', '1985-05-05', '1990-10-10', '1975-02-20', '1988-07-15']),
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
            'job_title': ['Analyst', 'Manager', 'Analyst', 'Manager', 'Analyst'],
            'department': ['Sales', 'Marketing', 'Sales', 'Marketing', 'Finance'],
            'salary': [60000, 80000, 65000, 90000, 70000],
            'hire_date': pd.to_datetime(['2020-01-15', '2019-06-20', '2021-02-10', '2018-08-05', '2022-03-20']),
            'email': ['john.doe@example.com', 'jane.doe@example.com', 'michael.smith@example.com', 'emily.jones@example.com', 'david.brown@example.com']}
    df = pd.DataFrame(data)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()

