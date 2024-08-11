from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

# Load data
df = pd.read_csv("Raw_Sales/sales_data_1.csv")
df['purchase_date'] = pd.to_datetime(df['purchase_date'])

# Initialize the Dash app
app = Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1(children='Sales Dashboard', style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Dropdown(df.country.unique(), 'Portugal', id='dropdown-country', style={'width': '48%'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['purchase_date'].min(),
            end_date=df['purchase_date'].max(),
            style={'width': '48%'}
        ),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '20px auto', 'width': '80%'}),
    
    html.Div([
        dcc.Graph(id='kpi-indicators', style={'height': '200px'}),
    ]),
    
    html.Div([
        dcc.Graph(id='customer-purchase'),
        dcc.Graph(id='product-sales')
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
    
    html.Div([
        dcc.Graph(id='sales-rep-performance'),
        dcc.Graph(id='age-distribution')
    ], style={'display': 'flex', 'justify-content': 'space-around'})
])

@callback(
    [Output('kpi-indicators', 'figure'),
     Output('customer-purchase', 'figure'),
     Output('product-sales', 'figure'),
     Output('sales-rep-performance', 'figure'),
     Output('age-distribution', 'figure')],
    [Input('dropdown-country', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(country, start_date, end_date):
    dff = df[(df.country == country) & 
             (df.purchase_date >= start_date) & 
             (df.purchase_date <= end_date)]
    
    total_revenue = dff['purchase_amount'].sum()
    total_customers = dff['customer_id'].nunique()
    average_order_value = dff['purchase_amount'].mean()
    total_orders = dff['purchase_date'].count()
    
    # Create KPI indicators
    kpi_fig = go.Figure()
    kpi_fig.add_trace(go.Indicator(
        mode = "number",
        value = total_revenue,
        title = {"text": "Total Revenue"},
        domain = {'row': 0, 'column': 0},
        number = {'prefix': "$"}
    ))
    kpi_fig.add_trace(go.Indicator(
        mode = "number",
        value = total_customers,
        title = {"text": "Total Customers"},
        domain = {'row': 0, 'column': 1}
    ))
    kpi_fig.add_trace(go.Indicator(
        mode = "number",
        value = average_order_value,
        title = {"text": "Avg Order Value"},
        domain = {'row': 0, 'column': 2},
        number = {'prefix': "$"}
    ))
    kpi_fig.add_trace(go.Indicator(
        mode = "number",
        value = total_orders,
        title = {"text": "Total Orders"},
        domain = {'row': 0, 'column': 3}
    ))
    kpi_fig.update_layout(
        grid = {'rows': 1, 'columns': 4, 'pattern': "independent"},
        margin = {'l':40, 'r':40, 't':40, 'b':40}
    )
    
    customer_purchase = px.bar(dff, x='customer_name', y='purchase_amount', title="Customer Purchase Analysis")
    product_sales = px.bar(dff, x='product_name', y='purchase_amount', title="Product Sales Analysis")
    sales_rep_performance = px.bar(dff, x='sales_representative', y='purchase_amount', title="Sales Representative Performance")
    age_distribution = px.histogram(dff, x='age', nbins=10, title="Customer Age Distribution")
    
    return kpi_fig, customer_purchase, product_sales, sales_rep_performance, age_distribution

# Run the app
if __name__ == '__main__':
    app.run(debug=True)