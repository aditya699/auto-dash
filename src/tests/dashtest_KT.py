# Import necessary libraries
import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
def load_data():
    while True:
        try:
            n = os.environ.get('FILE_PATH')
            df = pd.read_csv(n)
            df['purchase_date'] = pd.to_datetime(df['purchase_date'])
            return df
        except FileNotFoundError:
            print("File not found. Please enter a valid file path.")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

def create_app(df):
    # Initialize the Dash app
    app = Dash(__name__)

    # Define color scheme for consistent styling
    colors = {
        'background': '#d9d9d9',
        'text': '#000000',
        'primary': '#3498DB',
        'secondary': '#E74C3C',
        'positive': '#27AE60'
    }

    # Layout of the dashboard
    app.layout = html.Div([
        html.Div([
            html.H1('Sales Dashboard', style={'textAlign': 'center', 'color': colors['text'], 'marginBottom': '30px', 'fontSize': '50px'}),
            
            # Filter section with headers and reset button
            html.Div([
                html.Div([
                    html.Label('Country', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-country',
                        options=[{'label': i, 'value': i} for i in df.country.unique()],
                        value='France',
                        style={'width': '180px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['purchase_date'].min(),
                        end_date=df['purchase_date'].max(),
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Button('Reset Filters', id='reset-button', n_clicks=0, 
                                style={'padding': '10px 20px', 'backgroundColor': colors['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'marginTop': '20px'})
                ])
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-end', 'margin': '10px auto', 'width': '80%'}),
            
            # KPI indicators section
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),
            
            # Charts section
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

    # Callback function for updating the dashboard
    @callback(
        [Output('kpi-indicators', 'children'),
         Output('customer-purchase', 'figure'),
         Output('product-sales', 'figure'),
         Output('sales-rep-performance', 'figure'),
         Output('age-distribution', 'figure')],
        [Input('dropdown-country', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('customer-purchase', 'clickData'),
         Input('product-sales', 'clickData'),
         Input('sales-rep-performance', 'clickData'),
         Input('age-distribution', 'selectedData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(country, start_date, end_date, customer_click, product_click, sales_rep_click, age_selection, reset_clicks):
        # Convert string dates to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filter the dataframe based on selected country and date range
        dff = df[(df.country == country) & 
                 (df.purchase_date >= start_date) & 
                 (df.purchase_date <= end_date)]
        
        # Apply cross-filtering based on chart interactions
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                # Reset all filters
                dff = df[(df.country == country) & 
                         (df.purchase_date >= start_date) & 
                         (df.purchase_date <= end_date)]
            elif input_id == 'customer-purchase' and customer_click:
                customer = customer_click['points'][0]['x']
                dff = dff[dff['customer_name'] == customer]
            elif input_id == 'product-sales' and product_click:
                product = product_click['points'][0]['x']
                dff = dff[dff['product_name'] == product]
            elif input_id == 'sales-rep-performance' and sales_rep_click:
                sales_rep = sales_rep_click['points'][0]['x']
                dff = dff[dff['sales_representative'] == sales_rep]
            elif input_id == 'age-distribution' and age_selection:
                age_range = [age_selection['range']['x'][0], age_selection['range']['x'][1]]
                dff = dff[(dff['age'] >= age_range[0]) & (dff['age'] <= age_range[1])]

        
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
            'width': '150px'
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
        
        # Create graphs with interactivity
        customer_purchase = px.bar(dff, x='customer_name', y='purchase_amount', title="Customer Purchase Analysis",
                                   color_discrete_sequence=[colors['primary']], labels={'customer_name': 'Customer Name', 'purchase_amount': 'Purchase Amount'})
        customer_purchase.update_layout(plot_bgcolor='white', paper_bgcolor='white', clickmode='event+select')
        
        product_sales = px.bar(dff, x='product_name', y='purchase_amount', title="Product Sales Analysis",
                               color_discrete_sequence=[colors['primary']],labels={'product_name':'Product Name','purchase_amount':'Purchase amount'})
        product_sales.update_layout(plot_bgcolor='white', paper_bgcolor='white', clickmode='event+select')
        
        sales_rep_performance = px.bar(dff, x='sales_representative', y='purchase_amount', title="Sales Representative Performance",
                                       color_discrete_sequence=[colors['primary']],labels={'sales_representative':'Sales Representative','purchase_amount':'Purchase Amount'})
        sales_rep_performance.update_layout(plot_bgcolor='white', paper_bgcolor='white', clickmode='event+select')
        
        age_distribution = px.histogram(dff, x='age', nbins=10, title="Customer Age Distribution",
                                        color_discrete_sequence=[colors['primary']],labels={'age':'Age'})
        age_distribution.update_layout(plot_bgcolor='white', paper_bgcolor='white', selectdirection='h')
        
        return kpi_indicators, customer_purchase, product_sales, sales_rep_performance, age_distribution    

    return app

def main():
    df = load_data()
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()