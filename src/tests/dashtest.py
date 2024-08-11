from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_csv("Raw_Sales/sales_data_1.csv")

# Initialize the Dash app
app = Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1(children='Sales Dashboard', style={'textAlign': 'center'}),
    
    dcc.Dropdown(df.country.unique(), 'Portugal', id='dropdown-country', style={'width': '50%', 'margin': 'auto'}),
    
    html.Div([
        dcc.Graph(id='customer-purchase'),
        dcc.Graph(id='product-sales')
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
    
    html.Div([
        dcc.Graph(id='sales-rep-performance'),
        dcc.Graph(id='age-distribution')
    ], style={'display': 'flex', 'justify-content': 'space-around'})
])

# Callback to update Customer Purchase chart
@callback(
    Output('customer-purchase', 'figure'),
    Input('dropdown-country', 'value')
)
def update_customer_purchase(value):
    dff = df[df.country == value]
    return px.bar(dff, x='customer_name', y='purchase_amount', title="Customer Purchase Analysis")

# Callback to update Product Sales chart
@callback(
    Output('product-sales', 'figure'),
    Input('dropdown-country', 'value')
)
def update_product_sales(value):
    dff = df[df.country == value]
    return px.bar(dff, x='product_name', y='purchase_amount', title="Product Sales Analysis")

# Callback to update Sales Representative Performance chart
@callback(
    Output('sales-rep-performance', 'figure'),
    Input('dropdown-country', 'value')
)
def update_sales_rep_performance(value):
    dff = df[df.country == value]
    return px.bar(dff, x='sales_representative', y='purchase_amount', title="Sales Representative Performance")

# Callback to update Age Distribution chart
@callback(
    Output('age-distribution', 'figure'),
    Input('dropdown-country', 'value')
)
def update_age_distribution(value):
    dff = df[df.country == value]
    return px.histogram(dff, x='age', nbins=10, title="Customer Age Distribution")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
