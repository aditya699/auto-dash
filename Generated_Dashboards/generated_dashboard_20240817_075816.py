
import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

def create_app(df):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    colors = {
        'background': '#F7F7F7',
        'text': '#333333',
        'primary': '#3498DB',
        'secondary': '#2ECC71',
        'accent': '#F39C12',
        'negative': '#E74C3C'
    }

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
            
            html.Div([
                html.Div([
                    html.Label('Department', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-department',
                        options=[{'label': i, 'value': i} for i in df.department.unique()],
                        value=['Sales', 'Marketing'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Job Title', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-job-title',
                        options=[{'label': i, 'value': i} for i in df.job_title.unique()],
                        value=['Manager', 'Analyst'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Gender', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-gender',
                        options=[{'label': i, 'value': i} for i in df.gender.unique()],
                        value=['Male', 'Female'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Button('Reset Filters', id='reset-button', n_clicks=0, 
                                style={'padding': '10px 20px', 'backgroundColor': colors['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'all 0.3s ease'})
                ])
            ], style=filter_style),
            
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='employee-salary')], width=6),
                dbc.Col([dcc.Graph(id='employee-age')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='employee-tenure')], width=6),
                dbc.Col([dcc.Graph(id='employee-gender')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('employee-salary', 'figure'),
         Output('employee-age', 'figure'),
         Output('employee-tenure', 'figure'),
         Output('employee-gender', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('dropdown-job-title', 'value'),
         Input('dropdown-gender', 'value'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(departments, job_titles, genders, reset_clicks):
        dff = df[df.department.isin(departments) & 
                 df.job_title.isin(job_titles) & 
                 df.gender.isin(genders)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df
        
        total_employees = dff.shape[0]
        average_salary = dff.salary.mean()
        average_age = dff.date_of_birth.apply(lambda x: (datetime.now() - x).days // 365).mean()
        average_tenure = (datetime.now() - dff.hire_date.mean()).days // 365
        
        kpi_indicators = html.Div([
            create_kpi_card('Total Employees', total_employees, 0),
            create_kpi_card('Average Salary', average_salary, 0),
            create_kpi_card('Average Age', average_age, 0),
            create_kpi_card('Average Tenure', average_tenure, 0)
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
        
        employee_salary = px.histogram(dff, x='salary', nbins=10, title="Employee Salary Distribution",
                                      color_discrete_sequence=[colors['primary']], labels={'salary':'Salary'})
        employee_salary = update_chart_layout(employee_salary)
        
        employee_age = px.histogram(dff, x='date_of_birth', nbins=10, title="Employee Age Distribution",
                                   color_discrete_sequence=[colors['primary']], labels={'date_of_birth':'Date of Birth'})
        employee_age = update_chart_layout(employee_age)
        
        employee_tenure = px.histogram(dff, x='hire_date', nbins=10, title="Employee Tenure Distribution",
                                      color_discrete_sequence=[colors['primary']], labels={'hire_date':'Hire Date'})
        employee_tenure = update_chart_layout(employee_tenure)
        
        employee_gender = px.pie(dff, names='gender', title="Employee Gender Distribution",
                                color_discrete_sequence=[colors['primary'], colors['secondary']])
        employee_gender = update_chart_layout(employee_gender)
        
        return kpi_indicators, employee_salary, employee_age, employee_tenure, employee_gender

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
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()
