
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
                    html.Label('Department',
                               style={'fontWeight': 'bold', 'marginBottom': '5px',
                                      'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-department',
                        options=[{'label': i, 'value': i} for i in df.department.unique()],
                        value=df.department.iloc[0],
                        style={'width': '180px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range (Hire Date)',
                               style={'fontWeight': 'bold', 'marginBottom': '5px',
                                      'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['hire_date'].min(),
                        end_date=df['hire_date'].max(),
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Button('Reset Filters', id='reset-button', n_clicks=0,
                                style={'padding': '10px 20px', 'backgroundColor': colors['accent'],
                                       'color': 'white', 'border': 'none', 'borderRadius': '5px',
                                       'cursor': 'pointer', 'transition': 'all 0.3s ease'})
                ])
            ], style=filter_style),

            # KPI indicators section
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),

            # Charts section
            dbc.Row([
                dbc.Col([dcc.Graph(id='salary-by-gender')], width=6),
                dbc.Col([dcc.Graph(id='employee-count-by-job-title')], width=6),
            ], className='mb-4'),

            dbc.Row([
                dbc.Col([dcc.Graph(id='average-salary-by-department')], width=6),
                dbc.Col([dcc.Graph(id='employee-hire-date-distribution')], width=6),
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
         Output('salary-by-gender', 'figure'),
         Output('employee-count-by-job-title', 'figure'),
         Output('average-salary-by-department', 'figure'),
         Output('employee-hire-date-distribution', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('salary-by-gender', 'clickData'),
         Input('employee-count-by-job-title', 'clickData'),
         Input('average-salary-by-department', 'clickData'),
         Input('employee-hire-date-distribution', 'selectedData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(department, start_date, end_date, gender_click, job_title_click,
                         department_click, hire_date_selection, reset_clicks):
        # Convert string dates to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter the dataframe based on selected department and date range
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
            elif input_id == 'salary-by-gender' and gender_click:
                gender = gender_click['points'][0]['x']
                dff = dff[dff['gender'] == gender]
            elif input_id == 'employee-count-by-job-title' and job_title_click:
                job_title = job_title_click['points'][0]['x']
                dff = dff[dff['job_title'] == job_title]
            elif input_id == 'average-salary-by-department' and department_click:
                department = department_click['points'][0]['x']
                dff = dff[dff['department'] == department]
            elif input_id == 'employee-hire-date-distribution' and hire_date_selection:
                hire_date_range = [hire_date_selection['range']['x'][0],
                                   hire_date_selection['range']['x'][1]]
                dff = dff[(dff['hire_date'] >= hire_date_range[0]) &
                          (dff['hire_date'] <= hire_date_range[1])]

        # Calculate KPI values for the selected period
        total_employees = dff['employee_id'].nunique()
        average_salary = dff['salary'].mean()

        # Calculate KPI values for 6 months ago
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[(df.department == department) &
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
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px',
                                      'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.0f}' if isinstance(value, int) else f'{value:,.2f}',
                              style={'fontSize': '28px', 'fontWeight': 'bold',
                                     'color': colors['primary']}),
                    html.Div([
                        html.Span('▲' if change > 0 else '▼',
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'],
                                         'fontSize': '18px'}),
                        html.Span(f'{abs(change):,.0f}' if isinstance(change, int) else f'{abs(change):,.2f}',
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'],
                                         'fontSize': '18px', 'marginLeft': '5px'})
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
        salary_by_gender = px.box(dff, x='gender', y='salary',
                                   title="Salary Distribution by Gender",
                                   color_discrete_sequence=[colors['primary']],
                                   labels={'gender': 'Gender', 'salary': 'Salary'})
        salary_by_gender = update_chart_layout(salary_by_gender)

        employee_count_by_job_title = px.histogram(dff, x='job_title',
                                                    title="Employee Count by Job Title",
                                                    color_discrete_sequence=[colors['primary']],
                                                    labels={'job_title': 'Job Title'})
        employee_count_by_job_title = update_chart_layout(employee_count_by_job_title)

        average_salary_by_department = px.bar(dff.groupby('department', as_index=False)['salary'].mean(),
                                               x='department', y='salary',
                                               title="Average Salary by Department",
                                               color_discrete_sequence=[colors['primary']],
                                               labels={'department': 'Department', 'salary': 'Average Salary'})
        average_salary_by_department = update_chart_layout(average_salary_by_department)

        employee_hire_date_distribution = px.histogram(dff, x='hire_date', nbins=10,
                                                        title="Employee Hire Date Distribution",
                                                        color_discrete_sequence=[colors['primary']],
                                                        labels={'hire_date': 'Hire Date'})
        employee_hire_date_distribution = update_chart_layout(
            employee_hire_date_distribution)

        return kpi_indicators, salary_by_gender, employee_count_by_job_title, average_salary_by_department, employee_hire_date_distribution

    return app


# Main function to run the app
def main():
    # Sample data - replace with your actual data
    data = {
        'employee_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'first_name': ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sophia', 'Oliver', 'Emma', 'Daniel', 'Olivia'],
        'last_name': ['Doe', 'Smith', 'Wilson', 'Brown', 'Jones', 'Garcia', 'Davis', 'Taylor', 'Miller', 'Rodriguez'],
        'date_of_birth': ['1980-01-01', '1985-02-02', '1990-03-03', '1975-04-04', '1982-05-05', '1988-06-06',
                          '1995-07-07', '1978-08-08', '1984-09-09', '1992-10-10'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'job_title': ['Software Engineer', 'Data Analyst', 'Product Manager', 'Marketing Specialist', 'Sales Manager',
                      'HR Manager', 'Software Engineer', 'Data Analyst', 'Product Manager', 'Marketing Specialist'],
        'department': ['Technology', 'Analytics', 'Product', 'Marketing', 'Sales', 'HR', 'Technology', 'Analytics',
                       'Product', 'Marketing'],
        'salary': [100000, 80000, 120000, 90000, 110000, 75000, 105000, 85000, 125000, 95000],
        'hire_date': ['2020-01-15', '2019-05-10', '2021-08-22', '2018-03-07', '2022-06-14', '2017-09-20',
                      '2020-12-01', '2019-08-18', '2021-04-05', '2018-11-12'],
        'email': ['john.doe@example.com', 'jane.smith@example.com', 'michael.wilson@example.com',
                  'emily.brown@example.com', 'david.jones@example.com', 'sophia.garcia@example.com',
                  'oliver.davis@example.com', 'emma.taylor@example.com', 'daniel.miller@example.com',
                  'olivia.rodriguez@example.com']
    }
    df = pd.DataFrame(data)
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['hire_date'] = pd.to_datetime(df['hire_date'])

    app = create_app(df)
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
