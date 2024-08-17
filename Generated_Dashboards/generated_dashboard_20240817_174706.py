import os
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['age'] = (datetime.now() - df['date_of_birth']).astype('<m8[Y]').astype(int)
    df['tenure'] = (datetime.now() - df['hire_date']).astype('<m8[Y]').astype(int)

    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    colors = {
        'background': '#F7F7F7',
        'text': '#333333',
        'primary': '#3498DB',
        'secondary': '#2ECC71',
        'accent': '#F39C12',
        'negative': '#E74C3C'
    }

    app.layout = dbc.Container([
        html.H1('Employee Dashboard', className='mb-4'),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='department-filter',
                    options=[{'label': 'All Departments', 'value': 'All'}] + [{'label': dept, 'value': dept} for dept in df['department'].unique()],
                    value='All',
                    multi=True
                ),
            ], width=4),
            dbc.Col([
                dcc.Dropdown(
                    id='gender-filter',
                    options=[{'label': 'All Genders', 'value': 'All'}] + [{'label': gender, 'value': gender} for gender in df['gender'].unique()],
                    value='All',
                    multi=True
                ),
            ], width=4),
            dbc.Col([
                html.Button('Reset Filters', id='reset-button', className='btn btn-primary')
            ], width=4),
        ], className='mb-4'),

        html.Div(id='kpi-cards', className='mb-4'),

        dbc.Row([
            dbc.Col([dcc.Graph(id='salary-distribution')], width=6),
            dbc.Col([dcc.Graph(id='age-distribution')], width=6)
        ], className='mb-4'),

        dbc.Row([
            dbc.Col([dcc.Graph(id='department-breakdown')], width=6),
            dbc.Col([dcc.Graph(id='tenure-vs-salary')], width=6)
        ])
    ])

    @callback(
        [Output('kpi-cards', 'children'),
         Output('salary-distribution', 'figure'),
         Output('age-distribution', 'figure'),
         Output('department-breakdown', 'figure'),
         Output('tenure-vs-salary', 'figure')],
        [Input('department-filter', 'value'),
         Input('gender-filter', 'value'),
         Input('reset-button', 'n_clicks'),
         Input('salary-distribution', 'selectedData'),
         Input('age-distribution', 'selectedData'),
         Input('department-breakdown', 'clickData'),
         Input('tenure-vs-salary', 'selectedData')]
    )
    def update_dashboard(departments, genders, n_clicks, salary_data, age_data, dept_data, tenure_data):
        filtered_df = df.copy()

        if 'All' not in departments:
            filtered_df = filtered_df[filtered_df['department'].isin(departments)]
        if 'All' not in genders:
            filtered_df = filtered_df[filtered_df['gender'].isin(genders)]

        if ctx.triggered_id == 'reset-button':
            return dash.no_update

        kpi_cards = [
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Employees", className="card-title"),
                    html.P(f"{len(filtered_df)}", className="card-text")
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Salary", className="card-title"),
                    html.P(f"${filtered_df['salary'].mean():,.2f}", className="card-text")
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Age", className="card-title"),
                    html.P(f"{filtered_df['age'].mean():.1f} years", className="card-text")
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Tenure", className="card-title"),
                    html.P(f"{filtered_df['tenure'].mean():.1f} years", className="card-text")
                ])
            ])
        ]

        salary_fig = px.histogram(filtered_df, x='salary', title='Salary Distribution')
        age_fig = px.histogram(filtered_df, x='age', title='Age Distribution')
        dept_fig = px.pie(filtered_df, names='department', title='Department Breakdown')
        tenure_fig = px.scatter(filtered_df, x='tenure', y='salary', color='department', title='Tenure vs Salary')

        return kpi_cards, salary_fig, age_fig, dept_fig, tenure_fig

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()