import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
df = pd.read_csv(df_path, parse_dates=['purchase_date'])

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_kpi_card(title, value):
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title"),
            html.H2(value, className="card-text")
        ]),
        className="mb-4"
    )

app.layout = dbc.Container([
    html.H1("Sales Dashboard", className="text-center mb-4"),
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['purchase_date'].min(),
                end_date=df['purchase_date'].max(),
                display_format='YYYY-MM-DD'
            ),
        ], width=6),
        dbc.Col([
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in df['country'].unique()],
                value='All',
                multi=True
            ),
        ], width=6),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            dbc.Button("Reset Filters", id="reset-button", color="secondary", className="mb-3")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(id='kpi-cards', width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='sales-by-country')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='sales-by-product')
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='sales-over-time')
        ], width=12)
    ])
])

@callback(
    [Output('kpi-cards', 'children'),
     Output('sales-by-country', 'figure'),
     Output('sales-by-product', 'figure'),
     Output('sales-over-time', 'figure'),
     Output('date-range', 'start_date'),
     Output('date-range', 'end_date'),
     Output('country-dropdown', 'value')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('country-dropdown', 'value'),
     Input('reset-button', 'n_clicks')]
)
def update_dashboard(start_date, end_date, countries, n_clicks):
    if ctx.triggered_id == 'reset-button':
        start_date = df['purchase_date'].min()
        end_date = df['purchase_date'].max()
        countries = ['All']
    
    filtered_df = df[(df['purchase_date'] >= start_date) & (df['purchase_date'] <= end_date)]
    if 'All' not in countries:
        filtered_df = filtered_df[filtered_df['country'].isin(countries)]

    total_sales = filtered_df['purchase_amount'].sum()
    avg_order_value = filtered_df['purchase_amount'].mean()
    total_customers = filtered_df['customer_id'].nunique()

    kpi_cards = [
        dbc.Col(create_kpi_card("Total Sales", f"${total_sales:,.2f}"), width=4),
        dbc.Col(create_kpi_card("Avg Order Value", f"${avg_order_value:,.2f}"), width=4),
        dbc.Col(create_kpi_card("Total Customers", f"{total_customers:,}"), width=4)
    ]

    sales_by_country = px.bar(filtered_df.groupby('country')['purchase_amount'].sum().reset_index(),
                              x='country', y='purchase_amount', title='Sales by Country')

    sales_by_product = px.pie(filtered_df.groupby('product_name')['purchase_amount'].sum().reset_index(),
                              names='product_name', values='purchase_amount', title='Sales by Product')

    sales_over_time = px.line(filtered_df.groupby('purchase_date')['purchase_amount'].sum().reset_index(),
                              x='purchase_date', y='purchase_amount', title='Sales Over Time')

    return kpi_cards, sales_by_country, sales_by_product, sales_over_time, start_date, end_date, countries

if __name__ == '__main__':
    app.run_server(debug=True)