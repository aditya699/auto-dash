import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
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
                        value=[df.department.unique()[0]],
                        multi=True,
                        style={'width': '300px'}
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
            
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='salary-distribution')], width=6),
                dbc.Col([dcc.Graph(id='department-breakdown')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='age-distribution')], width=6),
                dbc.Col([dcc.Graph(id='gender-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('salary-distribution', 'figure'),
         Output('department-breakdown', 'figure'),
         Output('age-distribution', 'figure'),
         Output('gender-distribution', 'figure')],
        [Input('dropdown-department', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('salary-distribution', 'selectedData'),
         Input('department-breakdown', 'clickData'),
         Input('age-distribution', 'selectedData'),
         Input('gender-distribution', 'clickData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(departments, start_date, end_date, salary_selection, department_click, age_selection, gender_click, reset_clicks):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        dff = df[df.department.isin(departments) & 
                 (df.hire_date >= start_date) & 
                 (df.hire_date <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[df.department.isin(departments) & 
                         (df.hire_date >= start_date) & 
                         (df.hire_date <= end_date)]
            elif input_id == 'salary-distribution' and salary_selection:
                salary_range = [salary_selection['range']['x'][0], salary_selection['range']['x'][1]]
                dff = dff[(dff['salary'] >= salary_range[0]) & (dff['salary'] <= salary_range[1])]
            elif input_id == 'department-breakdown' and department_click:
                department = department_click['points'][0]['x']
                dff = dff[dff['department'] == department]
            elif input_id == 'age-distribution' and age_selection:
                age_range = [age_selection['range']['x'][0], age_selection['range']['x'][1]]
                dff = dff[(dff['date_of_birth'].dt.year <= (datetime.now().year - age_range[0])) & 
                          (dff['date_of_birth'].dt.year >= (datetime.now().year - age_range[1]))]
            elif input_id == 'gender-distribution' and gender_click:
                gender = gender_click['points'][0]['x']
                dff = dff[dff['gender'] == gender]

        total_employees = len(dff)
        avg_salary = dff['salary'].mean()
        avg_age = (datetime.now() - dff['date_of_birth']).mean().days / 365.25
        gender_ratio = dff['gender'].value_counts(normalize=True).get('Female', 0) * 100

        def create_kpi_card(title, value, format_str):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(format_str.format(value), style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']})
                ])
            ], style=kpi_style)
        
        kpi_indicators = html.Div([
            create_kpi_card('Total Employees', total_employees, '{:,.0f}'),
            create_kpi_card('Average Salary', avg_salary, '${:,.2f}'),
            create_kpi_card('Average Age', avg_age, '{:.1f}'),
            create_kpi_card('Female Ratio', gender_ratio, '{:.1f}%')
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
        
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
        
        salary_distribution = px.histogram(dff, x='salary', nbins=20, title="Salary Distribution",
                                           color_discrete_sequence=[colors['primary']], labels={'salary':'Salary'})
        salary_distribution = update_chart_layout(salary_distribution)
        
        department_breakdown = px.bar(dff.groupby('department').size().reset_index(name='count'), 
                                      x='department', y='count', title="Department Breakdown",
                                      color_discrete_sequence=[colors['primary']], labels={'department':'Department', 'count':'Employee Count'})
        department_breakdown = update_chart_layout(department_breakdown)
        
        age_distribution = px.histogram(dff, x=(datetime.now() - dff['date_of_birth']).astype('<m8[Y]'), 
                                        nbins=20, title="Age Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'x':'Age'})
        age_distribution = update_chart_layout(age_distribution)
        
        gender_distribution = px.pie(dff, names='gender', title="Gender Distribution",
                                     color_discrete_sequence=[colors['primary'], colors['secondary']])
        gender_distribution = update_chart_layout(gender_distribution)
        
        return kpi_indicators, salary_distribution, department_breakdown, age_distribution, gender_distribution

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()