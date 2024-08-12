# Import necessary libraries
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from datetime import timedelta

# Load data from CSV file
df = pd.read_csv("Raw_Sales/sales_data_1.csv")
df['purchase_date'] = pd.to_datetime(df['purchase_date'])

# Initialize the Dash app
app = Dash(__name__)

# Define color scheme for consistent styling
colors = {
    'background': '#F0F2F6',
    'text': '#2C3E50',
    'primary': '#3498DB',
    'secondary': '#E74C3C',
    'positive': '#27AE60'
}

# Layout of the dashboard
app.layout = html.Div([
    html.Div([
        html.H1('Sales Dashboard', style={'textAlign': 'center', 'color': colors['text'], 'marginBottom': '30px'}),
        
        # Updated filter section with headers
        html.Div([
            html.Div([
                html.Label('Country', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                dcc.Dropdown(
                    id='dropdown-country',
                    options=[{'label': i, 'value': i} for i in df.country.unique()],
                    value='France',
                    style={'width': '300px'}
                )
            ]),
            html.Div([
                html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=df['purchase_date'].min(),
                    end_date=df['purchase_date'].max(),
                    style={'width': '300px'}
                )
            ])
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'margin': '20px auto', 'width': '80%'}),
        
        html.Div(id='kpi-indicators', style={'margin': '50px 0'}),
        
        html.Div([
            html.Div([dcc.Graph(id='customer-purchase')], style={'width': '48%'}),
            html.Div([dcc.Graph(id='product-sales')], style={'width': '48%'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '30px 0'}),
        
        html.Div([
            html.Div([dcc.Graph(id='sales-rep-performance')], style={'width': '48%'}),
            html.Div([dcc.Graph(id='age-distribution')], style={'width': '48%'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '30px 0'}),
    ], style={'padding': '20px', 'backgroundColor': colors['background']})
])

# The callback function remains unchanged
@callback(
    [Output('kpi-indicators', 'children'),
     Output('customer-purchase', 'figure'),
     Output('product-sales', 'figure'),
     Output('sales-rep-performance', 'figure'),
     Output('age-distribution', 'figure')],
    [Input('dropdown-country', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(country, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter the dataframe based on selected country and date range
    dff = df[(df.country == country) & 
             (df.purchase_date >= start_date) & 
             (df.purchase_date <= end_date)]
    
    # Calculate KPI values for the selected period
    total_revenue = dff['purchase_amount'].sum()
    total_customers = dff['customer_id'].nunique()
    average_order_value = dff['purchase_amount'].mean()
    total_orders = dff['purchase_date'].count()
    
    # Calculate KPI values for 6 months ago
    past_start_date = start_date - timedelta(days=180)
    past_end_date = end_date - timedelta(days=180)
    past_dff = df[(df.country == country) & 
                  (df.purchase_date >= past_start_date) & 
                  (df.purchase_date <= past_end_date)]
    
    past_total_revenue = past_dff['purchase_amount'].sum()
    past_total_customers = past_dff['customer_id'].nunique()
    past_average_order_value = past_dff['purchase_amount'].mean()
    past_total_orders = past_dff['purchase_date'].count()
    
    # Calculate changes
    revenue_change = total_revenue - past_total_revenue
    customers_change = total_customers - past_total_customers
    aov_change = average_order_value - past_average_order_value
    orders_change = total_orders - past_total_orders
    
    # Create KPI card style
    kpi_style = {
        'textAlign': 'left',
        'padding': '20px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'margin': '10px',
        'width': '100px'
    }
    
    # Function to create a KPI card
    def create_kpi_card(title, value, change):
        return html.Div([
            html.H3(title, style={'color': colors['text'], 'marginBottom': '5px'}),
            html.Div([
                html.Span(f'{value:,.0f}', style={'fontSize': '36px', 'fontWeight': 'bold', 'color': colors['text']}),
                html.Div([
                    html.Span('▲' if change > 0 else '▼', style={'color': colors['positive'] if change > 0 else colors['secondary'], 'fontSize': '24px'}),
                    html.Span(f'{abs(change):,.0f}', style={'color': colors['positive'] if change > 0 else colors['secondary'], 'fontSize': '24px', 'marginLeft': '5px'})
                ], style={'marginTop': '5px'})
            ])
        ], style=kpi_style)
    
    # Create KPI indicators
    kpi_indicators = html.Div([
        create_kpi_card('Total Revenue', total_revenue, revenue_change),
        create_kpi_card('Total Customers', total_customers, customers_change),
        create_kpi_card('Avg Order Value', average_order_value, aov_change),
        create_kpi_card('Total Orders', total_orders, orders_change)
    ], style={'display': 'flex', 'justifyContent': 'space-between'})
    
    # Create graphs (unchanged from previous version)
    customer_purchase = px.bar(dff, x='customer_name', y='purchase_amount', title="Customer Purchase Analysis",
                               color_discrete_sequence=[colors['primary']])
    customer_purchase.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
    product_sales = px.bar(dff, x='product_name', y='purchase_amount', title="Product Sales Analysis",
                           color_discrete_sequence=[colors['primary']])
    product_sales.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
    sales_rep_performance = px.bar(dff, x='sales_representative', y='purchase_amount', title="Sales Representative Performance",
                                   color_discrete_sequence=[colors['primary']])
    sales_rep_performance.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
    age_distribution = px.histogram(dff, x='age', nbins=10, title="Customer Age Distribution",
                                    color_discrete_sequence=[colors['primary']])
    age_distribution.update_layout(plot_bgcolor='white', paper_bgcolor='grey')
    
    return kpi_indicators, customer_purchase, product_sales, sales_rep_performance, age_distribution    

# Run the app
if __name__ == '__main__':
    app.run(debug=True)